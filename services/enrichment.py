import os
from tavily import TavilyClient

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


async def enrich_company(company: str, website: str, industry: str) -> dict:
    try:
        queries = [
            f"{company} company overview products services",
            f"{company} {industry} recent news 2024 2025",
            f"{company} business model target customers",
        ]

        all_results = []
        for query in queries:
            result = client.search(
                query=query,
                search_depth="advanced",
                max_results=3
            )
            all_results.extend(result.get("results", []))

        # Deduplicate by URL
        seen = set()
        unique_results = []
        for r in all_results:
            if r["url"] not in seen:
                seen.add(r["url"])
                unique_results.append(r)

        # Build summary text
        summary_parts = []
        sources = []
        for r in unique_results[:6]:
            if r.get("content"):
                summary_parts.append(r["content"])
            if r.get("url"):
                sources.append(r["url"])

        summary = "\n\n".join(summary_parts)

        return {
            "company": company,
            "website": website,
            "industry": industry,
            "summary": summary[:4000],  # Keep within token limits
            "sources": sources,
            "raw_results": unique_results[:6]
        }

    except Exception as e:
        # Graceful fallback if enrichment fails
        return {
            "company": company,
            "website": website,
            "industry": industry,
            "summary": f"Company: {company}. Industry: {industry}. Website: {website}",
            "sources": [],
            "raw_results": [],
            "error": str(e)
        }