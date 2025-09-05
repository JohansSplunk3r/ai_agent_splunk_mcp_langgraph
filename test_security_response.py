#!/usr/bin/env python3
"""
Comprehensive Security Incident Response Test

Tests the complete workflow with the specific prompt:
"You're a Security Incident Response agent. Use the tools available to you to investigate 
an alert and isolate an endpoint. Use the tools available to you and report each step you 
take, the result and the raw response back."
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.insert(0, '/Users/johans/Documents/GitHub/ai_agent_splunk_mcp_langgraph')

load_dotenv()

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_individual_tools():
    """Test each tool individually to identify what works and what breaks."""
    print("🔧 Testing Individual Tools")
    print("="*50)
    
    results = {
        "splunk_mcp": {"status": "unknown", "error": None, "response": None},
        "cisco_firewall": {"status": "unknown", "error": None, "response": None},
        "cisco_endpoint": {"status": "unknown", "error": None, "response": None},
        "splunk_soar": {"status": "unknown", "error": None, "response": None},
        "database": {"status": "unknown", "error": None, "response": None}
    }
    
    # Test 1: Splunk MCP Client
    print("\n📡 Testing Splunk MCP Client...")
    try:
        from app.tools.splunk_mcp import SplunkMCPClient
        client = SplunkMCPClient()
        
        # Test basic query
        response = await client.run_splunk_query("| stats count", row_limit=1)
        print(f"✅ Splunk MCP: SUCCESS")
        print(f"   Raw response (first 100 chars): {response[:100]}...")
        results["splunk_mcp"]["status"] = "working"
        results["splunk_mcp"]["response"] = response[:200]
        
        # Test index search  
        index_response = await client.get_indexes(row_limit=5)
        print(f"✅ Splunk Indexes: SUCCESS")
        
    except Exception as e:
        print(f"❌ Splunk MCP: FAILED - {e}")
        results["splunk_mcp"]["status"] = "broken"
        results["splunk_mcp"]["error"] = str(e)
    
    # Test 2: Cisco Firewall
    print("\n🚫 Testing Cisco Firewall...")
    try:
        from app.tools.cisco_firewall import CiscoFirewall
        firewall = CiscoFirewall()
        
        response = firewall.block_ip("192.168.1.100")
        print(f"✅ Cisco Firewall: SUCCESS (Mock)")
        print(f"   Response: {response}")
        results["cisco_firewall"]["status"] = "mock_working"
        results["cisco_firewall"]["response"] = str(response)
        
    except Exception as e:
        print(f"❌ Cisco Firewall: FAILED - {e}")
        results["cisco_firewall"]["status"] = "broken"
        results["cisco_firewall"]["error"] = str(e)
    
    # Test 3: Cisco Secure Endpoint
    print("\n🔒 Testing Cisco Secure Endpoint...")
    try:
        from app.tools.cisco_secure_endpoint import CiscoSecureEndpoint
        endpoint = CiscoSecureEndpoint()
        
        response = endpoint.isolate_endpoint("192.168.1.100")
        print(f"✅ Cisco Endpoint: SUCCESS (Mock)")
        print(f"   Response: {response}")
        results["cisco_endpoint"]["status"] = "mock_working"
        results["cisco_endpoint"]["response"] = str(response)
        
    except Exception as e:
        print(f"❌ Cisco Endpoint: FAILED - {e}")
        results["cisco_endpoint"]["status"] = "broken"
        results["cisco_endpoint"]["error"] = str(e)
    
    # Test 4: Splunk SOAR
    print("\n📋 Testing Splunk SOAR...")
    try:
        from app.tools.splunk_soar import SplunkSOAR
        soar = SplunkSOAR()
        
        response = soar.create_case({"test": "incident"})
        print(f"✅ Splunk SOAR: SUCCESS (Mock)")
        print(f"   Response: {response}")
        results["splunk_soar"]["status"] = "mock_working"
        results["splunk_soar"]["response"] = str(response)
        
    except Exception as e:
        print(f"❌ Splunk SOAR: FAILED - {e}")
        results["splunk_soar"]["status"] = "broken"
        results["splunk_soar"]["error"] = str(e)
    
    # Test 5: Database
    print("\n💾 Testing Database...")
    try:
        from app.tools.database import Database
        db = Database()
        
        response = db.save_context({"test": "context"})
        print(f"✅ Database: SUCCESS (Mock)")
        print(f"   Response: {response}")
        results["database"]["status"] = "mock_working"
        results["database"]["response"] = str(response)
        
    except Exception as e:
        print(f"❌ Database: FAILED - {e}")
        results["database"]["status"] = "broken"
        results["database"]["error"] = str(e)
    
    return results

async def test_full_agent_workflow():
    """Test the complete SecurityIncidentAgent workflow."""
    print("\n\n🤖 Testing Full Agent Workflow")
    print("="*50)
    
    security_prompt = """
    You're a Security Incident Response agent. Use the tools available to you to investigate 
    an alert and isolate an endpoint. Use the tools available to you and report each step you 
    take, the result and the raw response back.
    
    INCIDENT ALERT:
    - Source IP: 192.168.1.100
    - Destination: malicious-domain.com
    - Alert Type: Suspicious network communication
    - Timestamp: 2025-09-05T02:00:00Z
    - Severity: HIGH
    """
    
    try:
        from app.agent import SecurityIncidentAgent
        
        print("🚨 Initializing SecurityIncidentAgent...")
        agent = SecurityIncidentAgent()
        print("✅ Agent initialized successfully")
        
        print(f"\n📝 Running incident response with prompt:")
        print("-" * 30)
        print(security_prompt)
        print("-" * 30)
        
        # Execute the workflow
        result = agent.run_incident_response(security_prompt)
        
        print(f"\n📊 Workflow Results:")
        print(f"Status: {result.get('workflow_status', 'unknown')}")
        
        if result.get('error'):
            print(f"❌ Error: {result['error']}")
            return {"status": "failed", "error": result['error']}
        else:
            print("✅ Workflow completed successfully!")
            
            # Print detailed results
            if 'messages' in result:
                print(f"\n💬 Messages exchanged: {len(result['messages'])}")
                for i, msg in enumerate(result['messages'][-3:]):  # Last 3 messages
                    print(f"   {i+1}. {msg.__class__.__name__}: {str(msg.content)[:100]}...")
            
            # Print other results
            for key, value in result.items():
                if key not in ['messages', 'workflow_status', 'error']:
                    print(f"   {key}: {value}")
            
            return {"status": "success", "result": result}
    
    except Exception as e:
        print(f"❌ Agent workflow FAILED: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "failed", "error": str(e)}

async def test_react_agent():
    """Test the ReACT agent separately."""
    print("\n\n🎭 Testing ReACT Agent (SplunkMCPAgent)")
    print("="*50)
    
    try:
        # Import the SplunkMCPAgent instead of SecurityIncidentAgent
        from app.agent import SplunkMCPAgent
        
        print("🤖 Initializing SplunkMCPAgent...")
        agent = SplunkMCPAgent()
        print("✅ ReACT Agent initialized successfully")
        
        security_prompt = """
        You're a Security Incident Response agent. Use the tools available to you to investigate 
        an alert and isolate an endpoint. Use the tools available to you and report each step you 
        take, the result and the raw response back.
        
        INCIDENT: Suspicious network activity from IP 192.168.1.100 to malicious-domain.com
        """
        
        print(f"\n📝 Running ReACT agent with security prompt...")
        result = agent.run(security_prompt)
        
        if "error" in result:
            print(f"❌ ReACT Agent Error: {result['error']}")
            return {"status": "failed", "error": result['error']}
        else:
            print("✅ ReACT Agent completed successfully!")
            print(f"📊 Messages: {len(result.get('messages', []))}")
            
            # Print conversation flow
            for i, message in enumerate(result.get("messages", [])[:5]):  # First 5 messages
                print(f"\n--- Message {i+1} ---")
                print(f"Type: {message.__class__.__name__}")
                
                if hasattr(message, 'content'):
                    if isinstance(message.content, list):
                        # Handle tool use messages
                        for j, content_block in enumerate(message.content):
                            if isinstance(content_block, dict):
                                if content_block.get('type') == 'text':
                                    print(f"Text: {content_block.get('text', '')[:200]}...")
                                elif content_block.get('type') == 'tool_use':
                                    print(f"🔧 Tool Call: {content_block.get('name', 'unknown')}")
                                    print(f"   Input: {content_block.get('input', {})}")
                    else:
                        print(f"Content: {str(message.content)[:200]}...")
            
            return {"status": "success", "result": result}
    
    except Exception as e:
        print(f"❌ ReACT Agent FAILED: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "failed", "error": str(e)}

async def main():
    """Main test function."""
    print("🚨 COMPREHENSIVE SECURITY INCIDENT RESPONSE TEST")
    print("="*60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Python: {sys.version}")
    
    # Test individual tools first
    tool_results = await test_individual_tools()
    
    # Test full agent workflow
    agent_results = await test_full_agent_workflow()
    
    # Test ReACT agent separately
    react_results = await test_react_agent()
    
    # Summary Report
    print("\n\n📋 FINAL TEST REPORT")
    print("="*50)
    
    print("\n🔧 Tool Status:")
    for tool, result in tool_results.items():
        status_icon = "✅" if result["status"] in ["working", "mock_working"] else "❌"
        print(f"   {status_icon} {tool}: {result['status']}")
        if result["error"]:
            print(f"      Error: {result['error']}")
    
    print(f"\n🤖 Agent Status:")
    agent_icon = "✅" if agent_results["status"] == "success" else "❌"
    print(f"   {agent_icon} SecurityIncidentAgent: {agent_results['status']}")
    
    react_icon = "✅" if react_results["status"] == "success" else "❌"
    print(f"   {react_icon} SplunkMCPAgent (ReACT): {react_results['status']}")
    
    # Recommendations
    print(f"\n🎯 Issues Found:")
    issues = []
    
    for tool, result in tool_results.items():
        if result["status"] == "broken":
            issues.append(f"   • {tool}: {result['error']}")
    
    if agent_results["status"] == "failed":
        issues.append(f"   • SecurityIncidentAgent: {agent_results.get('error', 'Unknown error')}")
        
    if react_results["status"] == "failed":
        issues.append(f"   • SplunkMCPAgent: {react_results.get('error', 'Unknown error')}")
    
    if issues:
        for issue in issues:
            print(issue)
    else:
        print("   🎉 No critical issues found!")
    
    print(f"\n✅ Test completed at {datetime.now().isoformat()}")

if __name__ == "__main__":
    asyncio.run(main())