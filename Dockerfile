# Dockerfile for the Spanner natural language agent.

# Use a slim Python base image for a minimal footprint.  Python 3.11
# provides good performance and security updates.
FROM python:3.11-slim

# Install system dependencies needed by `google-cloud-spanner` at runtime.  The
# default slim image does not include these.
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python requirements and install them.  Use a virtual environment to
# isolate dependencies.  The `--no-cache-dir` flag reduces image size.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create a non‑root user to run the application.  Running as non‑root is a
# recommended security practice for containers.
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app

# Copy the project code into the image.  We copy the spanner_agent package
# and the FastAPI entrypoint separately to allow layer caching when only
# application code changes.
COPY spanner_agent ./spanner_agent
COPY main.py .

# Switch to the non‑root user for the remainder of the image build and at
# runtime.  Also add the user's local bin directory to PATH so that installed
# CLI tools (e.g. uvicorn) are discoverable.
USER appuser
ENV PATH="/home/appuser/.local/bin:$PATH"

# Expose the port that the FastAPI app listens on.  Kubernetes uses this for
# containerPort in the Deployment manifest.
EXPOSE 8080

# Define the default command.  Uvicorn serves the FastAPI app defined in
# main.py.  Do not hard-code the port here; use the PORT environment variable
# instead.  In Kubernetes the PORT environment variable will be set via the
# manifest.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
