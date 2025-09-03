import os
import splunklib.client as client
import splunklib.results as results
from langchain_core.tools import tool

@tool
def search_splunk(query: str, earliest_time: str = "-24h", latest_time: str = "now"):
    """
    Executes a search query on the Splunk MCP Server.

    Args:
        query: The Splunk search query to execute.
        earliest_time: The earliest time for the search (e.g., "-24h", "-7d").
        latest_time: The latest time for the search (e.g., "now").

    Returns:
        A string containing the search results or an error message.
    """
    try:
        host = os.environ["SPLUNK_HOST"]
        port = int(os.environ["SPLUNK_PORT"])
        username = os.environ["SPLUNK_USERNAME"]
        password = os.environ["SPLUNK_PASSWORD"]
        # token = os.environ.get("SPLUNK_TOKEN") # Alternative authentication

        # Connect to Splunk
        service = client.connect(
            host=host,
            port=port,
            username=username,
            password=password
        )

        # Define the search parameters
        kwargs_search = {
            "earliest_time": earliest_time,
            "latest_time": latest_time,
            "output_mode": "json"
        }

        # Execute the search
        job = service.jobs.create(f"search {query}", **kwargs_search)

        # Wait for the job to finish
        while not job.is_done():
            pass

        # Get the results
        reader = results.JSONResultsReader(job.results())
        result_list = [item for item in reader]
        
        if not result_list:
            return "No results found."
            
        return str(result_list)

    except Exception as e:
        return f"An error occurred while connecting to or searching Splunk: {e}"

# Example of how to use the tool directly
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    # Make sure to have a .env file with SPLUNK_* variables set
    # Example: search for all successful logins in the last hour
    print(search_splunk.invoke({"query": 'index=_internal sourcetype=splunkd "Audit"' , "earliest_time": "-1h"}))
