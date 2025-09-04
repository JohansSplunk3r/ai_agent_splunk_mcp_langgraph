from typing import Literal, Dict, Any, Optional
import logging
import asyncio
from langchain_core.messages import ToolMessage, HumanMessage, AIMessage, BaseMessage
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, create_react_agent
from app.state import AgentState
from app.tools.splunk_mcp import SplunkMCP
from app.tools.cisco_secure_endpoint import CiscoSecureEndpoint
from app.tools.cisco_firewall import CiscoFirewall
from app.tools.splunk_soar import SplunkSOAR
from app.tools.database import Database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityIncidentAgent:
    """
    AI-powered security incident response agent using LangGraph.
    Orchestrates automated response workflow across multiple security tools.
    """
    
    def __init__(self):
        # Initialize tools
        self.splunk_mcp = SplunkMCP()
        self.cisco_secure_endpoint = CiscoSecureEndpoint()
        self.cisco_firewall = CiscoFirewall()
        self.splunk_soar = SplunkSOAR()
        self.database = Database()
        
        # Initialize the LLM for decision making
        self.model = ChatAnthropic(
            model="claude-sonnet-4-20250514", 
            temperature=0.1,  # Low temperature for consistent responses
            max_tokens=2048
        )
        
        # Build the workflow graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build and compile the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_incident", self._analyze_incident_node)
        workflow.add_node("search_splunk", self._splunk_search_node)
        workflow.add_node("assess_threat", self._assess_threat_node)
        workflow.add_node("isolate_endpoint", self._cisco_isolate_node)
        workflow.add_node("block_firewall", self._cisco_firewall_node)
        workflow.add_node("create_soar_case", self._soar_case_node)
        workflow.add_node("save_context", self._database_node)
        workflow.add_node("human_review", self._human_review_node)
        
        # Set entry point
        workflow.set_entry_point("analyze_incident")
        
        # Define conditional routing
        workflow.add_conditional_edges(
            "analyze_incident",
            self._should_proceed_with_search,
            {
                "search": "search_splunk",
                "end": END
            }
        )
        
        workflow.add_edge("search_splunk", "assess_threat")
        
        workflow.add_conditional_edges(
            "assess_threat",
            self._should_isolate_endpoint,
            {
                "isolate": "isolate_endpoint",
                "soar_only": "create_soar_case",
                "review": "human_review"
            }
        )
        
        workflow.add_edge("isolate_endpoint", "block_firewall")
        workflow.add_edge("block_firewall", "create_soar_case")
        workflow.add_edge("create_soar_case", "save_context")
        workflow.add_edge("human_review", "save_context")
        workflow.add_edge("save_context", END)
        
        return workflow.compile()
    
    def _analyze_incident_node(self, state: AgentState) -> Dict[str, Any]:
        """Analyze the initial incident using AI to determine next steps."""
        logger.info("🔍 Analyzing security incident...")
        
        try:
            # Get the latest message (incident report)
            incident_data = state["messages"][-1].content if state["messages"] else ""
            
            # Use AI to analyze the incident
            analysis_prompt = f"""
            Analyze this security incident and determine if it requires immediate investigation:
            
            Incident Data: {incident_data}
            
            Please provide:
            1. Severity assessment (Low/Medium/High/Critical)
            2. Incident type classification
            3. Whether Splunk search is needed
            4. Key indicators to search for
            
            Respond in a structured format.
            """
            
            response = self.model.invoke([HumanMessage(content=analysis_prompt)])
            
            # Store analysis results in state
            state["analysis"] = {
                "ai_assessment": response.content,
                "timestamp": "2024-01-01T00:00:00Z",  # You'd use actual timestamp
                "requires_search": True  # This would be parsed from AI response
            }
            
            return {
                "messages": [
                    AIMessage(content=f"Incident Analysis Complete: {response.content}")
                ],
                "analysis": state["analysis"]
            }
            
        except Exception as e:
            logger.error(f"Error in incident analysis: {e}")
            return {
                "messages": [
                    ToolMessage(content=f"Analysis failed: {str(e)}", tool_call_id="analyze_incident")
                ],
                "error": str(e)
            }
    
    def _cisco_firewall_node(self, state: AgentState) -> Dict[str, Any]:
        """Block malicious IPs using Cisco Firewall."""
        logger.info("🚫 Blocking malicious IPs via firewall...")
        
        try:
            threat_assessment = state.get("threat_assessment", {})
            affected_ips = threat_assessment.get("affected_ips", [])
            
            blocking_results = []
            for ip in affected_ips:
                result = self.cisco_firewall.block_ip(ip)
                blocking_results.append({"ip": ip, "result": result})
            
            return {
                "messages": [
                    ToolMessage(
                        content=f"Firewall blocking completed for {len(affected_ips)} IPs",
                        tool_call_id="cisco_firewall"
                    )
                ],
                "firewall_results": blocking_results
            }
            
        except Exception as e:
            logger.error(f"Error in firewall blocking: {e}")
            return {
                "messages": [
                    ToolMessage(content=f"Firewall blocking failed: {str(e)}", tool_call_id="cisco_firewall_error")
                ],
                "error": str(e)
            }
    
    def _splunk_search_node(self, state: AgentState) -> Dict[str, Any]:
        """Execute Splunk MCP search based on incident analysis."""
        logger.info("🔎 Executing Splunk MCP search...")
        
        try:
            # Extract search criteria from analysis
            incident_data = state["messages"][-1].content
            analysis = state.get("analysis", {})
            
            # Perform Splunk search
            search_result = asyncio.run(self.splunk_mcp.search(incident_data))
            
            return {
                "messages": [
                    ToolMessage(content=str(search_result), tool_call_id="splunk_search")
                ],
                "splunk_results": search_result
            }
            
        except Exception as e:
            logger.error(f"Error in Splunk search: {e}")
            return {
                "messages": [
                    ToolMessage(content=f"Splunk search failed: {str(e)}", tool_call_id="splunk_search_error")
                ],
                "error": str(e)
            }
    
    def _assess_threat_node(self, state: AgentState) -> Dict[str, Any]:
        """Use AI to assess threat level based on Splunk results."""
        logger.info("⚠️ Assessing threat level...")
        
        try:
            splunk_data = state.get("splunk_results", "")
            
            assessment_prompt = f"""
            Based on this Splunk search data, assess the threat level and recommend actions:
            
            Splunk Results: {splunk_data}
            
            Determine:
            1. Threat severity (Low/Medium/High/Critical)
            2. Whether endpoint isolation is required
            3. Affected systems/IPs
            4. Recommended response actions
            
            Provide a clear recommendation: ISOLATE, MONITOR, or REVIEW
            """
            
            response = self.model.invoke([HumanMessage(content=assessment_prompt)])
            
            # Parse AI recommendation (in real implementation, you'd use structured output)
            recommendation = "isolate" if "ISOLATE" in response.content.upper() else "monitor"
            
            threat_assessment = {
                "ai_recommendation": response.content,
                "action": recommendation,
                "affected_ips": ["1.2.3.4"],  # Would be extracted from Splunk results
                "severity": "high"  # Would be parsed from AI response
            }
            
            return {
                "messages": [
                    AIMessage(content=f"Threat Assessment: {response.content}")
                ],
                "threat_assessment": threat_assessment
            }
            
        except Exception as e:
            logger.error(f"Error in threat assessment: {e}")
            return {
                "messages": [
                    ToolMessage(content=f"Threat assessment failed: {str(e)}", tool_call_id="assess_threat_error")
                ],
                "error": str(e)
            }
    
    def _cisco_isolate_node(self, state: AgentState) -> Dict[str, Any]:
        """Isolate endpoints using Cisco Secure Endpoint."""
        logger.info("🔒 Isolating compromised endpoints...")
        
        try:
            threat_assessment = state.get("threat_assessment", {})
            affected_ips = threat_assessment.get("affected_ips", [])
            
            isolation_results = []
            for ip in affected_ips:
                result = self.cisco_secure_endpoint.isolate_endpoint(ip)
                isolation_results.append({"ip": ip, "result": result})
            
            return {
                "messages": [
                    ToolMessage(
                        content=f"Endpoint isolation completed for {len(affected_ips)} devices",
                        tool_call_id="cisco_isolate"
                    )
                ],
                "isolation_results": isolation_results
            }
            
        except Exception as e:
            logger.error(f"Error in endpoint isolation: {e}")
            return {
                "messages": [
                    ToolMessage(content=f"Endpoint isolation failed: {str(e)}", tool_call_id="cisco_isolate_error")
                ],
                "error": str(e)
            }
    
    def _soar_case_node(self, state: AgentState) -> Dict[str, Any]:
        """Create SOAR case with all collected information."""
        logger.info("📋 Creating Splunk SOAR case...")
        
        try:
            # Compile case information from state
            case_data = {
                "analysis": state.get("analysis", {}),
                "splunk_results": state.get("splunk_results", ""),
                "threat_assessment": state.get("threat_assessment", {}),
                "isolation_results": state.get("isolation_results", []),
                "firewall_results": state.get("firewall_results", [])
            }
            
            case_result = self.splunk_soar.create_case(case_data)
            
            return {
                "messages": [
                    ToolMessage(content=f"SOAR case created: {case_result}", tool_call_id="soar_case")
                ],
                "soar_case_id": case_result.get("case_id") if isinstance(case_result, dict) else None
            }
            
        except Exception as e:
            logger.error(f"Error creating SOAR case: {e}")
            return {
                "messages": [
                    ToolMessage(content=f"SOAR case creation failed: {str(e)}", tool_call_id="soar_case_error")
                ],
                "error": str(e)
            }
    
    def _database_node(self, state: AgentState) -> Dict[str, Any]:
        """Save complete workflow context to database."""
        logger.info("💾 Saving workflow context to database...")
        
        try:
            # Compile complete historical context
            workflow_context = {
                "messages": [msg.content for msg in state["messages"]],
                "analysis": state.get("analysis", {}),
                "splunk_results": state.get("splunk_results", ""),
                "threat_assessment": state.get("threat_assessment", {}),
                "isolation_results": state.get("isolation_results", []),
                "firewall_results": state.get("firewall_results", []),
                "soar_case_id": state.get("soar_case_id"),
                "workflow_status": "completed"
            }
            
            save_result = self.database.save_context(workflow_context)
            
            return {
                "messages": [
                    ToolMessage(content=f"Workflow context saved: {save_result}", tool_call_id="save_context")
                ],
                "workflow_complete": True
            }
            
        except Exception as e:
            logger.error(f"Error saving context: {e}")
            return {
                "messages": [
                    ToolMessage(content=f"Context save failed: {str(e)}", tool_call_id="save_context_error")
                ],
                "error": str(e)
            }
    
    def _human_review_node(self, state: AgentState) -> Dict[str, Any]:
        """Flag incident for human review."""
        logger.info("👤 Flagging for human review...")
        
        return {
            "messages": [
                ToolMessage(content="Incident flagged for human analyst review", tool_call_id="human_review")
            ],
            "requires_human_review": True
        }
    
    # Conditional edge functions
    def _should_proceed_with_search(self, state: AgentState) -> Literal["search", "end"]:
        """Determine if Splunk search is needed based on analysis."""
        analysis = state.get("analysis", {})
        if analysis.get("requires_search", False):
            return "search"
        return "end"
    
    def _should_isolate_endpoint(self, state: AgentState) -> Literal["isolate", "soar_only", "review"]:
        """Determine next action based on threat assessment."""
        threat_assessment = state.get("threat_assessment", {})
        action = threat_assessment.get("action", "monitor")
        severity = threat_assessment.get("severity", "low")
        
        if action == "isolate" or severity == "critical":
            return "isolate"
        elif severity in ["high", "medium"]:
            return "soar_only"
        else:
            return "review"
    
    def run_incident_response(self, incident_data: str) -> Dict[str, Any]:
        """
        Execute the complete incident response workflow.
        
        Args:
            incident_data: Initial security incident information
            
        Returns:
            Complete workflow results
        """
        logger.info("🚨 Starting security incident response workflow...")
        
        # Initialize state
        initial_state = {
            "messages": [HumanMessage(content=incident_data)],
            "workflow_id": "incident_response_001"  # You'd generate unique IDs
        }
        
        # Execute the workflow
        try:
            final_state = self.graph.invoke(initial_state)
            logger.info("✅ Incident response workflow completed successfully")
            return final_state
            
        except Exception as e:
            logger.error(f"❌ Workflow execution failed: {e}")
            return {"error": str(e), "workflow_status": "failed"}

# Usage example
def main():
    """Example usage of the SecurityIncidentAgent."""
    agent = SecurityIncidentAgent()
    
    # Sample incident data
    incident_data = """
    Security Alert: Suspicious network activity detected
    Source IP: 192.168.1.100
    Destination: external-malicious-domain.com
    Alert Type: Potential malware communication
    Timestamp: 2024-01-01T12:00:00Z
    """
    
    # Run the incident response
    result = agent.run_incident_response(incident_data)
    
    print("Workflow Results:")
    print(f"Status: {result.get('workflow_status', 'unknown')}")
    if result.get('error'):
        print(f"Error: {result['error']}")
    else:
        print("Incident response completed successfully!")

if __name__ == "__main__":
    main()