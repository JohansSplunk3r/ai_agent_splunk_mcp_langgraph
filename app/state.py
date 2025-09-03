from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

# The AgentState is a TypedDict that defines the structure of the state that will be passed around the graph.
# `add_messages` is a special function that ensures new messages are appended to the list of existing messages.
class AgentState(TypedDict):
    """
    Represents the state of our agent.

    Attributes:
        messages: A list of messages that have been exchanged between the user and the agent.
    """
    messages: Annotated[list[BaseMessage], add_messages]
