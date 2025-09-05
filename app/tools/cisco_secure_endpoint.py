import asyncio
import os
from dotenv import load_dotenv
import requests 

load_dotenv()

class CiscoSecureEndpointStatus: 
    "Object to track status of endpoint isolation"
    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.is_isolated = False
        self.unlock_code = None
        self.status = "not_isolated"

class CiscoSecureEndpoint:
    """
    Methods to emulate call to Cisco Secure Endpoint API call. 
    Need to have API key and baseURL, can hard code these in for now. 

    """
    
    def __init__(self):
        self.api_key = os.getenv("CISCO_SECURE_ENDPOINT_API_KEY", "test_key")
        self.base_url = os.getenv("CISCO_SECURE_ENDPOINT_BASE_URL", "https://api.amp.cisco.com/v1/computers/")
        self.status_objects = {} 
        
    def get_isolation_status(self, connector_guid):
        """
        Returns isolation status of the endpoint 

        Args:
            connector_guid (_type_): device IP address
        """
        status_obj = self.status_objects.get(connector_guid)
        if not status_obj:
            status_obj = CiscoSecureEndpointStatus(connector_guid)
            self.status_objects[connector_guid] = status_obj
        
        if status_obj.status == "pending_start": 
            status_obj.status = "isolated"
            return {
                "version": "v1.2.0",
                "metadata": {
                    "links": {
                    "self": f"{self.base_url}/{connector_guid}/isolation"
                    }
                },
                "data": {
                    "available": True,
                    "status": "isolated",
                    "unlock_code": "unlockme",
                    "ccms_message_guid": "0e334b24-a9e7-f3db-4197-4eb0057721bf",
                    "ccms_job_guid": "1c12f2e2-9300-4891-ba40-ad94fd675418"
                }
            }
            
        return {
            "data": {
                "available": True,
                "status": status_obj.status,
                "unlock_code": status_obj.unlock_code,
                "comment": "Isolation status checked"
            }
        }
        
        
    def isolate_endpoint(self, connector_guid):
        # Emulate PUT request for isolation
        status_obj = self.status_objects.get(connector_guid)
        if not status_obj:
            status_obj = CiscoSecureEndpointStatus(connector_guid)
            self.status_objects[connector_guid] = status_obj
        status_obj.is_isolated = True
        status_obj.status = "pending_start"
        status_obj.unlock_code = "unlockme"
        response_status_code = 200  
        return {
            "version": "v1.2.0",
            "metadata": {
                "links": {
                    "self": f"{self.base_url}/{connector_guid}/isolation"
                }
            },
            "data": {
                "available": True,
                "status": status_obj.status,
                "unlock_code": status_obj.unlock_code,
                "comment": f"Isolation on ip address {status_obj.ip_address} in progress"
            }
        }
        
async def main():
    """Test the Cisco Secure Endpoint replicated connection"""
    base_url = "https://api.apjc.amp.cisco.com/v1/computers/"
    api_key = "api_key"
    ip_address = "10.25.6.6"
    cisco_endpoint = CiscoSecureEndpoint()
    cisco_endpoint.get_isolation_status(ip_address)
    isolate_response = cisco_endpoint.isolate_endpoint(ip_address)
    print(f"Isolation response: {isolate_response}")
    isolated_status = cisco_endpoint.get_isolation_status(ip_address)
    print(f"Final isolation response: {isolated_status}")
    
if __name__ == "__main__":
    asyncio.run(main())
