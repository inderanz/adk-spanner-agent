# Cloud Spanner Natural Language Agent
<img width="1464" height="879" alt="image" src="https://github.com/user-attachments/assets/4dd74d38-f710-4fdb-afc8-feb5ac90d8bb" />

A comprehensive, secure, and production-ready natural language interface for Google Cloud Spanner databases built with the Google Agent Development Kit (ADK).

## Features

### Core Capabilities
- **Natural Language Query Interface**: Ask questions about your data in plain English
- **Comprehensive Schema Exploration**: Discover tables, columns, indexes, and relationships
- **Advanced Analytics**: Get insights, statistics, and performance analysis
- **Security-First Design**: Read-only operations with comprehensive audit logging
- **Production Monitoring**: Health checks, metrics, and observability

### Security Features
-  **Read-Only Operations**: Prevents destructive database operations
-  **SQL Injection Protection**: Comprehensive query validation
-  **Audit Logging**: Complete audit trail for compliance
-  **Rate Limiting**: Prevents resource exhaustion
-  **Least Privilege Access**: Minimal IAM permissions
-  **Workload Identity**: Secure authentication without service account keys

### Advanced Functionality
- **Query Performance Analysis**: Get optimization recommendations
- **Table Statistics**: Detailed metadata and row counts
- **Database Health Monitoring**: Connection status and metrics
- **Schema Visualization**: Understand database structure
- **Error Handling**: Graceful failure handling with retries

##  Prerequisites

### Google Cloud Requirements
- Google Cloud Project with billing enabled
- Google Kubernetes Engine (GKE) cluster with Workload Identity enabled
- Cloud Spanner instance and database
- Vertex AI API enabled
- Artifact Registry repository

### Required APIs
```bash
# Enable required APIs
gcloud services enable \
  spanner.googleapis.com \
  aiplatform.googleapis.com \
  container.googleapis.com \
  artifactregistry.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com
```

## 🛠 Installation & Setup

### 1. Clone and Configure

```bash
git clone <repository-url>
cd spanner_agent_project

# Update configuration
# Edit k8s/configmap.yaml with your Spanner details
```

### 2. Create GCP Service Account

```bash
# Create service account
gcloud iam service-accounts create spanner-agent-sa \
  --display-name="Spanner Agent Service Account" \
  --description="Service account for Spanner Agent with least-privilege access"

# Assign least-privilege IAM roles
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:spanner-agent-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/spanner.databaseViewer"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:spanner-agent-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:spanner-agent-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/logging.logWriter"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:spanner-agent-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/monitoring.metricWriter"

# Enable Workload Identity binding
gcloud iam service-accounts add-iam-policy-binding \
  spanner-agent-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="serviceAccount:YOUR_PROJECT_ID.svc.id.goog[default/spanner-agent-sa]"
```

### 3. Build and Deploy

```bash
# Build and push container image
gcloud builds submit . --tag us-central1-docker.pkg.dev/YOUR_PROJECT_ID/agent-repo/spanner-agent:latest

# Apply Kubernetes manifests
kubectl apply -f k8s/serviceaccount.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Verify deployment
kubectl get pods -l app=spanner-agent
kubectl logs -l app=spanner-agent
```

### 4. Access the Application

```bash
# Port forward to access the ADK UI
kubectl port-forward deployment/spanner-agent 8080:8080

# Open in browser: http://localhost:8080
```

##  Security Configuration

### IAM Roles and Permissions

| Role | Purpose | Scope |
|------|---------|-------|
| `roles/spanner.databaseViewer` | Read-only access to Spanner databases | Database level |
| `roles/aiplatform.user` | Access to Vertex AI for LLM operations | Project level |
| `roles/logging.logWriter` | Write audit logs to Cloud Logging | Project level |
| `roles/monitoring.metricWriter` | Write metrics to Cloud Monitoring | Project level |

### Security Features

#### Query Validation
- Blocks dangerous SQL patterns (DELETE, DROP, ALTER, etc.)
- Enforces read-only operations
- Limits query complexity and length
- Prevents SQL injection attacks

#### Access Control
- Workload Identity for secure authentication
- No service account keys required
- Pod-level security contexts
- Network policies (configurable)

#### Audit and Compliance
- Complete audit trail of all operations
- User and session tracking
- Query execution logging
- Performance metrics collection

## 📊 Monitoring and Observability

### Health Checks
- **Readiness Probe**: `/healthz` endpoint
- **Liveness Probe**: Application health monitoring
- **Startup Probe**: Initialization verification

### Metrics
- Query execution times
- Success/failure rates
- Resource utilization
- Custom business metrics

### Logging
- Structured JSON logs
- Audit trail for compliance
- Error tracking and debugging
- Performance analysis

##  Usage Examples

### Basic Queries
```
"Show me the first 10 users"
"List all tables in the database"
"What's the total number of orders?"
"Find users who signed up this month"
```

### Advanced Analytics
```
"Analyze the performance of the users table"
"Show me database health metrics"
"Get statistics for the orders table"
"Find the most active users in the last 30 days"
```

### Schema Exploration
```
"What tables are available?"
"Show me the structure of the users table"
"What indexes exist on the orders table?"
"Describe the relationships between tables"
```

##  Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SPANNER_PROJECT` | Required | GCP Project ID |
| `SPANNER_INSTANCE` | Required | Spanner Instance ID |
| `SPANNER_DATABASE` | Required | Spanner Database ID |
| `SPANNER_READ_ONLY` | `true` | Enforce read-only operations |
| `SPANNER_MAX_ROWS` | `1000` | Maximum rows per query |
| `SPANNER_QUERY_TIMEOUT` | `30` | Query timeout in seconds |
| `MODEL_NAME` | `gemini-2.5-flash` | Vertex AI model to use |
| `ENABLE_AUDIT_LOGGING` | `true` | Enable audit logging |

### Feature Flags
- `ENABLE_QUERY_ANALYSIS`: Performance analysis
- `ENABLE_SCHEMA_EXPLORATION`: Schema discovery
- `ENABLE_TABLE_STATISTICS`: Table metadata
- `ENABLE_HEALTH_MONITORING`: Health checks


### Common Issues

#### 1. Permission Denied Errors
```bash
# Verify Workload Identity is enabled
gcloud container clusters describe YOUR_CLUSTER --zone=YOUR_ZONE --format="value(workloadPool)"

# Check service account binding
kubectl get serviceaccount spanner-agent-sa -o yaml
```

#### 2. Model Not Found Errors
```bash
# Check available models in your region
gcloud ai models list --region=us-central1 --filter="name:gemini"

# Update MODEL_NAME in configmap
kubectl edit configmap spanner-agent-config
```

#### 3. Database Connection Issues
```bash
# Verify Spanner instance and database
gcloud spanner instances list
gcloud spanner databases list --instance=YOUR_INSTANCE

# Check pod logs
kubectl logs -l app=spanner-agent
```

### Debug Mode
```bash
# Enable debug logging
kubectl patch configmap spanner-agent-config --patch '{"data":{"LOG_LEVEL":"DEBUG"}}'
kubectl rollout restart deployment spanner-agent
```

##  Learning ADK

### ADK Concepts

The Google Agent Development Kit (ADK) provides a framework for building AI agents. This project demonstrates:

1. **Agent Definition**: Creating agents with tools and instructions
2. **Tool Functions**: Implementing callable functions for the agent
3. **Security**: Building secure, production-ready agents
4. **Deployment**: Containerizing and deploying agents to Kubernetes

### Key ADK Components

#### Agent Definition
```python
root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="spanner_agent",
    description="Production-grade Cloud Spanner database assistant",
    instruction=AGENT_INSTRUCTIONS,
    tools=[run_spanner_query, get_spanner_schema, ...]
)
```

#### Tool Functions
```python
def run_spanner_query(sql: str) -> Dict[str, Any]:
    """Execute SQL query with security validation."""
    # Implementation with security checks
    pass
```

#### Instructions
The agent instructions guide the LLM's behavior and capabilities, ensuring consistent, secure, and helpful responses.

### ADK Best Practices

1. **Security First**: Always validate inputs and enforce security policies
2. **Clear Instructions**: Provide detailed, actionable instructions to the agent
3. **Error Handling**: Implement comprehensive error handling and logging
4. **Monitoring**: Add observability and monitoring capabilities
5. **Testing**: Test agents thoroughly before production deployment
