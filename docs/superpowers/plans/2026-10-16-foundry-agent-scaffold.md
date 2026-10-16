# Azure AI Foundry Hosted Agent Scaffolding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Install the Azure Developer CLI (`azd`) with Foundry extensions, scaffold a Python hosted agent adhering to the Microsoft Foundry runtime contract (`responses` protocol, port 8088, `/readiness`), and verify local execution with unit and integration tests.

**Architecture:** A root `azure.yaml` project manifest defines the agent service configuration. Under `src/agent/`, a Python service implements the health probe and responses protocol using an asynchronous web engine (FastAPI + Uvicorn) packaged for code deployment.

**Tech Stack:** Python 3.14 (`py`), FastAPI, Uvicorn, Pytest, HTTPX, Azure Developer CLI (`azd`), Foundry CLI extension (`microsoft.foundry`).

## Global Constraints
- Target platform: Microsoft Azure AI Foundry hosted agent runtime
- Language: Python 3.10+
- Host type: `ai.agent`
- Protocol: `responses`
- Port: 8088
- Readiness probe path: `GET /readiness` returning HTTP 200 with `{"status": "ready"}`
- Deployment mode: Code deployment (ZIP archive, no Docker required)
- No interactive prompts during automated steps

---

### Task 1: Tooling Installation & Verification (`azd` & `microsoft.foundry` extension)

**Files:**
- Create: none (system CLI installation)
- Verify: system PATH and extensions

**Interfaces:**
- Consumes: Windows package manager (`winget`) or PowerShell installer
- Produces: `azd` CLI available in terminal PATH; `microsoft.foundry` extension bundle installed

- [ ] **Step 1: Check existing azd or install Azure Developer CLI via winget**

Run in PowerShell:
```powershell
winget install Microsoft.Azd --accept-source-agreements --accept-package-agreements
```
If winget requires a shell PATH refresh, verify by querying the default installation path:
```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
azd version
```
Expected output: `azd version 1.25.2` or later.

- [ ] **Step 2: Install Microsoft Foundry extension bundle**

Run:
```powershell
azd ext install microsoft.foundry
```
Expected output: Installed `microsoft.foundry` and associated extensions (`azure.ai.agents`, `azure.ai.inspector`, `azure.ai.projects`, etc.).

- [ ] **Step 3: Verify extension installation**

Run:
```powershell
azd ext list
azd ai agent version
```
Expected output: `microsoft.foundry` listed and version information for `azure.ai.agents` printed.

- [ ] **Step 4: Commit task notes if needed**

Run:
```bash
git status
```
Expected: Clean working tree or ready for Task 2.

---

### Task 2: Project Manifest, Dependencies, and Virtual Environment

**Files:**
- Create: `.gitignore`
- Create: `azure.yaml`
- Create: `requirements.txt`
- Create: `requirements-dev.txt`

**Interfaces:**
- Consumes: Python runtime (`py`)
- Produces: `.venv` virtual environment with dependencies; valid `azure.yaml` manifest

- [ ] **Step 1: Create `.gitignore`**

Create `c:\Dev\Foundry\foundry-agents-mvp\.gitignore`:
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
ENV/

# Azure & azd
.azure/

# IDE & Testing
.pytest_cache/
.coverage
htmlcov/
.vscode/
.idea/
```

- [ ] **Step 2: Create `azure.yaml` project manifest**

Create `c:\Dev\Foundry\foundry-agents-mvp\azure.yaml`:
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

- [ ] **Step 3: Create dependency files**

Create `c:\Dev\Foundry\foundry-agents-mvp\requirements.txt`:
```
fastapi>=0.115.0,<1.0.0
uvicorn[standard]>=0.32.0,<1.0.0
pydantic>=2.9.0,<3.0.0
```

Create `c:\Dev\Foundry\foundry-agents-mvp\requirements-dev.txt`:
```
-r requirements.txt
pytest>=8.3.0
httpx>=0.28.0
pytest-asyncio>=0.24.0
```

- [ ] **Step 4: Create virtual environment and install dependencies**

Run in PowerShell:
```powershell
py -m venv .venv
.venv\Scripts\pip install --upgrade pip
.venv\Scripts\pip install -r requirements-dev.txt
```
Expected: Virtual environment created at `.venv/` and packages installed cleanly.

- [ ] **Step 5: Commit manifest and dependencies**

Run:
```bash
git add .gitignore azure.yaml requirements.txt requirements-dev.txt
git commit -m "chore: scaffold azure.yaml manifest and project dependencies"
```
Expected: Clean git commit with 4 files committed.

---

### Task 3: Hosted Agent Service Implementation (TDD)

**Files:**
- Create: `src/agent/__init__.py`
- Create: `src/agent/main.py`
- Create: `tests/__init__.py`
- Create: `tests/test_agent.py`

**Interfaces:**
- Consumes: FastAPI, Uvicorn
- Produces: `app` FastAPI instance with `GET /readiness` and `POST /responses` endpoints

- [ ] **Step 1: Write failing unit & contract tests**

Create `c:\Dev\Foundry\foundry-agents-mvp\tests/__init__.py` (empty file).
Create `c:\Dev\Foundry\foundry-agents-mvp\tests/test_agent.py`:
```python
import pytest
from httpx import ASGITransport, AsyncClient
from src.agent.main import app

@pytest.mark.asyncio
async def test_readiness_probe():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/readiness")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ready"

@pytest.mark.asyncio
async def test_responses_endpoint_valid_turn():
    payload = {
        "messages": [
            {"role": "user", "content": "Hello, agent!"}
        ]
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/responses", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "content" in data["response"]
    assert len(data["response"]["content"]) > 0

@pytest.mark.asyncio
async def test_responses_endpoint_empty_messages():
    payload = {"messages": []}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/responses", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
```

- [ ] **Step 2: Run test to verify failure**

Run:
```powershell
.venv\Scripts\pytest tests/test_agent.py -v
```
Expected: FAIL with `ModuleNotFoundError: No module named 'src.agent.main'`

- [ ] **Step 3: Implement hosted agent service**

Create `c:\Dev\Foundry\foundry-agents-mvp\src/agent/__init__.py` (empty file).
Create `c:\Dev\Foundry\foundry-agents-mvp\src/agent/main.py`:
```python
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI(
    title="Foundry Hosted Agent",
    description="Azure AI Foundry hosted agent implementing the responses protocol",
    version="0.1.0"
)

class Message(BaseModel):
    role: str
    content: str

class ResponsesRequest(BaseModel):
    messages: List[Message] = Field(default_factory=list)
    temperature: Optional[float] = 0.7

class ResponseContent(BaseModel):
    role: str = "assistant"
    content: str

class ResponsesResponse(BaseModel):
    response: ResponseContent
    protocol: str = "responses"

@app.get("/readiness")
async def readiness():
    """Foundry health probe endpoint."""
    return {"status": "ready"}

@app.post("/responses", response_model=ResponsesResponse)
async def handle_responses(request: ResponsesRequest):
    """Foundry responses protocol conversational handler."""
    if not request.messages:
        return JSONResponse(
            status_code=400,
            content={"error": "The 'messages' list cannot be empty."}
        )

    last_user_message = request.messages[-1].content
    reply_text = f"Foundry Agent received: {last_user_message}"

    return ResponsesResponse(
        response=ResponseContent(role="assistant", content=reply_text),
        protocol="responses"
    )

def start():
    port = int(os.environ.get("PORT", 8088))
    uvicorn.run("src.agent.main:app", host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    start()
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```powershell
.venv\Scripts\pytest tests/test_agent.py -v
```
Expected: PASS (all 3 tests passing).

- [ ] **Step 5: Commit hosted agent service**

Run:
```bash
git add src/ tests/
git commit -m "feat: implement hosted agent runtime service with /readiness and /responses"
```
Expected: Clean git commit with agent code and tests.

---

### Task 4: End-to-End Local Execution & Contract Verification

**Files:**
- Create: `README.md`

**Interfaces:**
- Consumes: Running agent server on port 8088
- Produces: Verified live HTTP readiness check, validated responses exchange, project documentation

- [ ] **Step 1: Test live background server startup and HTTP probe**

Run in PowerShell:
```powershell
$proc = Start-Process -FilePath ".venv\Scripts\python.exe" -ArgumentList "src\agent\main.py" -PassThru
Start-Sleep -Seconds 3
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8088/readiness" -Method Get
    Write-Output "Readiness Status: $($response.status)"
    $chatBody = @{ messages = @( @{ role = "user"; content = "Ping test" } ) } | ConvertTo-Json
    $chatResponse = Invoke-RestMethod -Uri "http://localhost:8088/responses" -Method Post -Body $chatBody -ContentType "application/json"
    Write-Output "Chat Response: $($chatResponse.response.content)"
} finally {
    Stop-Process -Id $proc.Id -Force
}
```
Expected output:
- `Readiness Status: ready`
- `Chat Response: Foundry Agent received: Ping test`

- [ ] **Step 2: Create comprehensive `README.md`**

Create `c:\Dev\Foundry\foundry-agents-mvp\README.md`:
```markdown
# Foundry Agents MVP

Hosted AI Agent scaffolded for Microsoft Azure AI Foundry using the Azure Developer CLI (`azd`) and the `microsoft.foundry` extensions.

## Architecture
- **Protocol**: `responses` protocol
- **Port**: `8088`
- **Health Probe**: `GET /readiness`
- **Deploy Mode**: Code deployment (ZIP package)

## Prerequisites
- Python 3.10+
- Azure Developer CLI (`azd` >= 1.25.2)
- Foundry Extension bundle: `azd ext install microsoft.foundry`

## Local Setup & Development
1. Create and activate virtual environment:
   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements-dev.txt
   ```
2. Run tests:
   ```powershell
   pytest tests/ -v
   ```
3. Run agent locally:
   ```powershell
   python src/agent/main.py
   ```
4. Test health probe:
   ```powershell
   curl http://localhost:8088/readiness
   ```
5. Inspect locally with Foundry UI:
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
```

- [ ] **Step 3: Commit README and verify repository state**

Run:
```bash
git add README.md
git commit -m "docs: add project README with local run and deployment instructions"
git status
```
Expected: Clean working tree, on branch `main`.
