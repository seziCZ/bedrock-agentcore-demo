import os
from typing import Dict, Any

from bedrock_agentcore import BedrockAgentCoreApp, RequestContext
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langgraph_checkpoint_aws import AgentCoreMemoryStore, AgentCoreMemorySaver

# define constants
USER_HEADER = "X-Amzn-Bedrock-AgentCore-Runtime-Custom-User"
SESSION_HEADER = "X-Amzn-Bedrock-AgentCore-Runtime-Custom-Session"

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

# initialize agent
agent = create_agent(
    model=model,
    checkpointer=short_term_memory,
    store=long_term_memory
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
        Typically includes user input fields required for agent execution.
    :param context: Runtime context provided by Bedrock AgentCore, including session
        metadata, request identifiers, and request-scoped headers.
    :return: Dict representing the result to send back to the caller. Expected to
        contain serialized results produced by the agent or application logic.
    """

    # reconstruct parameters
    prompt = payload.get("prompt", "The user did not supply any input or instructions.")
    actor_id = context.request_headers[USER_HEADER] if context.request_headers else "anonymous"
    session_id = context.request_headers[SESSION_HEADER] if context.request_headers else context.session_id

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
