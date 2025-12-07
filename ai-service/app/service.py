from .schemas import AdviceRequest, AdviceResponse, CategorySummary
from google import genai
import json
import os


# Initialize client only if API key is available
api_key = os.getenv("GOOGLE_AI_API_KEY")
if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None
MODEL_NAME = "gemini-2.5-flash"


def build_prompt(req: AdviceRequest) -> str:
    """Turn the budget snapshot + user question into a clear text prompt."""
    income = req.snapshot.income
    expenses = req.snapshot.expenses

    
    totals_by_category: dict[str, float] = {}
    for e in expenses:
        totals_by_category[e.category] = totals_by_category.get(e.category, 0.0) + e.amount

    total_expenses = sum(totals_by_category.values())

    lines: list[str] = [
        "You are Budget Baddie, a helpful but honest budgeting assistant.",
        "You get the user's recent monthly budget and a question about a potential purchase.",
        "You must answer using ONLY the data provided.",
        "",
        f"Month: {req.snapshot.month}",
        f"Monthly income: {income:.2f}",
        f"Total expenses: {total_expenses:.2f}",
        "",
        "Expenses by category (sum for this month):",
    ]

    for cat, amt in totals_by_category.items():
        lines.append(f"- {cat}: {amt:.2f}")

    if req.item_name:
        lines.append("")
        lines.append(f"Item they are considering: {req.item_name}")
    if req.item_url:
        lines.append(f"Item link (for context only, do not browse): {req.item_url}")

    lines.append("")
    lines.append(f"User's question: {req.question}")
    lines.append("")
    lines.append(
        "Based on this information, decide whether they should buy this item now."
    )
    lines.append(
        "Only consider affordability and their spending patterns, not moral judgment."
    )
    lines.append("")
    lines.append("Return your answer as valid JSON ONLY, with this exact schema:")
    lines.append("{")
    lines.append('  "recommendation": "BUY" | "WAIT" | "AVOID",')
    lines.append('  "explanation": "short explanation in 3-6 sentences",')
    lines.append('  "top_categories": [')
    lines.append('    {"category": "string", "total": number},')
    lines.append('    {"category": "string", "total": number},')
    lines.append('    {"category": "string", "total": number}')
    lines.append("  ],")
    lines.append('  "suggested_monthly_savings": number')
    lines.append("}")
    lines.append("")
    lines.append("Do not include any text before or after the JSON.")

    return "\n".join(lines)


def generate_advice(req: AdviceRequest) -> AdviceResponse:
    """
    Call Gemini with the budget snapshot + question and turn its JSON reply
    into our AdviceResponse model.
    """
    if not client:
        return AdviceResponse(
            recommendation="WAIT",
            explanation=(
                "AI service is not configured. Please set GOOGLE_AI_API_KEY environment variable. "
                "For now, we recommend waiting to make this purchase."
            ),
            top_categories=[],
            suggested_monthly_savings=None,
        )
    
    prompt = build_prompt(req)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    raw_text = response.text.strip()

  
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        # Fallback
        return AdviceResponse(
            recommendation="WAIT",
            explanation=(
                "I had trouble parsing the AI's response, so here is a conservative "
                "recommendation: wait to make this purchase until your expenses are "
                "clearly below your income."
            ),
            top_categories=[],
            suggested_monthly_savings=None,
        )

    top_categories = [
        CategorySummary(category=item["category"], total=float(item["total"]))
        for item in data.get("top_categories", [])
        if "category" in item and "total" in item
    ]

    return AdviceResponse(
        recommendation=data.get("recommendation", "WAIT"),
        explanation=data.get("explanation", ""),
        top_categories=top_categories,
        suggested_monthly_savings=data.get("suggested_monthly_savings"),
    )
