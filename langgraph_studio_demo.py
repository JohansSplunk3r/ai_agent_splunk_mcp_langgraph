#!/usr/bin/env python3
"""
LangGraph Studio-Compatible Interactive Demo

This script creates a simplified, interactive version of the SecurityIncidentAgent
that can be explored in LangGraph Studio for visualization and debugging.
"""

import os
import json
import logging
from typing import Dict, Any, Literal, TypedDict, Annotated
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# State definition for LangGraph Studio compatibility
class InteractiveAgentState(TypedDict):
    """State schema for the interactive security agent."""
    messages: Annotated[list[BaseMessage], add_messages]
    incident_severity: str
    requires_investigation: bool
    investigation_results: str
    threat_level: str
    actions_taken: list[str]
    case_status: str

class InteractiveSecurityAgent:
    """
    Simplified Security Agent designed for LangGraph Studio exploration.
    
    This version focuses on the core decision-making flow without external
    tool dependencies, making it perfect for testing and visualization.
    """
    
    def __init__(self):
        self.model = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            temperature=0.1,
            max_tokens=1024
        )
        
        # Build the graph
        self.graph = self._build_interactive_graph()
    
    def _build_interactive_graph(self) -> StateGraph:
        """Build an interactive LangGraph for Studio visualization."""
        
        workflow = StateGraph(InteractiveAgentState)
        
        # Add nodes
        workflow.add_node("classify_incident", self._classify_incident_node)
        workflow.add_node("investigate_threat", self._investigate_threat_node) 
        workflow.add_node("assess_risk", self._assess_risk_node)
        workflow.add_node("execute_response", self._execute_response_node)
        workflow.add_node("create_report", self._create_report_node)
        workflow.add_node("escalate_to_analyst", self._escalate_to_analyst_node)
        
        # Set entry point
        workflow.set_entry_point("classify_incident")
        
        # Add conditional routing
        workflow.add_conditional_edges(
            "classify_incident",
            self._should_investigate,
            {
                "investigate": "investigate_threat",
                "escalate": "escalate_to_analyst"
            }
        )
        
        workflow.add_edge("investigate_threat", "assess_risk")
        
        workflow.add_conditional_edges(
            "assess_risk", 
            self._determine_response_level,
            {
                "automated": "execute_response",
                "manual": "escalate_to_analyst"
            }
        )
        
        workflow.add_edge("execute_response", "create_report")
        workflow.add_edge("escalate_to_analyst", "create_report")
        workflow.add_edge("create_report", END)
        
        return workflow.compile()
    
    def _classify_incident_node(self, state: InteractiveAgentState) -> Dict[str, Any]:
        """Classify the security incident using AI."""
        logger.info("🔍 Classifying security incident...")
        
        # Get the incident data from messages
        incident_data = state["messages"][-1].content if state["messages"] else "Unknown incident"
        
        classification_prompt = f"""
        Analyze this security incident and classify it:
        
        Incident: {incident_data}
        
        Provide:
        1. Severity level (Low/Medium/High/Critical)
        2. Whether it requires automated investigation (Yes/No)
        3. Brief classification reasoning
        
        Format your response as:
        SEVERITY: [level]
        INVESTIGATE: [Yes/No] 
        REASONING: [brief explanation]
        """
        
        try:
            response = self.model.invoke([HumanMessage(content=classification_prompt)])
            
            # Parse response (simplified)
            content = response.content
            severity = "Medium"  # Default
            requires_investigation = True  # Default
            
            if "SEVERITY:" in content:
                severity_line = [line for line in content.split('\n') if "SEVERITY:" in line][0]
                severity = severity_line.split("SEVERITY:")[-1].strip()
            
            if "INVESTIGATE:" in content:
                investigate_line = [line for line in content.split('\n') if "INVESTIGATE:" in line][0]
                requires_investigation = "Yes" in investigate_line
            
            return {
                "messages": [AIMessage(content=f"Incident classified: {content}")],
                "incident_severity": severity,
                "requires_investigation": requires_investigation
            }
            
        except Exception as e:
            logger.error(f"Classification error: {e}")
            return {
                "messages": [AIMessage(content=f"Classification failed: {str(e)}")],
                "incident_severity": "Unknown",
                "requires_investigation": False
            }
    
    def _investigate_threat_node(self, state: InteractiveAgentState) -> Dict[str, Any]:
        """Simulate threat investigation."""
        logger.info("🔎 Investigating potential threat...")
        
        # Simulate investigation results based on severity
        severity = state.get("incident_severity", "Medium")
        
        investigation_results = {
            "Critical": "Multiple indicators of compromise detected. Active threat confirmed.",
            "High": "Suspicious activity patterns identified. Potential security breach.", 
            "Medium": "Anomalous behavior detected. Requires further monitoring.",
            "Low": "Minor security event. Appears to be false positive."
        }
        
        result = investigation_results.get(severity, "Investigation inconclusive.")
        
        return {
            "messages": [AIMessage(content=f"Investigation complete: {result}")],
            "investigation_results": result
        }
    
    def _assess_risk_node(self, state: InteractiveAgentState) -> Dict[str, Any]:
        """Assess risk level and determine response strategy."""
        logger.info("⚠️ Assessing risk level...")
        
        severity = state.get("incident_severity", "Medium")
        investigation = state.get("investigation_results", "")
        
        risk_assessment_prompt = f"""
        Based on this security analysis, determine the threat level:
        
        Severity: {severity}
        Investigation: {investigation}
        
        Determine:
        - Threat Level (Low/Medium/High/Critical)
        - Response Type (Automated/Manual)
        - Recommended Actions
        
        Format:
        THREAT_LEVEL: [level]
        RESPONSE: [Automated/Manual]
        ACTIONS: [comma-separated list]
        """
        
        try:
            response = self.model.invoke([HumanMessage(content=risk_assessment_prompt)])
            content = response.content
            
            # Parse threat level
            threat_level = "Medium"  # Default
            if "THREAT_LEVEL:" in content:
                threat_line = [line for line in content.split('\n') if "THREAT_LEVEL:" in line][0]
                threat_level = threat_line.split("THREAT_LEVEL:")[-1].strip()
            
            return {
                "messages": [AIMessage(content=f"Risk assessment: {content}")],
                "threat_level": threat_level
            }
            
        except Exception as e:
            logger.error(f"Risk assessment error: {e}")
            return {
                "messages": [AIMessage(content=f"Risk assessment failed: {str(e)}")],
                "threat_level": "Unknown"
            }
    
    def _execute_response_node(self, state: InteractiveAgentState) -> Dict[str, Any]:
        """Execute automated security response actions."""
        logger.info("🚀 Executing automated response...")
        
        threat_level = state.get("threat_level", "Medium")
        
        # Define response actions based on threat level
        response_actions = {
            "Critical": ["isolate_endpoints", "block_malicious_ips", "create_soar_case", "alert_soc_team"],
            "High": ["quarantine_files", "update_firewall_rules", "create_soar_case"],
            "Medium": ["log_event", "update_monitoring", "create_ticket"],
            "Low": ["log_event", "update_baseline"]
        }
        
        actions = response_actions.get(threat_level, ["log_event"])
        
        # Simulate action execution
        action_results = []
        for action in actions:
            action_results.append(f"✅ {action.replace('_', ' ').title()}: Success")
        
        return {
            "messages": [AIMessage(content=f"Automated response executed: {', '.join(actions)}")],
            "actions_taken": actions,
            "case_status": "automated_response_complete"
        }
    
    def _escalate_to_analyst_node(self, state: InteractiveAgentState) -> Dict[str, Any]:
        """Escalate incident to human analyst."""
        logger.info("👤 Escalating to security analyst...")
        
        return {
            "messages": [AIMessage(content="Incident escalated to security analyst for manual review")],
            "case_status": "escalated_to_analyst",
            "actions_taken": ["escalate_to_analyst"]
        }
    
    def _create_report_node(self, state: InteractiveAgentState) -> Dict[str, Any]:
        """Generate final incident report."""
        logger.info("📋 Creating incident report...")
        
        # Compile report from state
        report = {
            "incident_severity": state.get("incident_severity", "Unknown"),
            "threat_level": state.get("threat_level", "Unknown"), 
            "investigation_results": state.get("investigation_results", "None"),
            "actions_taken": state.get("actions_taken", []),
            "case_status": state.get("case_status", "completed"),
            "total_messages": len(state.get("messages", []))
        }
        
        report_summary = f"""
        🔒 SECURITY INCIDENT REPORT
        
        Severity: {report['incident_severity']}
        Threat Level: {report['threat_level']}
        Actions Taken: {len(report['actions_taken'])} actions
        Status: {report['case_status']}
        
        Investigation: {report['investigation_results']}
        """
        
        return {
            "messages": [AIMessage(content=report_summary)],
            "case_status": "report_generated"
        }
    
    # Conditional edge functions
    def _should_investigate(self, state: InteractiveAgentState) -> Literal["investigate", "escalate"]:
        """Determine if automated investigation should proceed."""
        requires_investigation = state.get("requires_investigation", False)
        severity = state.get("incident_severity", "Medium")
        
        # Escalate Critical incidents immediately, investigate others if flagged
        if severity == "Critical":
            return "escalate"
        elif requires_investigation:
            return "investigate"
        else:
            return "escalate"
    
    def _determine_response_level(self, state: InteractiveAgentState) -> Literal["automated", "manual"]:
        """Determine if response can be automated or requires manual intervention."""
        threat_level = state.get("threat_level", "Medium")
        
        # Automate Low/Medium threats, escalate High/Critical
        if threat_level in ["Low", "Medium"]:
            return "automated"
        else:
            return "manual"

# Demo scenarios for testing in LangGraph Studio
def create_demo_scenarios():
    """Create sample incident scenarios for testing."""
    return [
        "Suspicious login attempt from unusual IP address 192.168.1.100",
        "Multiple failed authentication attempts detected for user admin",
        "Malware detected on workstation DESK-001, file quarantined",
        "Unusual network traffic to external domain malicious-site.com",
        "Privilege escalation attempt detected in Active Directory"
    ]

def main():
    """Main function for standalone testing."""
    print("🔒 LangGraph Studio Security Agent Demo")
    print("=" * 50)
    
    # Initialize agent
    agent = InteractiveSecurityAgent()
    
    # Test with a sample incident
    sample_incident = "Suspicious network activity: Multiple connections to unknown external IP 203.0.113.5"
    
    print(f"📝 Processing incident: {sample_incident}")
    print("-" * 50)
    
    # Create initial state
    initial_state = {
        "messages": [HumanMessage(content=sample_incident)],
        "incident_severity": "",
        "requires_investigation": False,
        "investigation_results": "",
        "threat_level": "",
        "actions_taken": [],
        "case_status": "new"
    }
    
    # Execute workflow
    try:
        final_state = agent.graph.invoke(initial_state)
        
        print("\n✅ Workflow completed successfully!")
        print(f"📊 Final Status: {final_state.get('case_status', 'unknown')}")
        print(f"🎯 Threat Level: {final_state.get('threat_level', 'unknown')}")
        print(f"⚡ Actions Taken: {len(final_state.get('actions_taken', []))}")
        
        # Print final message
        if final_state.get("messages"):
            final_message = final_state["messages"][-1].content
            print(f"\n📋 Final Report:\n{final_message}")
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        print(f"❌ Error: {e}")

# Export for LangGraph Studio
def get_graph():
    """Function to get the graph for LangGraph Studio."""
    agent = InteractiveSecurityAgent()
    return agent.graph

if __name__ == "__main__":
    main()