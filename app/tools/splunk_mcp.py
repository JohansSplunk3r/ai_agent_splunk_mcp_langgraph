import os
from dotenv import load_dotenv

load_dotenv()

"""Call Out to MCP Server 
1. df_baseline_traffic
2. ss_basleine_trafficc

Await: create time limit, if it persists over the hardcoded response"""

# class SplunkMCP:
#     def __init__(self):
#         self.api_key = os.getenv("SPLUNK_MCP_API_KEY")
#         self.base_url = os.getenv("SPLUNK_MCP_BASE_URL")

#     def search(self, query):
#         # Placeholder for Splunk MCP search logic
#         print(f"Searching Splunk MCP with query: {query}")
#         return {"result": "Splunk MCP search result"}

# TODO: Update the MCP connector to handle all tooling and add in prompt
""" 
Prompt 1:  The MLTK model df_baseline_traffic was created in my Splunk environment. Can you please find and apply this model on data in the test_summary_firewall index? 
Prompt 2: The MLTK model df_baseline_traffic was created in my Splunk environment. Can you please find and apply this model on data in the test_summary_firewall index?
When developing the SPL query, use the last 24 hours for the apply command and head value of 20, retry until you get a 200 response back.
Once you get a response stop all retries/attempts, send the information back to be processed by the user.
"""