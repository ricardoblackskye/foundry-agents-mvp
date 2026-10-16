# Foundry Agents MVP

Hosted AI Agent scaffolded for Microsoft Azure AI Foundry using the Azure Developer CLI (`azd`) and the `microsoft.foundry` extensions.

## Architecture
- **Protocol**: `responses` protocol
- **Port**: `8088`
- **Health Probe**: `GET /readiness`
- **Deploy Mode**: Code deployment (ZIP package)

## Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Azure Developer CLI (`azd` >= 1.25.2, installed `1.36.0`)
- Foundry Extension bundle: `microsoft.foundry` (installed `1.0.0-beta.2`)

## Local Setup & Development

1. **Create and activate virtual environment**:
   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements-dev.txt
   ```

2. **Run tests**:
   ```powershell
   pytest tests/ -v
   ```

3. **Run agent locally**:
   ```powershell
   python src/agent/main.py
   ```

4. **Verify health probe**:
   ```powershell
   curl http://localhost:8088/readiness
   ```

5. **Inspect locally with Foundry UI**:
   ```powershell
   azd ai inspector
   ```

## Azure Deployment
When you are ready to deploy to your Azure Foundry project:
1. Log in to Azure:
   ```powershell
   azd auth login
   ```
2. Set your Foundry project context:
   ```powershell
   azd ai project set --project-id <your-foundry-resource-id>
   ```
3. Deploy the hosted agent:
   ```powershell
   azd deploy
   ```
