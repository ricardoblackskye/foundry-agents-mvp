# Azure AI Foundry Hosted Agent Scaffolding Design

## Objective
Scaffold a hosted agent project targeting Microsoft Azure AI Foundry using the Azure Developer CLI (`azd`) and the `microsoft.foundry` extension, following the official Microsoft Foundry hosted agent architecture and runtime contract.

## Context & Constraints
- **Target Platform**: Microsoft Azure AI Foundry (Hosted Agents).
- **Language**: Python 3.10+ (local runtime Python 3.14 available).
- **Deployment Mode**: Code deployment (packaged as ZIP package, avoiding local Docker requirement).
- **Protocol**: `responses` protocol (standard streaming / turn-based conversational agent interface).
- **Cloud Resources**: Local project scaffolding first; authentication (`azd auth login`) and Azure resource connection (`azd ai project set` / `azd deploy`) executed when the user is ready.

## Architecture & Directory Layout
The repository root contains a unified `azure.yaml` manifest that manages both `azd` environment settings and hosted agent runtime metadata:

```
foundry-agents-mvp/
├── .gitignore                   # Standard Python & azd ignores (.venv, .azure, __pycache__)
├── azure.yaml                   # Unified azd project manifest & hosted agent definition
├── requirements.txt             # Agent dependencies (FastAPI/uvicorn or Foundry SDK dependencies)
├── src/
│   └── agent/
│       ├── __init__.py
│       └── main.py              # Hosted agent entrypoint implementing runtime contract
└── docs/
    └── superpowers/
        └── specs/
            └── 2026-10-16-foundry-agent-scaffold-design.md
```

### Manifest Definition (`azure.yaml`)
The project manifest defines the agent service and protocol:
```yaml
name: foundry-agents-mvp
metadata:
  template: azure.ai.agents/python-responses-basic
services:
  agent:
    project: ./src/agent
    language: python
    host: ai.agent
    config:
      protocol: responses
```

## Runtime Contract & Protocol Specification
The hosted agent adheres strictly to the Microsoft Azure AI Foundry hosted agent runtime contract:

1. **Network Listener**: Listens on TCP port `8088` (default Foundry hosted agent port).
2. **Readiness Probe**:
   - Route: `GET /readiness`
   - Response: HTTP 200 with status payload (e.g. `{"status": "ready"}`).
3. **Conversational Endpoint**:
   - Handles the `responses` protocol for inbound chat messages and replies with formatted agent turn responses.
4. **Resilience & Error Handling**:
   - Handles malformed message turns gracefully with informative HTTP 400 responses.
   - Logs diagnostics to standard output for capture by local CLI and Azure Monitor.

## Prerequisites & Tooling Setup
1. **Azure Developer CLI (`azd`)**:
   - Install via Windows Package Manager: `winget install Microsoft.Azd --accept-source-agreements --accept-package-agreements`
   - Verify `azd version` (minimum v1.25.2 required).
2. **Foundry CLI Extension Bundle**:
   - Install meta-package: `azd ext install microsoft.foundry`
   - Extensions provided:
     - `azure.ai.agents`: Agent scaffolding, packaging, and deployment (`azd ai agent`).
     - `azure.ai.inspector`: Local visual testing and chat web interface (`azd ai inspector`).
     - `azure.ai.projects`: Project context binding (`azd ai project`).
     - `azure.ai.connections`, `azure.ai.skills`, `azure.ai.routines`, `azure.ai.toolboxes`.
3. **Local Python Environment**:
   - Create local virtual environment: `py -m venv .venv`
   - Activate environment and install dependencies: `.venv\Scripts\pip install -r requirements.txt`.

## Verification & Testing
1. **Health Probe Verification**:
   - Run the agent locally: `.venv\Scripts\python src/agent/main.py`.
   - Send health probe: `curl -i http://localhost:8088/readiness`.
   - Verify HTTP 200 status code returned.
2. **Interactive Local Inspection**:
   - Launch inspector: `azd ai inspector`.
   - Inspect local execution logs and test conversational turn handling.
3. **Git Version Control**:
   - Ensure clean `.gitignore` for `.azure/`, `.venv/`, and temporary bytecode.
   - Commit initial scaffold with clear descriptive commit message.

## Future Cloud Connection & Deployment
When connecting to Azure cloud resources:
1. Authenticate session: `azd auth login`
2. Link project context: `azd ai project set --project-id <foundry-project-resource-id>`
3. Deploy agent: `azd deploy`
