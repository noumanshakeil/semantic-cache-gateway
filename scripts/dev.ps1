# Dev server for semantic-cache-gateway
$env:LLM_MODE = "mock"
uvicorn backend.main:app --reload --port 8000
