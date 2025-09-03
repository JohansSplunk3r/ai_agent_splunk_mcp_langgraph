import os
import requests
from langchain_core.tools import tool
from typing import Literal, Dict, Any

@tool
def call_node_api(endpoint: str, method: Literal["GET", "POST", "PUT", "DELETE"] = "GET", payload: Dict[str, Any] = None):
    """
    Makes an API call to a specified endpoint of the Node.js service.

    Args:
        endpoint: The API endpoint to call (e.g., "/users", "/products/123").
        method: The HTTP method to use (GET, POST, PUT, DELETE).
        payload: A dictionary representing the JSON payload for POST or PUT requests.

    Returns:
        A string containing the JSON response from the API or an error message.
    """
    base_url = os.environ.get("NODE_API_BASE_URL")
    if not base_url:
        return "Error: NODE_API_BASE_URL is not set in the environment."

    url = f"{base_url}{endpoint}"
    
    try:
        headers = {"Content-Type": "application/json"}
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=payload, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=payload, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            return f"Error: Unsupported HTTP method '{method}'."

        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.json()

    except requests.exceptions.RequestException as e:
        return f"An error occurred during the API call: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# Example of how to use the tool directly
if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    # Assumes a running Node.js API at the base URL defined in .env
    # Example: Get a list of users
    # print(call_node_api.invoke({"endpoint": "/users"}))
    
    # Example: Create a new user
    # new_user = {"name": "John Doe", "email": "john.doe@example.com"}
    # print(call_node_api.invoke({"endpoint": "/users", "method": "POST", "payload": new_user}))
    print("Please run this tool from within the agent or by uncommenting examples.")
