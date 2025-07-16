# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Import your compiled LangGraph application
# Make sure my_langgraph_app.py is in the same directory or accessible via PYTHONPATH
try:
    from my_langgraph_app import langgraph_app # Assuming your compiled app is named 'langgraph_app'
except ImportError as e:
    raise RuntimeError(f"Could not import langgraph_app from my_langgraph_app.py: {e}. "
                       "Ensure 'my_langgraph_app.py' exists and 'langgraph_app' is defined.")


app = FastAPI(
    title="LangGraph FastAPI Integrator",
    description="API to interact with a LangGraph application.",
    version="1.0.0",
)

# Pydantic model for the input to your LangGraph
# This matches the 'messages' field in your AgentState
class LangGraphInvokeRequest(BaseModel):
    messages: List[str]
    # Optional: If you want to support specific thread IDs from the API caller
    thread_id: Optional[str] = None

@app.get("/")
async def read_root():
    """
    Root endpoint to confirm the API is running.
    """
    return {"message": "LangGraph FastAPI service is up and running!"}

@app.post("/invoke_langgraph/")
async def invoke_langgraph_endpoint(request: LangGraphInvokeRequest):
    """
    Invokes the LangGraph application with the provided messages.

    Args:
        request (LangGraphInvokeRequest): The request body containing messages
                                         and an optional thread_id.

    Returns:
        Dict[str, Any]: A dictionary containing the status and the output stream from LangGraph.
    """
    try:
        # Prepare the input for LangGraph based on your AgentState definition
        # Assuming AgentState has a 'messages' key that expects a List[str]
        langgraph_input = {"messages": request.messages}

        # Prepare the thread_config for LangGraph.
        # If no thread_id is provided, you might want to generate one or use a default.
        # For simplicity, we'll use a hardcoded one if not provided.
        # In a real app, generate a UUID or use session IDs.
        thread_id = request.thread_id if request.thread_id else "default_langgraph_thread"
        thread_config = {"configurable": {"thread_id": thread_id}}

        # Stream the results from LangGraph
        output_stream = []
        # The .stream() method returns an iterable; we collect all results
        # You could also consider using FastAPI StreamingResponse for very long outputs
        for s in langgraph_app.stream(langgraph_input, thread_config):
            output_stream.append(s)

        return {
            "status": "success",
            "thread_id": thread_id,
            "output": output_stream
        }
    except Exception as e:
        # Log the error for debugging purposes (e.g., using Python's logging module)
        print(f"Error invoking LangGraph: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# This block allows you to run the FastAPI app directly using 'python main.py'
if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server...")
    print("Access API documentation at http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)