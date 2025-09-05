# LangGraph Studio Interactive Demo

This project is now configured for **LangGraph Studio** visualization and interactive testing!

## 🚀 Getting Started with LangGraph Studio

### 1. Install LangGraph Studio
```bash
pip install langgraph-studio
```

### 2. Launch Studio
```bash
# From the project root directory
langgraph studio
```

### 3. Open in Browser
- Studio will automatically open at `http://localhost:3000`
- Select the "Interactive Security Incident Response Agent" graph

## 🎯 What You Can Explore

### Interactive Graph Visualization
- **6 nodes**: classify_incident → investigate_threat → assess_risk → execute_response → create_report
- **2 conditional decision points**: Investigation routing & Response level determination
- **Visual node connections**: See the complete workflow flow
- **State inspection**: View state changes at each step

### Test Scenarios
Try these sample incidents in the Studio interface:

1. **Low Severity**: `"Minor login anomaly detected for user john.doe"`
2. **Medium Severity**: `"Suspicious network activity: Multiple connections to unknown external IP"`  
3. **High Severity**: `"Malware detected on critical server, active threat confirmed"`
4. **Critical Severity**: `"Active data exfiltration detected, multiple systems compromised"`

### State Schema
```python
{
    "messages": [List of AI/Human messages],
    "incident_severity": "Low|Medium|High|Critical", 
    "requires_investigation": Boolean,
    "investigation_results": "Investigation findings",
    "threat_level": "Assessed threat level",
    "actions_taken": [List of response actions],
    "case_status": "Workflow status"
}
```

## 🔧 Features for Studio Exploration

### 1. **Node Inspection**
- Click on any node to see its implementation
- View input/output state changes
- Monitor execution timing

### 2. **Conditional Routing Logic**
```python
# Investigation Decision
def _should_investigate(state):
    if severity == "Critical":
        return "escalate"  # Skip to human analyst
    elif requires_investigation:
        return "investigate"  # Automated investigation
    else:
        return "escalate"  # Human review

# Response Level Decision  
def _determine_response_level(state):
    if threat_level in ["Low", "Medium"]:
        return "automated"  # Execute automated response
    else:
        return "manual"  # Escalate to analyst
```

### 3. **Step-by-Step Execution**
- Run workflows step-by-step
- Pause at any node
- Inspect intermediate states
- Modify state values and continue

### 4. **Interactive Testing**
- Input custom incident descriptions
- Watch AI classification in real-time
- See decision points trigger different paths
- View final reports and action summaries

## 📊 Workflow Paths

### Path 1: Automated Response
`START → classify_incident → investigate_threat → assess_risk → execute_response → create_report → END`

### Path 2: Human Escalation (Critical)
`START → classify_incident → escalate_to_analyst → create_report → END`

### Path 3: Manual Review (High Threat)
`START → classify_incident → investigate_threat → assess_risk → escalate_to_analyst → create_report → END`

## 🎮 Interactive Demo Features

- **No External Dependencies**: Simplified for Studio exploration
- **AI-Powered Decisions**: Real Claude Sonnet 4 reasoning
- **Multiple Execution Paths**: Based on incident severity and threat assessment
- **Rich State Tracking**: Complete audit trail of decisions
- **Realistic Scenarios**: Security incident patterns and responses

## 🔍 Debugging Capabilities

- **State Visualization**: See how state evolves through each node
- **Message Tracking**: Follow AI reasoning and decision-making
- **Conditional Logic**: Understand why certain paths are taken
- **Error Handling**: Test failure scenarios and recovery

Start exploring your security workflow in LangGraph Studio! 🚀