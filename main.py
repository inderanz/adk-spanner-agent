"""FastAPI entrypoint for the Spanner natural language agent.

This module defines a FastAPI application that serves the agent over HTTP.  It
uses the Agent Development Kit's `get_fast_api_app` helper to wrap the agent
into an API.  When deployed on GKE or other hosting environments, uvicorn
invokes this module to start the server.
"""

import os

import uvicorn
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app


# Determine the directory that contains this file.  Point the ADK at the
# directory that CONTAINS the agent packages (e.g. this file's folder), not at
# a specific agent package. The ADK scans immediate subdirectories for
# packages that expose `root_agent` in `<package>/agent.py`.
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Use SQLite for session persistence. Store the DB under /tmp because the root
# filesystem is read-only in Kubernetes (readOnlyRootFilesystem: true), while
# /tmp is mounted as a writable emptyDir volume in the Deployment.
# You can override the path with SESSION_DB_PATH if needed.
SESSION_DB_PATH = os.environ.get("SESSION_DB_PATH", "/tmp/sessions.db")
SESSION_SERVICE_URI = f"sqlite:///{SESSION_DB_PATH}"

# Allow requests from any origin by default.  Restrict this list in
# production to trusted domains.  When deploying behind an internal
# load balancer, you may remove CORS entirely.
ALLOWED_ORIGINS = ["*"]

# Serve the web interface so users can interact with the agent via a
# browser.  Set this to False if you only need the API endpoints.
SERVE_WEB_INTERFACE = True


app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    session_service_uri=SESSION_SERVICE_URI,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
)


# Kubernetes readiness/liveness endpoint expected by the Deployment probes
@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    # Use the PORT environment variable if provided (e.g. Cloud Run), default to
    # port 8080.  Uvicorn will start the ASGI server on the specified host and
    # port.  Do not set reload=True in production.
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
