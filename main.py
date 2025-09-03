"""
LangGraph Agent Script for Splunk Enterprise Security Integration

This script processes Splunk Enterprise Security alerts using a LangGraph agent.
It accepts Splunk event data as a command-line argument and processes it through
the configured agent workflow.
"""

import os
import sys
import json
import logging
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

try:
   from app.agent import SecurityIncidentAgent
   agent = SecurityIncidentAgent()
   graph = agent.graph
except ImportError as e:
   print(f"Error importing agent: {e}")
   print("Please ensure the 'app.agent' module is available and properly configured.")
   sys.exit(1)
# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_environment() -> bool:
    """
    Validate that required environment variables are set.
    
    Returns:
        bool: True if all required environment variables are set, False otherwise.
    """
    required_vars = ["GOOGLE_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set them in your .env file.")
        return False
    
    return True


def validate_json_input(json_string: str) -> bool:
    """
    Validate that the input string is valid JSON.
    
    Args:
        json_string (str): The JSON string to validate.
        
    Returns:
        bool: True if valid JSON, False otherwise.
    """
    try:
        json.loads(json_string)
        return True
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON input: {e}")
        return False


def process_splunk_event(splunk_event_json: str) -> None:
    """
    Process a Splunk event through the LangGraph agent.
    
    Args:
        splunk_event_json (str): JSON string containing the Splunk event data.
    """
    # Validate JSON input
    if not validate_json_input(splunk_event_json):
        raise ValueError("Invalid JSON format in Splunk event data")
    
    # Prepare input for the graph
    inputs = {"messages": [HumanMessage(content=splunk_event_json)]}
    
    logger.info("Starting agent workflow...")
    
    try:
        # Process the event through the graph
        step_count = 0
        for output in graph.stream(inputs):
            step_count += 1
            
            # Print the output of each step
            for key, value in output.items():
                logger.info(f"Step {step_count}: {key}")
                
                # Safe access to messages
                if isinstance(value, dict) and 'messages' in value:
                    messages = value['messages']
                    if messages and len(messages) > 0:
                        content = messages[-1].content
                        print(f"Output: {content}")
                    else:
                        print("Output: No messages found")
                else:
                    print(f"Output: {value}")
                
                print("---")
        
        logger.info(f"Agent workflow finished successfully after {step_count} steps.")
        
    except Exception as e:
        logger.error(f"Error during agent workflow execution: {e}")
        raise


def main() -> None:
    """
    Main function to run the LangGraph agent.
    
    This script is triggered by a Splunk Enterprise Security alert.
    It takes the Splunk event data as a command-line argument.
    """
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python main.py <splunk_event_json>")
        print("\nExample:")
        print('python main.py \'{"event_id": "12345", "severity": "high", "description": "Suspicious activity detected"}\'')
        sys.exit(1)
    
    # Validate environment
    if not validate_environment():
        sys.exit(1)
    
    splunk_event_json = sys.argv[1]
    
    try:
        process_splunk_event(splunk_event_json)
        
    except ValueError as e:
        logger.error(f"Input validation error: {e}")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Error processing Splunk event: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()