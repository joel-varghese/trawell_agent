from fastapi import APIRouter
from app.models.schemas import ToolRequest
from app.services.member_service import get_member
from app.services.partner_config import get_partner_config
from app.services.recommendation import generate_recommendations

router = APIRouter()


@router.get("/tools")
def list_tools():
    return {
        "tools": [
            {
                "name": "get_travel_recommendations",
                "description": "Get personalized travel recommendations",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "member_id": {"type": "string"}
                    },
                    "required": ["member_id"]
                }
            }
        ]
    }


@router.post("/tools/call")
def call_tool(request: ToolRequest):

    if request.name != "get_travel_recommendations":
        return {"error": "Unknown tool"}

    member = get_member(request.arguments["member_id"])
    rules = get_partner_config(member["partner_id"])

    recs = generate_recommendations(member, rules)

    return {
        "member": member,
        "recommendations": recs,
        "rules": rules
    }