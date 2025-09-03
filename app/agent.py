from typing import Literal

from langchain_core.messages import ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from app.state import AgentState
from app.tools.splunk_mcp import SplunkMCP
from app.tools.cisco_secure_endpoint import CiscoSecureEndpoint
from app.tools.splunk_soar import SplunkSOAR
from app.tools.database import Database

# 1. Initialize the tools
splunk_mcp = SplunkMCP()
cisco_secure_endpoint = CiscoSecureEndpoint()
splunk_soar = SplunkSOAR()
database = Database()

# 2. Define the model
# Note: The 'model' is not directly used in this linear, non-agentic workflow.
# However, it is good practice to define it for future extensions or if you want
# to add AI-driven decision-making back into the flow.
model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)

# 3. Define the nodes for the graph
def splunk_mcp_node(state: AgentState):
    """
    Searches Splunk MCP based on the initial event data.
    """
    print("Executing Splunk MCP search...")
    event_data = state["messages"][-1].content
    result = splunk_mcp.search(event_data)
    return {"messages": [ToolMessage(content=str(result), name="splunk_mcp_search")]}

def cisco_secure_endpoint_node(state: AgentState):
    """
    Isolates a device in Cisco Secure Endpoint based on the output of the Splunk MCP search.
    """
    print("Executing Cisco Secure Endpoint action...")
    splunk_result = state["messages"][-1].content
    # Assuming the Splunk result contains the device_ip to isolate
    device_ip = "1.2.3.4" # Placeholder
    result = cisco_secure_endpoint.isolate_endpoint(device_ip)
    return {"messages": [ToolMessage(content=str(result), name="cisco_isolate_endpoint")]}

def splunk_soar_node(state: AgentState):
    """
    Creates a case in Splunk SOAR with the collected information.
    """
    print("Executing Splunk SOAR action...")
    cisco_result = state["messages"][-1].content
    result = splunk_soar.create_case(cisco_result)
    return {"messages": [ToolMessage(content=str(result), name="splunk_soar_create_case")]}

def database_node(state: AgentState):
    """
    Saves the historical context of the workflow to a database.
    """
    print("Saving historical context to the database...")
    # We can concatenate the content of all messages to form the historical context
    historical_context = "\n".join([msg.content for msg in state["messages"]])
    result = database.save_context(historical_context)
    return {"messages": [ToolMessage(content=str(result), name="save_context_to_db")]}

# 4. Define the graph
workflow = StateGraph(AgentState)

# Add the nodes
workflow.add_node("splunk_mcp", splunk_mcp_node)
workflow.add_node("cisco_secure_endpoint", cisco_secure_endpoint_node)
workflow.add_node("splunk_soar", splunk_soar_node)
workflow.add_node("database", database_node)

# Set the entrypoint
workflow.set_entry_point("splunk_mcp")

# Add the edges to define the linear flow
workflow.add_edge("splunk_mcp", "cisco_secure_endpoint")
workflow.add_edge("cisco_secure_endpoint", "splunk_soar")
workflow.add_edge("splunk_soar", "database")
workflow.add_edge("database", END)

# Compile the graph
graph = workflow.compile()