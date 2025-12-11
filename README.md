# 🚀 Bedrock AgentCore Minimal Agent

This repository provides a **minimal reference implementation** of an **Amazon Bedrock AgentCore**–based agent, packaged as a Docker container and deployed using **AWS CDK**.  
It demonstrates how to run a fully custom agent runtime while leveraging Bedrock’s managed memory store, model invocation, and runtime orchestration.

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

| Component | Description |
|----------|-------------|
| **Bedrock Agent Runtime** | Managed service that hosts and executes your custom agent image. |
| **Custom Agent Container** | Python application that implements the AgentCore runtime server using `bedrock_agentcore`. |
| **Memory Store** | Persistent long-term and short-term conversation memory via `AgentCoreMemoryStore` and `AgentCoreMemorySaver`. |
| **Foundation Model** | Amazon **Nova 2 Lite**, accessed via `bedrock_converse`. |
| **Agent Logic** | LangChain agent created with `create_agent()`, supporting memory-backed reasoning. |
| **AWS CDK** | Provisions memory, builds and pushes the Docker image, deploys the Agent Runtime, configures model access. |

---

## 🧠 Memory Model

### Short-Term Memory
- Scoped to a single conversation thread  
- Used for conversational continuity  
- Implemented using **AgentCoreMemorySaver**

### Long-Term Memory
- Persists across all conversations  
- Used for storing facts or knowledge learned over time  
- Implemented using **AgentCoreMemoryStore**

Both memory layers use the same Bedrock Memory resource created by the CDK stack.

---

## 🛠️ Technologies Used

### AWS Services
- **Amazon Bedrock AgentCore** – runtime orchestration and memory integration  
- **Amazon Bedrock Converse** – LLM interface for Nova 2 Lite  
- **Amazon ECR** – stores the built agent Docker image  
- **AWS CDK (Python)** – infrastructure definition and automated deployment  

### Python Libraries
- `bedrock-agentcore` – server runtime for AgentCore  
- `langchain` – agent orchestration and message handling  
- `langgraph-checkpoint-aws` – memory persistence via Bedrock Memory  
- `bedrock-converse` – Bedrock model wrapper for LangChain  

---

## 🧩 Capabilities

- Conversational reasoning powered by **Nova 2 Lite**  
- Integrated **short- and long-term memory** for context persistence  
- **Session and user identity propagation** via request headers  
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

### Supported Headers

| Header | Description |
|--------|-------------|
| `X-Amzn-Bedrock-AgentCore-Runtime-Custom-User` | Identifies the caller |
| `X-Amzn-Bedrock-AgentCore-Runtime-Custom-Session` | Specifies the session/thread ID |

### Example Payload

```json
{
  "prompt": "Hello, who are you?"
}
```

## Summary
This project illustrates how to:

- Deploy a custom containerized Bedrock AgentCore application
- Integrate Nova 2 Lite with LangChain
- Persist memory using Bedrock’s built-in infrastructure
- Build cloud-ready agents with minimal infrastructure overhead
- It serves as a clean foundation for production AI agents on Amazon Bedrock, ready for extension with tools, workflows, and domain-specific logic.