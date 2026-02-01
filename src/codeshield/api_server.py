"""
CodeShield API Server
Exposes CodeShield functionality via HTTP for the React Frontend.
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any
import uvicorn
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Import CodeShield core modules
# We wrap imports in try/except to handle potential missing dependencies during dev
try:
    from codeshield.trustgate.checker import verify_code
    from codeshield.trustgate.sandbox import full_verification
    from codeshield.styleforge.corrector import check_style
    from codeshield.contextvault.capture import save_context, list_contexts
    from codeshield.contextvault.restore import restore_context
except ImportError:
    # Fallback for dev environment if paths aren't set up
    print("WARNING: Could not import CodeShield modules. Ensure you are running as a module.")
    verify_code = None
    full_verification = None
    check_style = None
    save_context = None
    list_contexts = None
    restore_context = None

app = FastAPI(title="CodeShield API", version="0.1.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---

class VerifyRequest(BaseModel):
    code: str
    auto_fix: bool = True
    use_sandbox: bool = False

class StyleCheckRequest(BaseModel):
    code: str
    codebase_path: str = "."

class ContextSaveRequest(BaseModel):
    name: str
    files: List[str] = []
    cursor: Optional[dict] = None
    notes: Optional[str] = None

class ContextRestoreRequest(BaseModel):
    name: str

# --- Endpoints ---

@app.get("/api/health")
async def health_check():
    return {"status": "online", "service": "CodeShield API"}

@app.post("/api/verify")
async def api_verify_code(req: VerifyRequest):
    if not verify_code:
        return {"error": "Backend modules not loaded"}
    
    if req.use_sandbox:
        # Full sandbox verification
        result = full_verification(req.code)
        return result
    else:
        # Fast static verification
        result = verify_code(req.code, auto_fix=req.auto_fix)
        return result.to_dict()

@app.post("/api/style")
async def api_check_style(req: StyleCheckRequest):
    if not check_style:
        return {"error": "Backend modules not loaded"}
    
    result = check_style(req.code, req.codebase_path)
    return result.to_dict()

@app.post("/api/context/save")
async def api_save_context(req: ContextSaveRequest):
    if not save_context:
        return {"error": "Backend modules not loaded"}
    
    result = save_context(
        name=req.name,
        files=req.files,
        cursor=req.cursor,
        notes=req.notes
    )
    return result

@app.post("/api/context/restore")
async def api_restore_context(req: ContextRestoreRequest):
    if not restore_context:
        return {"error": "Backend modules not loaded"}
    
    result = restore_context(name=req.name)
    return result

@app.get("/api/contexts")
async def api_list_contexts():
    if not list_contexts:
        return {"error": "Backend modules not loaded"}
    
    result = list_contexts()
    return result

# --- Frontend Static Serving ---

# Mount assets (CSS/JS)
if os.path.exists("frontend/dist/assets"):
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

# Serve other static files (favicon, etc.) and SPA fallback
@app.get("/{full_path:path}")
async def serve_static(full_path: str):
    # API requests are handled by routes above.
    # If we get here, it's a static file or client-side route.
    
    # Security: Prevent traversing up? FileResponse handles it.
    
    dist_dir = "frontend/dist"
    if not os.path.exists(dist_dir):
        return {"status": "Frontend not built", "deployment": "backend-only"}

    # Try to find specific file
    file_path = os.path.join(dist_dir, full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # Fallback to index.html for SPA routing
    return FileResponse(os.path.join(dist_dir, "index.html"))


if __name__ == "__main__":
    uvicorn.run("codeshield.api_server:app", host="0.0.0.0", port=8000, reload=True)
