# my_langgraph_app.py
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, List, Annotated
import operator
import uuid  # Import uuid for generating unique thread_ids


# Define your state
class AgentState(TypedDict):
    """
    Represents the state of our graph.
    Attributes:
        messages: A list of messages in the conversation.
    """
    messages: Annotated[List[str], operator.add]  # Accumulate messages


# Define your nodes (agents, tools, etc.)
def call_llm(state: AgentState):
    """Simulates an LLM call based on the last message."""
    last_message = state["messages"][-1] if state["messages"] else ""
    print(f"LLM Node: Processing: '{last_message}'")

    # Simple logic to decide if we need a tool or if we're done
    if "tool_needed" in last_message.lower():
        response = "Okay, I'll use a tool."
    elif "hello" in last_message.lower():
        response = "Hello there! How can I help?"
    else:
        response = "I've processed your message."

    return {"messages": [response]}


def tool_node(state: AgentState):
    """Simulates a tool usage."""
    last_message = state["messages"][-1] if state["messages"] else ""
    print(f"Tool Node: Performing action based on: '{last_message}'")
    return {"messages": ["Tool action completed. What next?"]}


# Build the graph
workflow = StateGraph(AgentState)
workflow.add_node("llm", call_llm)
workflow.add_node("tool", tool_node)

# Set the entry point
workflow.set_entry_point("llm")

# Define conditional edges
workflow.add_conditional_edges(
    "llm",
    # Decide next step based on the LLM's response
    lambda state: "tool" if "tool" in state["messages"][-1].lower() else END,
    {
        "tool": "tool",  # If the lambda returns "tool", go to the 'tool' node
        END: END  # If the lambda returns END (directly), end the graph
    }
)

# After the tool, we go back to the LLM or end
workflow.add_edge("tool", "llm")  # After tool, go back to LLM to continue conversation

# Compile the graph
# Using MemorySaver for simplicity; for real apps, use persistent storage (e.g., Redis)
langgraph_app = workflow.compile(checkpointer=MemorySaver())

if __name__ == "__main__":
    print("Testing LangGraph locally from my_langgraph_app.py...")

    # --- Example 1: A simple conversation thread ---
    print("\n--- Conversation Thread 1 ---")
    # Generate a unique thread ID for this conversation
    thread_id_1 = str(uuid.uuid4())

    inputs_1 = {"messages": ["Hello LangGraph!"]}
    # Pass the thread_config as the second argument to .stream()
    for s in langgraph_app.stream(inputs_1, {"configurable": {"thread_id": thread_id_1}}):
        print(s)

    # Continue the same conversation thread
    inputs_2 = {"messages": ["How are you today?"]}
    for s in langgraph_app.stream(inputs_2, {"configurable": {"thread_id": thread_id_1}}):
        print(s)

    # --- Example 2: Another conversation thread, possibly triggering a tool ---
    print("\n--- Conversation Thread 2 (with tool trigger) ---")
    thread_id_2 = str(uuid.uuid4())  # A new unique ID for a different conversation

    inputs_3 = {"messages": ["I need some data, tool_needed"]}
    for s in langgraph_app.stream(inputs_3, {"configurable": {"thread_id": thread_id_2}}):
        print(s)

    # Continue this conversation after the tool
    inputs_4 = {"messages": ["Thank you for using the tool."]}
    for s in langgraph_app.stream(inputs_4, {"configurable": {"thread_id": thread_id_2}}):
        print(s)

    # You can also get the state of a specific thread
    print(f"\n--- Current state of Thread 1 ({thread_id_1}) ---")
    state_thread_1 = langgraph_app.get_state({"configurable": {"thread_id": thread_id_1}})
    print(state_thread_1.values)  # .values gives you the actual AgentState content

    print(f"\n--- Current state of Thread 2 ({thread_id_2}) ---")
    state_thread_2 = langgraph_app.get_state({"configurable": {"thread_id": thread_id_2}})
    print(state_thread_2.values)