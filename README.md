# AI-Powered Security Incident Response Agent

This project implements an intelligent security incident response system using LangGraph and Claude AI. The agent orchestrates automated response workflows across multiple security tools including Splunk MCP, Cisco Secure Endpoint, Cisco Firewall, and Splunk SOAR.

## Architecture Overview

The agent uses a sophisticated workflow that analyzes security incidents, performs threat assessment, and executes automated response actions based on AI-driven decision making.

### Workflow Flow

1. **Incident Analysis** - AI analyzes incoming security incidents
2. **Splunk Search** - Executes MCP searches for additional context
3. **Threat Assessment** - AI determines threat severity and recommended actions
4. **Automated Response** - Based on assessment:
   - **High/Critical Threats**: Endpoint isolation → Firewall blocking → SOAR case
   - **Medium Threats**: SOAR case creation only
   - **Low/Unknown**: Human review flagging
5. **Context Persistence** - Saves complete workflow history to database

## Project Structure

```
ai_agent_splunk_mcp_langgraph/
├── app/
│   ├── __init__.py
│   ├── agent.py             # Main SecurityIncidentAgent with LangGraph workflow
│   ├── state.py             # AgentState definition for workflow state management
│   └── tools/
│       ├── __init__.py
│       ├── splunk_mcp.py       # Splunk MCP connector for log searches
│       ├── cisco_secure_endpoint.py  # Cisco endpoint isolation
│       ├── cisco_firewall.py   # Cisco firewall IP blocking
│       ├── splunk_soar.py      # Splunk SOAR case management
│       ├── database.py         # Workflow context persistence
│       └── node_api.py         # Generic Node.js API connector
├── main.py                  # Main entry point
├── requirements.txt         # Python dependencies
└── .env.example             # Environment variables template
```

## Key Features

- **AI-Driven Analysis**: Uses Claude Sonnet 4 for intelligent incident analysis and threat assessment
- **Automated Response Orchestration**: Coordinates actions across multiple security tools based on threat severity
- **Splunk MCP Integration**: Advanced log searching and analysis using Splunk's Model Context Protocol
- **Multi-Tool Security Integration**:
  - Cisco Secure Endpoint for device isolation
  - Cisco Firewall for IP blocking
  - Splunk SOAR for case management
  - Database persistence for audit trails
- **Conditional Workflow Logic**: Dynamic decision trees based on AI assessment and threat indicators
- **Complete Audit Trail**: Saves entire workflow context including decisions, actions, and results

## Workflow Decision Points

The agent makes intelligent routing decisions at key points:

1. **Initial Analysis** → Proceed with search or end workflow
2. **Threat Assessment** → Route to:
   - **ISOLATE**: Critical threats requiring immediate endpoint isolation
   - **SOAR_ONLY**: Medium threats requiring case creation without isolation
   - **REVIEW**: Low-severity incidents flagged for human analysis

## Setup Instructions

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Environment Variables:**
    Copy the example environment file and fill in your credentials:
    ```bash
    cp .env.example .env
    ```
    Configure the following in your `.env` file:
    - Anthropic API key for Claude AI
    - Splunk MCP connection details
    - Cisco API credentials and endpoints
    - SOAR system configuration
    - Database connection string

3.  **Run the Agent:**
    ```bash
    python main.py
    ```

## Usage Example

```python
from app.agent import SecurityIncidentAgent

# Initialize the agent
agent = SecurityIncidentAgent()

# Define incident data
incident_data = """
Security Alert: Suspicious network activity detected
Source IP: 192.168.1.100
Destination: external-malicious-domain.com
Alert Type: Potential malware communication
Timestamp: 2024-01-01T12:00:00Z
"""

# Execute incident response workflow
result = agent.run_incident_response(incident_data)

# Check results
if result.get('error'):
    print(f"Workflow failed: {result['error']}")
else:
    print("Incident response completed successfully!")
    print(f"SOAR Case ID: {result.get('soar_case_id')}")
```

## Agent Components

### Core Classes

- **`SecurityIncidentAgent`**: Main orchestrator class that builds and executes the LangGraph workflow
- **`AgentState`**: State management for workflow data persistence across nodes

### Tool Integrations

- **`SplunkMCP`**: Advanced Splunk searches using Model Context Protocol (`app/tools/splunk_mcp.py:180`)
- **`CiscoSecureEndpoint`**: Endpoint isolation capabilities (`app/agent.py:247`)
- **`CiscoFirewall`**: IP blocking and firewall rules (`app/agent.py:138`)
- **`SplunkSOAR`**: Case creation and management (`app/agent.py:279`)
- **`Database`**: Workflow context and audit trail storage (`app/agent.py:311`)
