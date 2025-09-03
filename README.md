# LangGraph Agent Scaffolding

This project provides a basic scaffolding for a LangGraph-based AI agent designed to connect to Splunk, a Node.js API, and the Cisco Secure Firewall API.

## Project Structure

```
langgraph_agent/
├── app/
│   ├── __init__.py
│   ├── agent.py             # Defines the LangGraph graph, state, and nodes
│   ├── state.py             # Defines the AgentState for the graph
│   └── tools/
│       ├── __init__.py
│       ├── splunk.py          # Splunk tool/connector
│       ├── node_api.py        # Generic Node API tool/connector
│       └── cisco_firewall.py  # Cisco Secure Firewall tool/connector
├── main.py                  # Main entry point to run the application
├── requirements.txt         # Dependencies
└── .env.example             # Environment variable template
```

## Setup Instructions

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Environment Variables:**
    Copy the example environment file and fill in your credentials.
    ```bash
    cp .env.example .env
    ```
    Now, edit the `.env` file with your specific API keys, tokens, and hostnames.

3.  **Run the Agent:**
    ```bash
    python main.py
    ```
