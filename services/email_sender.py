import os
import resend
from pathlib import Path

resend.api_key = os.getenv("RESEND_API_KEY")


async def send_email(lead, pdf_path: Path):
    with open(pdf_path, "rb") as f:
        pdf_bytes = list(f.read())

    safe_company = lead.company.replace(" ", "_")

    html_body = f"""
    <div style="font-family: 'Helvetica Neue', Arial, sans-serif; max-width: 600px; margin: 0 auto;">
      <div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%); padding: 40px; border-radius: 12px 12px 0 0;">
        <h1 style="color: #ffffff; font-size: 24px; font-weight: 700; margin: 0;">LeadPilot</h1>
        <p style="color: #94a3b8; font-size: 13px; margin: 4px 0 0;">AI Business Intelligence</p>
      </div>
      <div style="padding: 40px; background: #f8fafc; border: 1px solid #e2e8f0;">
        <h2 style="color: #0f172a; font-size: 20px; margin: 0 0 16px;">Hi {lead.name} 👋</h2>
        <p style="color: #475569; font-size: 15px; line-height: 1.7; margin: 0 0 16px;">
          Thank you for your interest. We've completed a personalized business audit report for
          <strong style="color: #0f172a;">{lead.company}</strong> — it's attached to this email.
        </p>
        <p style="color: #475569; font-size: 15px; line-height: 1.7; margin: 0 0 24px;">
          The report covers a detailed company overview, industry analysis, key opportunities,
          challenges, and tailored recommendations specific to your business.
        </p>
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;"/>
        <p style="color: #64748b; font-size: 13px; margin: 0;">
          This report was generated exclusively for <strong>{lead.company}</strong>.<br/>
          If you have any questions, simply reply to this email.
        </p>
      </div>
      <div style="padding: 24px 40px; background: #0f172a; border-radius: 0 0 12px 12px; text-align: center;">
        <p style="color: #475569; font-size: 12px; margin: 0;">© 2025 LeadPilot · Automated Business Intelligence</p>
      </div>
    </div>
    """

    params = {
        "from": os.getenv("SENDER_EMAIL"),
        "to": [lead.email],
        "subject": f"Your Business Audit Report — {lead.company}",
        "html": html_body,
        "attachments": [
            {
                "filename": f"{safe_company}_Audit_Report.pdf",
                "content": pdf_bytes,
            }
        ],
    }

    resend.Emails.send(params)