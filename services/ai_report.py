import os
import json
import re
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def clean_json(raw: str) -> str:
    # Strip markdown fences
    raw = raw.strip()
    raw = re.sub(r'^```(?:json)?', '', raw, flags=re.MULTILINE)
    raw = re.sub(r'```$', '', raw, flags=re.MULTILINE)
    # Find first { to last }
    start = raw.find('{')
    end = raw.rfind('}')
    if start != -1 and end != -1:
        raw = raw[start:end+1]
    # Fix control characters ONLY inside JSON string values
    result = []
    in_string = False
    escape = False
    for char in raw:
        if escape:
            result.append(char)
            escape = False
        elif char == '\\':
            result.append(char)
            escape = True
        elif char == '"':
            result.append(char)
            in_string = not in_string
        elif in_string and char == '\n':
            result.append('\\n')
        elif in_string and char == '\r':
            result.append('\\r')
        elif in_string and char == '\t':
            result.append('\\t')
        elif in_string and ord(char) < 0x20:
            result.append(' ')
        else:
            result.append(char)
    return ''.join(result)

async def generate_report(lead, enriched: dict) -> dict:
    prompt = f"""You are a senior business analyst at a top consulting firm.
Generate a highly personalized business audit report for this company.

PROSPECT INFORMATION:
- Name: {lead.name}
- Company: {lead.company}
- Website: {lead.website}
- Industry: {lead.industry}
- Description: {lead.description}

RESEARCH DATA FOUND:
{enriched.get('summary', '')[:3000]}

IMPORTANT RULES:
- Every insight must be SPECIFIC to {lead.company}
- Use actual facts from the research data above
- Do NOT use generic statements
- Address {lead.name} directly in the conclusion

You MUST respond with ONLY a valid JSON object. No text before or after. No markdown. Just the raw JSON.

{{
  "executive_summary": "3 paragraph personalized summary specific to {lead.company} using real research data",
  "company_overview": "Detailed overview of what {lead.company} actually does based on research",
  "industry_analysis": {{
    "current_landscape": "Current state of {lead.industry} industry with specific market context",
    "key_trends": ["specific trend 1", "specific trend 2", "specific trend 3", "specific trend 4"],
    "market_opportunity": "Specific opportunity relevant to {lead.company}"
  }},
  "strengths": [
    {{"title": "Specific strength title", "detail": "Specific detail about {lead.company} strength"}},
    {{"title": "Specific strength title", "detail": "Specific detail about {lead.company} strength"}},
    {{"title": "Specific strength title", "detail": "Specific detail about {lead.company} strength"}}
  ],
  "opportunities": [
    {{"title": "Opportunity title", "detail": "Specific actionable opportunity for {lead.company}"}},
    {{"title": "Opportunity title", "detail": "Specific actionable opportunity for {lead.company}"}},
    {{"title": "Opportunity title", "detail": "Specific actionable opportunity for {lead.company}"}}
  ],
  "challenges": [
    {{"title": "Challenge title", "detail": "Specific challenge {lead.company} faces"}},
    {{"title": "Challenge title", "detail": "Specific challenge {lead.company} faces"}}
  ],
  "recommendations": [
    {{"priority": "High", "title": "Recommendation", "detail": "Specific recommendation for {lead.company}", "impact": "Expected impact"}},
    {{"priority": "High", "title": "Recommendation", "detail": "Specific recommendation for {lead.company}", "impact": "Expected impact"}},
    {{"priority": "Medium", "title": "Recommendation", "detail": "Specific recommendation for {lead.company}", "impact": "Expected impact"}},
    {{"priority": "Medium", "title": "Recommendation", "detail": "Specific recommendation for {lead.company}", "impact": "Expected impact"}}
  ],
  "conclusion": "Personalized closing paragraph addressing {lead.name} directly with specific next steps for {lead.company}"
}}"""

    try:
        message = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=4000,
            temperature=0.7,
            messages=[
                {
                    "role": "system",
                    "content": "You are a business analyst. Always respond with valid JSON only. No markdown, no explanation, just raw JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        raw = message.choices[0].message.content
        cleaned = clean_json(raw)

        print("=== RAW AI RESPONSE (first 300) ===")
        print(raw[:300])
        print("=== CLEANED JSON (first 300) ===")
        print(cleaned[:300])

        report_data = json.loads(cleaned)
        return report_data

    except json.JSONDecodeError as e:
        print(f"JSON PARSE ERROR: {e}")
        try:
            # Second attempt - remove all control chars aggressively
            aggressive = re.sub(r'[\x00-\x1f\x7f]', ' ', cleaned)
            report_data = json.loads(aggressive)
            return report_data
        except Exception:
            print(f"SECOND PARSE ALSO FAILED")
            return _fallback_report(lead)


def _fallback_report(lead) -> dict:
    return {
        "executive_summary": f"This report provides an analysis of {lead.company} operating in the {lead.industry} sector.",
        "company_overview": f"{lead.company}: {lead.description}",
        "industry_analysis": {
            "current_landscape": f"The {lead.industry} industry is evolving rapidly with digital transformation.",
            "key_trends": ["Digital transformation", "AI adoption", "Customer experience", "Data analytics"],
            "market_opportunity": f"Significant growth opportunities exist for {lead.company}."
        },
        "strengths": [
            {"title": "Market Presence", "detail": f"{lead.company} has established itself in {lead.industry}."},
            {"title": "Domain Expertise", "detail": "Deep industry knowledge and experience."},
            {"title": "Customer Focus", "detail": "Strong orientation toward customer needs."}
        ],
        "opportunities": [
            {"title": "Digital Expansion", "detail": "Leverage digital channels for growth."},
            {"title": "Process Automation", "detail": "Automate repetitive workflows."},
            {"title": "Data Utilization", "detail": "Better use of data for decisions."}
        ],
        "challenges": [
            {"title": "Market Competition", "detail": "Increasing competition in the sector."},
            {"title": "Scaling Operations", "detail": "Managing growth while maintaining quality."}
        ],
        "recommendations": [
            {"priority": "High", "title": "Invest in Automation", "detail": "Prioritize workflow automation.", "impact": "30% efficiency gain"},
            {"priority": "High", "title": "Strengthen Digital Presence", "detail": "Enhance online visibility.", "impact": "Increased lead generation"},
            {"priority": "Medium", "title": "Build Data Infrastructure", "detail": "Implement analytics.", "impact": "Better decisions"},
            {"priority": "Medium", "title": "Customer Retention", "detail": "Launch loyalty program.", "impact": "Reduced churn"}
        ],
        "conclusion": f"Dear {lead.name}, we look forward to supporting {lead.company}'s growth journey.",
        "error": "fallback"
    }