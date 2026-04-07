"""
LangGraph-based AI agent that wraps the three MCP-style travel tools.
Uses Claude claude-sonnet-4-20250514 via the Anthropic API.
"""

import os
import json
from typing import Annotated
from typing_extensions import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq

from app.services.member_service import get_member as _get_member
from app.services.partner_config import get_partner_config as _get_partner_config
from app.services.recommendation import generate_recommendations as _generate_recommendations


base_model = "openai/gpt-oss-120b"
api = os.getenv("GROQ_API_KEY")
# ─────────────────────────── TOOLS ────────────────────────────────────────────

@tool
def get_member_info(member_id: str) -> str:
    """
    Retrieve full member profile from the member data service.
    Returns member ID, name, loyalty tier (Silver/Gold/Platinum),
    travel history (last 5 bookings), and partner ID.
    Use this when the user asks about a member's profile, tier, or past trips.
    """
    try:
        data = _get_member(member_id)
        return json.dumps(data, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def get_partner_rules(partner_id: str) -> str:
    """
    Retrieve partner-specific configuration and business rules.
    Returns max recommendations cap (None = unlimited), excluded offer types
    (e.g. cruise), preferred categories, and commission tier.
    Use this when the user asks about partner constraints or configuration.
    """
    try:
        data = _get_partner_config(partner_id)
        return json.dumps(data, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


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
        member = _get_member(member_id)
        rules = _get_partner_config(member["partner_id"])
        recs = _generate_recommendations(member, rules)
        return json.dumps({
            "member_id": member_id,
            "member_name": member.get("name"),
            "loyalty_tier": member.get("loyalty_tier"),
            "partner_id": member.get("partner_id"),
            "partner_name": rules.get("partner_name"),
            "rules_applied": {
                "max_recommendations": rules.get("max_recommendations"),
                "excluded_types": rules.get("exclude_types"),
                "allow_cruise_offers": rules.get("allow_cruise_offers"),
            },
            "recommendations": recs,
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


TOOLS = [get_member_info, get_partner_rules, get_recommendations]

SYSTEM_PROMPT = """You are an AI Travel Concierge assistant for a loyalty travel platform.

You have access to three tools that connect to backend microservices:

1. **get_member_info(member_id)** — Fetches member profile: loyalty tier (Silver/Gold/Platinum), travel history, and partner ID.
2. **get_partner_rules(partner_id)** — Fetches partner-specific business rules: recommendation caps, excluded offer types (e.g., no cruises), preferred categories.
3. **get_recommendations(member_id)** — Generates personalized travel recommendations, automatically applying partner rules and loyalty tier boosts.

Guidelines:
- Always call tools when the user asks about a member, partner, or recommendations — never guess data.
- Call only the tool needed to answer the user's question. Each based on member info partner rules and recommendations.
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