# Security Documentation

## Overview

This document outlines the comprehensive security measures implemented in the Production-Grade Cloud Spanner Natural Language Agent. The system is designed with security-first principles, implementing defense-in-depth strategies to protect data and ensure compliance.

## 🔒 Security Architecture

### Defense in Depth

The security architecture follows a multi-layered approach:

1. **Network Security**: Kubernetes network policies and service mesh
2. **Container Security**: Pod security policies and runtime security
3. **Application Security**: Input validation and secure coding practices
4. **Data Security**: Encryption at rest and in transit
5. **Access Control**: Least privilege and identity-based access

### Security Principles

- **Zero Trust**: Never trust, always verify
- **Least Privilege**: Minimum necessary permissions
- **Defense in Depth**: Multiple security layers
- **Security by Design**: Built-in from the ground up
- **Continuous Monitoring**: Real-time security monitoring

## 🛡️ Security Features

### 1. Authentication & Authorization

#### Workload Identity
- **Technology**: Google Cloud Workload Identity Federation
- **Purpose**: Secure authentication without service account keys
- **Implementation**: Kubernetes service account mapped to GCP service account
- **Benefits**: 
  - No long-lived credentials
  - Automatic credential rotation
  - Audit trail for all access

#### Service Account Configuration
```yaml
# Kubernetes Service Account
apiVersion: v1
kind: ServiceAccount
metadata:
  name: spanner-agent-sa
  annotations:
    iam.gke.io/gcp-service-account: spanner-agent-sa@PROJECT_ID.iam.gserviceaccount.com
```

### 2. IAM Roles & Permissions

#### Least Privilege Access

| Role | Scope | Permissions | Justification |
|------|-------|-------------|---------------|
| `roles/spanner.databaseViewer` | Database | Read-only access to Spanner databases | Query data without modification capabilities |
| `roles/aiplatform.user` | Project | Access Vertex AI models | Required for LLM operations |
| `roles/logging.logWriter` | Project | Write audit logs | Compliance and monitoring requirements |
| `roles/monitoring.metricWriter` | Project | Write metrics | Observability and performance monitoring |

#### Role Assignment Commands
```bash
# Spanner Database Viewer (Read-only)
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:spanner-agent-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/spanner.databaseViewer"

# Vertex AI User
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:spanner-agent-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# Logging Writer
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:spanner-agent-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/logging.logWriter"

# Monitoring Writer
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:spanner-agent-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/monitoring.metricWriter"
```

### 3. Query Security

#### SQL Injection Prevention

**Pattern-Based Validation**
```python
DANGEROUS_PATTERNS = [
    r'\b(DELETE|DROP|TRUNCATE|ALTER|CREATE|INSERT|UPDATE|GRANT|REVOKE)\b',
    r'\b(EXEC|EXECUTE|sp_|xp_)\b',
    r'--.*$',  # SQL comments
    r'/\*.*?\*/',  # Multi-line comments
    r';\s*$',  # Multiple statements
    r'UNION\s+ALL\s+SELECT',  # Union attacks
    r'INFORMATION_SCHEMA\.(TABLES|COLUMNS)',  # Schema enumeration
]
```

**Read-Only Enforcement**
- All operations are read-only by default
- Only SELECT, WITH, SHOW, DESCRIBE queries allowed
- DML operations (INSERT, UPDATE, DELETE) blocked
- DDL operations (CREATE, ALTER, DROP) blocked

**Query Complexity Limits**
- Maximum query length: 10,000 characters
- Maximum SELECT statements: 3 per query
- Maximum rows returned: 1,000 per query
- Query timeout: 30 seconds

### 4. Container Security

#### Pod Security Standards

**Security Context**
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 3000
  fsGroup: 2000
  seccompProfile:
    type: RuntimeDefault
  capabilities:
    drop:
      - ALL
```

**Container Security**
```yaml
securityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 3000
  capabilities:
    drop:
      - ALL
  seccompProfile:
    type: RuntimeDefault
```

#### Image Security
- Base image: Official Python slim image
- Multi-stage build to reduce attack surface
- Non-root user execution
- Minimal dependencies
- Regular security updates

### 5. Network Security

#### Kubernetes Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: spanner-agent-network-policy
spec:
  podSelector:
    matchLabels:
      app: spanner-agent
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to: []
    ports:
    - protocol: TCP
      port: 443
    - protocol: TCP
      port: 80
```

#### Service Mesh (Optional)
- Istio or Linkerd for advanced traffic management
- mTLS encryption between services
- Fine-grained access control
- Traffic monitoring and logging

### 6. Data Protection

#### Encryption
- **At Rest**: Cloud Spanner encryption
- **In Transit**: TLS 1.3 for all communications
- **Secrets**: Kubernetes secrets with encryption

#### Data Classification
- **Public**: Non-sensitive configuration
- **Internal**: Application logs and metrics
- **Confidential**: Database queries and results
- **Restricted**: Audit logs and security events

### 7. Audit & Compliance

#### Comprehensive Logging
```python
audit_entry = {
    "timestamp": datetime.utcnow().isoformat(),
    "operation": operation,
    "user_id": security_context.user_id,
    "session_id": security_context.session_id,
    "project_id": self.project_id,
    "instance_id": self.instance_id,
    "database_id": self.database_id,
    "details": details
}
```

#### Audit Events
- **Query Execution**: All SQL queries with results
- **Query Rejection**: Blocked queries with reasons
- **Authentication**: Service account access
- **Authorization**: Permission checks
- **System Events**: Health checks and errors

#### Compliance Features
- **GDPR**: Data minimization and right to be forgotten
- **SOX**: Financial data protection
- **HIPAA**: Healthcare data privacy
- **PCI DSS**: Payment card data security

### 8. Monitoring & Alerting

#### Security Monitoring
```yaml
# Prometheus metrics
- name: spanner_queries_total
  help: "Total number of Spanner queries"
  type: counter

- name: spanner_queries_blocked
  help: "Number of blocked queries"
  type: counter

- name: spanner_query_duration_seconds
  help: "Query execution time"
  type: histogram
```

#### Security Alerts
- Failed authentication attempts
- Blocked queries (potential attacks)
- Unusual query patterns
- Resource exhaustion
- Service account privilege escalation

## 🚨 Security Incident Response

### Incident Classification

| Severity | Description | Response Time |
|----------|-------------|---------------|
| Critical | Data breach or system compromise | 1 hour |
| High | Unauthorized access attempt | 4 hours |
| Medium | Suspicious activity detected | 24 hours |
| Low | Security policy violation | 72 hours |

### Response Procedures

1. **Detection**: Automated monitoring and alerting
2. **Assessment**: Impact analysis and containment
3. **Response**: Immediate mitigation actions
4. **Recovery**: System restoration and validation
5. **Post-Incident**: Lessons learned and improvements

## 🔍 Security Testing

### Automated Security Scans

#### Container Scanning
```bash
# Trivy vulnerability scanner
trivy image us-central1-docker.pkg.dev/PROJECT_ID/agent-repo/spanner-agent:latest

# Snyk container scanning
snyk container test us-central1-docker.pkg.dev/PROJECT_ID/agent-repo/spanner-agent:latest
```

#### Code Security Analysis
```bash
# Bandit security linter
bandit -r spanner_agent/

# Semgrep security scanning
semgrep --config=auto spanner_agent/
```

#### Dependency Scanning
```bash
# Safety vulnerability checker
safety check

# Snyk dependency scanning
snyk test
```

### Penetration Testing

#### SQL Injection Testing
- Automated SQL injection payload testing
- Manual query manipulation attempts
- Schema enumeration prevention testing

#### Authentication Testing
- Service account privilege escalation
- Workload Identity bypass attempts
- Token manipulation testing

#### Container Escape Testing
- Privilege escalation attempts
- File system access testing
- Network isolation verification

## 📋 Compliance Checklist

### Security Controls

- [ ] **Access Control**
  - [ ] Least privilege principle implemented
  - [ ] Workload Identity configured
  - [ ] Service account permissions documented
  - [ ] Regular access reviews conducted

- [ ] **Data Protection**
  - [ ] Encryption at rest enabled
  - [ ] Encryption in transit enabled
  - [ ] Data classification implemented
  - [ ] Data retention policies defined

- [ ] **Monitoring & Logging**
  - [ ] Comprehensive audit logging
  - [ ] Security event monitoring
  - [ ] Alerting configured
  - [ ] Log retention policies

- [ ] **Incident Response**
  - [ ] Incident response plan documented
  - [ ] Security team contacts defined
  - [ ] Escalation procedures established
  - [ ] Post-incident review process

### Compliance Frameworks

- [ ] **GDPR Compliance**
  - [ ] Data minimization implemented
  - [ ] Right to be forgotten supported
  - [ ] Data processing agreements
  - [ ] Privacy impact assessments

- [ ] **SOX Compliance**
  - [ ] Financial data protection
  - [ ] Audit trail maintenance
  - [ ] Access control documentation
  - [ ] Change management procedures

- [ ] **HIPAA Compliance**
  - [ ] PHI data protection
  - [ ] Access logging requirements
  - [ ] Encryption standards
  - [ ] Business associate agreements

## 🔄 Security Maintenance

### Regular Security Tasks

#### Monthly
- Security patch updates
- Dependency vulnerability scanning
- Access review and cleanup
- Security metric review

#### Quarterly
- Penetration testing
- Security architecture review
- Compliance audit
- Incident response testing

#### Annually
- Security policy review
- Risk assessment update
- Security training refresh
- Business continuity testing

### Security Updates

#### Critical Updates
- Zero-day vulnerabilities
- Security patches
- Configuration changes
- Emergency deployments

#### Regular Updates
- Dependency updates
- Security tool updates
- Policy updates
- Documentation updates

## 📞 Security Contacts

### Security Team
- **Security Lead**: [security@company.com]
- **Incident Response**: [incident@company.com]
- **Compliance**: [compliance@company.com]

### Escalation Procedures
1. **Level 1**: Security team (24/7)
2. **Level 2**: Security lead (business hours)
3. **Level 3**: CISO (critical incidents)

### External Contacts
- **Google Cloud Security**: [Google Cloud Support]
- **Kubernetes Security**: [Kubernetes Security Team]
- **Vendor Security**: [Vendor Security Contacts]

---

**Note**: This security documentation should be reviewed and updated regularly to ensure it reflects current security practices and compliance requirements. 