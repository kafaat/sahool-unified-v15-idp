"""
SAHOOL Auto Audit Tools
Comprehensive suite for automated audit log analysis, validation, and compliance

Tools included:
- Audit Log Analyzer: Pattern detection, statistical analysis, and reporting
- Hash Chain Validator: Verify integrity of audit trail
- Compliance Report Generator: Generate compliance reports for GDPR, SOC2, ISO27001
- Anomaly Detector: ML-based anomaly detection in audit patterns
- Audit Data Exporter: Export audit data in various formats
- Audit Agent: A2A-compliant intelligent audit agent with self-healing

The Audit Agent integrates all tools and provides:
- A2A Protocol compatibility for agent-to-agent communication
- Automated security monitoring and threat detection
- Compliance validation and reporting
- Self-healing recommendations
"""

__version__ = "1.0.0"
__author__ = "KAFAAT Team"

from .analyzer import AuditLogAnalyzer
from .anomaly_detector import AuditAnomalyDetector
from .compliance_reporter import ComplianceReporter
from .exporter import AuditDataExporter
from .hashchain_validator import HashChainValidator

# Conditional import for agent (requires A2A protocol)
try:
    from .agent import AuditAgent, create_audit_agent

    _AGENT_AVAILABLE = True
except ImportError:
    _AGENT_AVAILABLE = False
    AuditAgent = None
    create_audit_agent = None

__all__ = [
    "AuditLogAnalyzer",
    "HashChainValidator",
    "ComplianceReporter",
    "AuditAnomalyDetector",
    "AuditDataExporter",
]

if _AGENT_AVAILABLE:
    __all__.extend(["AuditAgent", "create_audit_agent"])
