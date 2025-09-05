import os
import requests
from langchain_core.tools import tool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent

### When agent runs 

class CiscoFirewall:
    """
    Cisco Secure Firewall integration for automated threat response.
    Provides methods to block malicious IPs and manage firewall policies.
    """
    
    def __init__(self):
        # need to initialize with host from event based on ip 
        self.host = os.environ.get("CISCO_FIREWALL_HOST")
        self.token = os.environ.get("CISCO_FIREWALL_API_TOKEN")
        self.server_params = StdioServerParameters(
            command="python", 
            args=[ "scc_fw_mcp_server.py", "--oneshot" ], 
            env={ 
                "FIREWALL_BASE_URL": "https://api.us.security.cisco.com/", 
                "API_KEY": "eyJraWQiOiIwIiwidHlwIjoiSldUIiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOiIwIiwicm9sZXMiOlsiUk9MRV9TVVBFUl9BRE1JTiJdLCJpc3MiOiJpdGQiLCJjbHVzdGVySWQiOiI1Iiwic3ViamVjdFR5cGUiOiJ1c2VyIiwiY2xpZW50X2lkIjoiYXBpLWNsaWVudCIsInBhcmVudElkIjoiN2Y5Yzc2ZTUtODg4MC00ZTkwLWFjNTAtNGYyNzkzMTA4ZDQ4Iiwic2NvcGUiOlsidHJ1c3QiLCJyZWFkIiwiN2Y5Yzc2ZTUtODg4MC00ZTkwLWFjNTAtNGYyNzkzMTA4ZDQ4Iiwid3JpdGUiXSwiaWQiOiI3ZTRiNGQ3ZC1mZmM3LTQ3ZjAtOTc3Ny1iNjQxOTZlZDAzNTYiLCJleHAiOjM5MDMwNTE1NjgsInJlZ2lvbiI6InByb2QiLCJpYXQiOjE3NTU1Njc5ODEsImp0aSI6ImM3YmZkNTM4LTA1MzItNDU1ZS05NDZiLTNkMzExNDYwMGViYSJ9.XvrsrX0Jlp1gpWDew3xoz0BWaEeDHYSf8qeYsNcIXaNQGhUdhXR_fBeZqKZ9lgBHCg6Cf2mWDYVLnHWdH8ylDIr4nDdzVpA7x_4E0-pzxmUP-ldC6ASlqV69C6bJWuMhlV9AsdeWAY_iCvjSn-1trkdkjiiChyUNoH7ZoYaXby1o6YPncoAr2oU8rBZmst06L5EfblX2iAemQVvC4aFmr2mHiD6hTpIk69nHpMFqxqMZ3tvREAQYv4Bmy2G2n-eXBA8ETyUd6Dj4duo1QTz8Q7qBizNgfWSS2jmzxzzEbeT2vlDK7_F0-pMxGxIK6oyNRw3vA9q8HXQKbCxXURlrKg", 
            }
        )
    
    def block_ip(self, ip_address: str) -> dict:
        """
        Block a malicious IP address by adding it to a firewall rule.
        
        Args:
            ip_address: The IP address to block
            
        Returns:
            dict: Result of the blocking operation
        """
        if not self.host or not self.token:
            return {"error": "Cisco Firewall host or token is not configured"}
            
        try:
            # In a real implementation, this would create a blocking rule
            result = {
                "status": "success",
                "blocked_ip": ip_address,
                "action": "IP blocked via firewall rule",
                "timestamp": "2024-01-01T00:00:00Z"
            }
            return result
        except Exception as e:
            return {"error": f"Failed to block IP {ip_address}: {str(e)}"}
        

@tool
def get_firewall_policies():
    """
    Retrieves the list of access control policies from the Cisco Secure Firewall.
    """
    host = os.environ.get("CISCO_FIREWALL_HOST")
    token = os.environ.get("CISCO_FIREWALL_API_TOKEN")

    if not host or not token:
        return "Error: Cisco Firewall host or token is not configured in the environment."

    # Example endpoint, replace with the actual one for your device/version
    url = f"https://{host}/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/policy/accesspolicies"

    headers = {
        "X-auth-access-token": token,
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(url, headers=headers, verify=False) # In production, use verify=True with proper certs
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"An error occurred while fetching firewall policies: {e}"

@tool
def add_firewall_rule(policy_id: str, rule_name: str, source_ip: str, dest_ip: str, action: str = "ALLOW"):
    """
    Adds a new rule to a specific firewall policy.

    Args:
        policy_id: The ID of the policy to add the rule to.
        rule_name: The name for the new rule.
        source_ip: The source IP address or network object.
        dest_ip: The destination IP address or network object.
        action: The action for the rule (e.g., "ALLOW", "BLOCK").
    """
    # This is a placeholder for the actual implementation.
    # You would need to construct the correct API payload according to the
    # Cisco Secure Firewall API documentation.
    return f"Placeholder: A rule named '{rule_name}' would be added to policy '{policy_id}' to {action} traffic from {source_ip} to {dest_ip}."

async def main():
    client = CiscoFirewall()
    config = {"configurable": {"thread_id": 1234}}
    async with stdio_client(client.server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Check available tools
            tools = await load_mcp_tools(session)
            print("Available tools:", [tool.name for tool in tools])
            
