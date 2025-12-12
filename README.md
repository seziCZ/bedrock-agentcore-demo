# 🚀 Bedrock AgentCore Minimal Agent

This repository provides a **minimal reference implementation** of an **Amazon Bedrock AgentCore**–based agent, packaged as a Docker container and deployed using **AWS CDK**.  
It demonstrates how to run a fully custom agent runtime while leveraging Bedrock’s managed memory store, model invocation, and an integrated web search capability.

---

## 🧱 Architecture Overview

Below is a high-level ASCII architecture diagram describing how all components interact:

          ┌──────────────────────────────┐
          │        Client / Caller        │
          │  (sends prompt + headers)     │
          └───────────────┬──────────────┘
                          │ Invoke
                          ▼
            ┌──────────────────────────┐
            │   Bedrock Agent Runtime  │
            │  (managed execution env) │
            └───────────────┬──────────┘
                            │ HTTP call
                            ▼
             ┌───────────────────────────┐
             │   Custom Agent Container  │
             │  (Python + LangChain App) │
             ├───────────────────────────┤
             │ - Reads/Writes Memory     │
             │ - Invokes Bedrock Model   │
             │ - Uses user/session ctx   │
             └───────────┬──────────────┘
                         │
                         ▼
         ┌────────────────────────────────┐
         │       Bedrock Memory Store      │
         │  (short-term + long-term state) │
         └────────────────────────────────┘

                         │
                         ▼
            ┌───────────────────────────┐
            │ Bedrock Foundation Model  │
            │     (Nova 2 Lite)         │
            └───────────────────────────┘

---

### Core Components

| Component                          | Description                                                                           |
| ---------------------------------- | ------------------------------------------------------------------------------------- |
| **Bedrock Agent Runtime**          | Fully managed service that executes your custom agent container.                      |
| **Custom Agent Runtime Container** | Python application using LangChain + Bedrock AgentCore server.                        |
| **Memory Store**                   | Persistent memory (short-term + long-term) backed by Bedrock Memory.                  |
| **Nova Model**                     | Amazon Nova model invoked via Bedrock Converse (`model_provider='bedrock_converse'`). |
| **LangChain Agent**                | Orchestrates reasoning, memory usage, and tool calls.                                 |
| **Search Tool**                    | DuckDuckGo-based web search for current event reasoning.                              |
| **AWS CDK Stack**                  | Builds Docker image, deploys Agent Runtime, configures IAM + Memory.                  |

---

## 🧠 Memory Model

### Short-Term Memory
- Scoped to a single conversation thread  
- Used for conversational continuity  
- Implemented using **langgraph_checkpoint_aws.AgentCoreMemorySaver**

### Long-Term Memory
- Persists across all conversations  
- Used for storing facts or knowledge learned over time  
- Implemented using **langgraph_checkpoint_aws.AgentCoreMemoryStore**

Both memory layers use the same Bedrock Memory resource created by the CDK stack.

---

## 🛠️ Technologies Used

### AWS Services
- **Amazon Bedrock AgentCore** – runtime orchestration and memory integration  
- **Amazon Bedrock Converse** – LLM interface for Nova 2 Lite  
- **Amazon ECR** – stores the built agent Docker image  
- **AWS CDK (Python)** – infrastructure definition and automated deployment  

### Python Libraries
- `bedrock-converse` – Bedrock model wrapper for LangChain
- `bedrock-agentcore` – server runtime for AgentCore  
- `langchain` – agent orchestration and message handling  
- `langchain-aws` - interface for Bedrock Converse models  
- `langchain-community` - community managed Tools, including DuckDuckGo search
- `langgraph-checkpoint-aws` – integrates memory with Bedrock AgentCore

---

## 🧩 Capabilities

- Docker-based deployment with **AWS-managed execution**
- Conversational reasoning powered by **Nova 2 Lite**  
- Integrated **short- and long-term memory** for context persistence  
- DuckDuckGo search for **current-event reasoning**
- Fully customizable logic using LangChain tools or workflows  
- Modular design suited for extension (RAG, APIs, LangGraph workflows, etc.)

This repository provides a minimal baseline intended for extension with more advanced agent behaviors.

---

## 🚢 Deployment Model (CDK)

The AWS CDK stack:

1. Creates a Bedrock Memory store  
2. Builds and uploads the Docker agent image to Amazon ECR  
3. Deploys a Bedrock Agent Runtime referencing that image  
4. Grants permissions for memory read/write and model invocation  
5. Outputs the **Agent Runtime ARN** for external invocation

---

## 📬 Invocation

Use the **Runtime ARN** emitted by CDK to invoke the agent.

### Example Payload

```json
{
  "input": "What's the weather like in Tokyo today?",
  "user_id": "12345",
  "session_id": "3456789"
}
```

## Summary
This project illustrates how to:

- Running a custom containerized Bedrock Agent
- Integrating Nova models with LangChain
- Persisting memory with Bedrock AgentCore Memory
- Extending agents with real-world tools and logic
- Deploying production-ready agent runtimes using AWS CDK