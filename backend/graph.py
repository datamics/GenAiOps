from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage
try:
    from config import SYSTEM_PROMPT
except ModuleNotFoundError:
    from backend.config import SYSTEM_PROMPT
try:
    from llm import get_llm
except ModuleNotFoundError:
    from backend.llm import get_llm
try:
    from tools import get_tools
except ModuleNotFoundError:
    from backend.tools import get_tools

# Initialize components once
tools = get_tools()
llm = get_llm()
llm_with_tools = llm.bind_tools(tools)


def reasoner_node(state: MessagesState):
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def check_for_tools(state: MessagesState) -> str:
    """
    Checks the last message in the state for tool calls.
    """
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return "end"


def build_graph():
    tool_node = ToolNode(tools)

    graph = StateGraph(MessagesState)
    graph.add_node("reasoner", reasoner_node)
    graph.add_node("tool", tool_node)

    graph.add_edge(START, "reasoner")
    graph.add_conditional_edges(
        "reasoner",
        check_for_tools,
        {
            "tools": "tool",
            "end": END
        }
    )
    graph.add_edge("tool", "reasoner")

    return graph.compile()


# Create a singleton instance of the app
app = build_graph()
