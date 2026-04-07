"""
LangGraph-based AI agent that wraps the three MCP-style travel tools.
Uses Claude claude-sonnet-4-20250514 via the Anthropic API.
"""

import os
import json
from typing import Annotated
from typing_extensions import TypedDict
import requests
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq


base_model = "openai/gpt-oss-120b"
api = os.getenv("GROQ_API_KEY")
# ─────────────────────────── TOOLS ────────────────────────────────────────────

def call_mcp_tool(name, arguments):
    try:
        res = requests.post(
            "https://wanderops-backend.vercel.app/tools/call",
            json={"name": name, "arguments": arguments},
            timeout=10
        )
        res.raise_for_status()
        return res.json()
    except Exception as e:
        return {"error": str(e)}

@tool
def get_recommendations(member_id: str) -> str:
    """
    Generate personalized travel recommendations for a member.
    Automatically fetches the member's profile and their partner's rules,
    then applies loyalty tier boosts, partner exclusions (e.g. no cruises),
    and recommendation caps before returning a ranked list.
    Use this when the user wants travel suggestions for a specific member.
    """
    try:
        data = call_mcp_tool(
            "get_travel_recommendations",
            {"member_id": member_id}
        )
        return json.dumps({
            "member_id": data["member"]["member_id"],
            "member_name": data["member"]["name"],
            "loyalty_tier": data["member"]["loyalty_tier"],
            "partner_id": data["member"]["partner_id"],
            "partner_name": data["rules"]["partner_name"],
            "rules_applied": {
                "max_recommendations": data["rules"].get("max_recommendations"),
                "excluded_types": data["rules"].get("exclude_types"),
                "allow_cruise_offers": data["rules"].get("allow_cruise_offers"),
            },
            "recommendations": data["recommendations"],
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


TOOLS = [get_recommendations]

SYSTEM_PROMPT = """You are an AI Travel Concierge assistant for a loyalty travel platform.

You have access to one tool that connect to backend microservices:

1. **get_recommendations(member_id)** — Generates personalized travel recommendations, automatically applying partner rules and loyalty tier boosts.

Guidelines:
- Always call tools when the user asks about a member, partner, or recommendations — never guess data.
- If the member does not exist return an appropriate message stating the condition.
- After receiving tool results, summarize them in a friendly, concise, travel-agent style.
- Highlight loyalty tier perks, partner constraints, and why certain destinations were recommended.
- If a partner excludes cruise offers, proactively mention this to the user.
- Be warm, professional, and conversational."""


# ─────────────────────────── STATE ────────────────────────────────────────────

class State(TypedDict):
    messages: Annotated[list, add_messages]


# ─────────────────────────── BUILD GRAPH ──────────────────────────────────────

def build_agent():
    """Build and compile the LangGraph agent. Returns (graph, llm)."""
    llm = ChatGroq(
        api_key = api,
        model = base_model,
        temperature=0.3
    )
    llm_with_tools = llm.bind_tools(TOOLS)

    def chatbot(state: State):
        msgs = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        response = llm_with_tools.invoke(msgs)
        return {"messages": [response]}

    memory = MemorySaver()
    builder = StateGraph(State)

    builder.add_node("chatbot", chatbot)
    builder.add_node("tools", ToolNode(tools=TOOLS))

    builder.add_edge(START, "chatbot")
    builder.add_conditional_edges("chatbot", tools_condition, {"tools": "tools", "__end__": END})
    builder.add_edge("tools", "chatbot")

    graph = builder.compile(checkpointer=memory)
    return graph


# ─────────────────────────── PUBLIC API ───────────────────────────────────────

_graph = None

def get_graph():
    global _graph
    if _graph is None:
        _graph = build_agent()
    return _graph


def run_agent(user_input: str, thread_id: str = "default") -> str:
    """Invoke the agent with a user message. Maintains conversation memory per thread_id."""
    graph = get_graph()
    config = {"configurable": {"thread_id": thread_id}}
    result = graph.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        config=config,
    )
    return result["messages"][-1].content