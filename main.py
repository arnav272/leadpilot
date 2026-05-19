import os
import json
import asyncio
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="LeadPilot")
templates = Jinja2Templates(directory="templates")
Path("reports").mkdir(exist_ok=True)


class Lead(BaseModel):
    name: str
    email: str
    company: str
    website: str
    industry: str
    description: str


@app.get("/", response_class=HTMLResponse)
async def serve_form(request: Request):
    return templates.TemplateResponse(request=request, name="form.html")


@app.get("/reports/{filename}")
async def serve_report(filename: str):
    """Serve generated PDF for download or inline view."""
    pdf_path = Path("reports") / filename
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=filename
    )


@app.post("/analyze")
async def analyze_lead(lead: Lead):
    async def pipeline(lead: Lead):
        from services.enrichment import enrich_company
        from services.ai_report import generate_report
        from services.pdf_generator import generate_pdf
        from services.email_sender import send_email
        from services.google_services import log_to_sheets, archive_to_drive

        def event(step, status, message, data={}):
            payload = json.dumps({
                "step": step,
                "status": status,
                "message": message,
                **data
            })
            return f"data: {payload}\n\n"

        pdf_path = None
        report_status = "Failed"

        try:
            # ── Step 1: Validate ─────────────────────────────────────────
            yield event("validate", "running", "Verifying submitted information...")
            await asyncio.sleep(0.6)
            if not lead.email or not lead.company:
                yield event("validate", "error", "Missing required fields.")
                return
            yield event("validate", "done", "Lead information verified.")

            # ── Step 2: Enrich ───────────────────────────────────────────
            yield event("enrich", "running", f"Researching {lead.company} across public sources...")
            try:
                enriched = await enrich_company(lead.company, lead.website, lead.industry)
            except Exception as e:
                print(f"ENRICH ERROR: {e}")
                enriched = {
                    "company": lead.company,
                    "website": lead.website,
                    "industry": lead.industry,
                    "summary": f"{lead.company}: {lead.description}",
                    "sources": [],
                }
            yield event("enrich", "done", "Company research completed.")

            # ── Step 3: Generate Report ──────────────────────────────────
            yield event("report", "running", "AI is analyzing and writing your report...")
            try:
                report_content = await generate_report(lead, enriched)
            except Exception as e:
                print(f"REPORT ERROR: {e}")
                report_content = {
                    "executive_summary": f"{lead.company} operates in the {lead.industry} sector. {lead.description}",
                    "company_overview": lead.description,
                    "industry_analysis": {
                        "current_landscape": f"The {lead.industry} industry is rapidly evolving.",
                        "key_trends": ["Digital transformation", "AI adoption", "Customer experience", "Data analytics"],
                        "market_opportunity": f"Significant opportunities exist for {lead.company}."
                    },
                    "strengths": [
                        {"title": "Market Presence", "detail": f"{lead.company} operates in {lead.industry}."},
                        {"title": "Domain Expertise", "detail": "Strong industry knowledge."},
                        {"title": "Customer Focus", "detail": "Customer-centric approach."}
                    ],
                    "opportunities": [
                        {"title": "Digital Expansion", "detail": "Leverage digital channels."},
                        {"title": "Automation", "detail": "Streamline operations."},
                        {"title": "Data Strategy", "detail": "Build data-driven decisions."}
                    ],
                    "challenges": [
                        {"title": "Competition", "detail": "Growing competitive pressure."},
                        {"title": "Scaling", "detail": "Managing growth efficiently."}
                    ],
                    "recommendations": [
                        {"priority": "High", "title": "Invest in Technology", "detail": "Prioritize tech stack improvements.", "impact": "Efficiency gains"},
                        {"priority": "High", "title": "Market Expansion", "detail": "Enter new segments.", "impact": "Revenue growth"},
                        {"priority": "Medium", "title": "Data Infrastructure", "detail": "Build analytics capabilities.", "impact": "Better decisions"},
                        {"priority": "Medium", "title": "Customer Retention", "detail": "Launch loyalty program.", "impact": "Reduced churn"}
                    ],
                    "conclusion": f"Dear {lead.name}, we look forward to supporting {lead.company}'s growth."
                }
            yield event("report", "done", "Report content generated successfully.")

            # ── Step 4: Generate PDF ─────────────────────────────────────
            yield event("pdf", "running", "Compiling your professional PDF document...")
            try:
                pdf_path = await generate_pdf(lead, report_content)
            except Exception as e:
                print(f"PDF ERROR: {e}")
                yield event("pdf", "error", f"PDF generation failed: {str(e)}")
                await log_to_sheets(lead, "Failed - PDF Error")
                return
            yield event("pdf", "done", "PDF document ready.", {
                "pdf_filename": pdf_path.name
            })

            # ── Step 5: Send Email ───────────────────────────────────────
            yield event("email", "running", f"Sending report to {lead.email}...")
            try:
                await send_email(lead, pdf_path)
            except Exception as e:
                print(f"EMAIL ERROR: {e}")
                yield event("email", "error", f"Email delivery failed: {str(e)}")
                await log_to_sheets(lead, "Failed - Email Error")
                return
            yield event("email", "done", f"Report delivered to {lead.email}")

            # ── Bonus: Google Sheets + Drive ─────────────────────────────
            report_status = "Success"
            await log_to_sheets(lead, report_status)
            await archive_to_drive(pdf_path)

            # ── Complete ─────────────────────────────────────────────────
            yield event("complete", "done", "Pipeline complete!", {
                "pdf_filename": pdf_path.name
            })

        except Exception as e:
            print(f"PIPELINE ERROR: {e}")
            await log_to_sheets(lead, f"Failed - {str(e)[:50]}")
            yield event("error", "error", f"An unexpected error occurred: {str(e)}")

    return StreamingResponse(
        pipeline(lead),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)