from codeshield.api_server import app

# Expose 'app' (FastAPI) for LeanMCP to serve the REST API
# This allows the Frontend to communicate with the deployment

# Lambda handler for serverless deployments (LeanMCP / AWS Lambda)
try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
except ImportError:
    # mangum not installed — running via uvicorn/Docker instead
    handler = None

