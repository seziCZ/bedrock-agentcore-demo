import os
from typing import Dict, Any

from bedrock_agentcore import BedrockAgentCoreApp, RequestContext
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.tools import Tool
from langgraph_checkpoint_aws import AgentCoreMemoryStore, AgentCoreMemorySaver

# initialize model
model = init_chat_model(
    model=os.environ.get("MODEL_ID"),
    model_provider='bedrock_converse'
)

# short term (single conversation) memory
short_term_memory = AgentCoreMemorySaver(
    memory_id=os.environ.get("MEMORY_ID")
)

# long term (multiple conversations) memory
long_term_memory = AgentCoreMemoryStore(
    memory_id=os.environ.get("MEMORY_ID")
)

# allow for reasoning about current events
duck_duck_go = DuckDuckGoSearchResults()
duck_duck_go_search = Tool(
    name="web_search",
    func=lambda query: duck_duck_go.run(query),
    description=(
        "Search the web using DuckDuckGo and return recent, relevant results. "
        "Use this for up-to-date information and reasoning about current events."
    ),
)

# initialize agent
agent = create_agent(
    model=model,
    checkpointer=short_term_memory,
    store=long_term_memory,
    tools=[duck_duck_go_search],
    debug=True
)

app = BedrockAgentCoreApp()

@app.entrypoint
def handler(
    payload: Dict[str, Any],
    context: RequestContext,
) -> Dict[str, Any]:
    """
    Entrypoint handler for processing Bedrock AgentCore runtime requests.
    :param payload: Dictionary containing the inbound request body supplied by the caller.
    :param context: Runtime context provided by Bedrock AgentCore.
    :return: Dict representing the result to send back to the caller. Expected to
        contain serialized results produced by the agent or application logic.
    """

    # reconstruct parameters
    actor_id = payload.get("user_id", "anonymous")
    session_id = payload.get("session_id", context.session_id)
    prompt = payload.get("input", "No user input provided.")

    # invoke agent
    result = agent.invoke(
        input={  # type: ignore[arg-type]
            "messages": [("human", prompt)]
        },
        config={  # type: ignore[arg-type]
            "configurable": {
                "actor_id": actor_id,
                "thread_id": session_id
            }
        }
    )

    return {
        "result": result["messages"][-1].content
    }


if __name__ == "__main__":
    """
    Starts the Bedrock AgentCore runtime server.
    This bootstraps the AgentCore application and launches the underlying
    HTTP server so that the runtime can receive and process incoming
    invocation requests from the Bedrock Agent Runtime service.
    """
    app.run()
