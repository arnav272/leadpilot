"""
LeadPilot PDF Generator
Premium, minimal, high-end editorial business intelligence layout.
"""

from pathlib import Path
from fpdf import FPDF, XPos, YPos
from datetime import datetime

# ── Design tokens (Strict, premium three-tone editorial scheme) ───────────────
NAVY     = (15,  23,  42)    # Accent / Headings (Deep Slate / Navy Blue)
BODY     = (55,  65,  81)    # Body text (Dark Charcoal)
MUTED    = (107, 114, 128)   # Sub-labels, dates, and captions (Muted Slate Gray)
RULE     = (229, 231, 235)   # Subtle, elegant division lines
WHITE    = (255, 255, 255)   # Strict solid white backgrounds across all pages

# ── Page geometry ─────────────────────────────────────────────────────────────
L_MARGIN  = 24   # Increased left margin for elegant breathing room
R_MARGIN  = 24   # Increased right margin
T_MARGIN  = 26   # Top margin for running layout
PAGE_W    = 210  # A4 width mm
CONTENT_W = PAGE_W - L_MARGIN - R_MARGIN   # 162 mm usable text content width


def safe(v) -> str:
    """Strip non-latin-1 characters so fpdf2 built-in fonts don't crash."""
    return str(v or '').encode('latin-1', 'replace').decode('latin-1')


def cur_year() -> str:
    return str(datetime.now().year)


# ── Premium Editorial PDF Layout Class ────────────────────────────────────────

class LeadPilotPDF(FPDF):

    def __init__(self, company: str, date_str: str):
        super().__init__()
        self._company  = safe(company)
        self._date_str = date_str
        self.set_auto_page_break(auto=False)
        self.set_margins(L_MARGIN, T_MARGIN, R_MARGIN)

    def header(self):
        if self.page_no() <= 1:
            return
        # Sits neatly at the top margin edge
        self.set_y(12)
        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(*NAVY)
        self.cell(40, 5, 'LEADPILOT', new_x=XPos.RIGHT, new_y=YPos.TOP)
        
        self.set_font('Helvetica', '', 8)
        self.set_text_color(*MUTED)
        label = f'{self._company}   |   Business Audit Report'
        self.cell(0, 5, label, align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # Super thin running border rule
        self.set_draw_color(*RULE)
        self.set_line_width(0.2)
        self.line(L_MARGIN, 19, PAGE_W - R_MARGIN, 19)
        self.set_y(T_MARGIN)

    def footer(self):
        if self.page_no() <= 1:
            return
        # Pushed cleanly to the absolute bottom margin edge to prevent overlaps
        self.set_draw_color(*RULE)
        self.set_line_width(0.2)
        self.line(L_MARGIN, 280, PAGE_W - R_MARGIN, 280)
        
        self.set_y(283)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(*MUTED)
        self.cell(
            0, 5,
            f'Confidential  ·  LeadPilot AI  ·  {self._date_str}',
            new_x=XPos.LMARGIN, new_y=YPos.TOP,
        )
        self.cell(
            0, 5,
            f'Page {self.page_no()}',
            align='R',
            new_x=XPos.LMARGIN, new_y=YPos.NEXT,
        )


# ── Layout structural helpers (Typographic Stack over Box Borders) ────────────

def section_label(pdf, text: str, gap_before=14):
    """Clean unbordered vertical section tags."""
    pdf.ln(gap_before)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_text_color(*NAVY)
    pdf.set_x(L_MARGIN)
    pdf.cell(0, 4, text.upper(), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(3)


def page_heading(pdf, text: str):
    """Large, premium heading scale with modern whitespace."""
    pdf.set_x(L_MARGIN)
    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 10, safe(text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(6)


def body_para(pdf, text: str, color=None, is_bold=False):
    """Standard cleanly tracked copy paragraph block."""
    pdf.set_x(L_MARGIN)
    font_style = 'B' if is_bold else ''
    pdf.set_font('Helvetica', font_style, 10)
    pdf.set_text_color(*(color or BODY))
    pdf.multi_cell(CONTENT_W, 6, safe(text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)


# ── Editorial Structural Elements ──────────────────────────────────────────────

def typographic_paragraph(pdf, title: str, text: str, label_prefix=""):
    """Replaces box cards with a modern, beautifully spaced typographic stack."""
    pdf.set_x(L_MARGIN)
    
    # Title / Label line
    pdf.set_font('Helvetica', 'B', 10.5)
    pdf.set_text_color(*NAVY)
    full_title = f"{label_prefix} {title}".strip() if label_prefix else title
    pdf.multi_cell(CONTENT_W, 5.5, safe(full_title), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1.5)
    
    # Text line
    pdf.set_x(L_MARGIN)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(*BODY)
    pdf.multi_cell(CONTENT_W, 5.5, safe(text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(6)


# ── Cover page (Unbordered, Typographic Whitespace Stack) ─────────────────────

def draw_cover(pdf: LeadPilotPDF, lead, date_str: str):
    pdf.add_page()

    # Absolute pure white corporate background
    pdf.set_fill_color(*WHITE)
    pdf.rect(0, 0, PAGE_W, 297, 'F')

    # Top brand header stack
    pdf.set_xy(L_MARGIN, 30)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 6, 'LeadPilot', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_x(L_MARGIN)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(*MUTED)
    pdf.cell(0, 5, 'AI Business Intelligence Solution', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Large Main Dynamic Headline Stack
    pdf.set_xy(L_MARGIN, 95)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(*MUTED)
    pdf.cell(0, 5, 'BUSINESS AUDIT REPORT', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)

    co = safe(lead.company)
    # Fix potential clipping issues by accurately scaling font size
    fs = 36 if len(co) <= 15 else 28 if len(co) <= 25 else 22
    pdf.set_x(L_MARGIN)
    pdf.set_font('Helvetica', 'B', fs)
    pdf.set_text_color(*NAVY)
    pdf.multi_cell(CONTENT_W, fs * 0.6, co, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.ln(3)
    pdf.set_x(L_MARGIN)
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(*BODY)
    pdf.multi_cell(
        CONTENT_W, 6,
        f"A comprehensive AI-powered strategic evaluation detailing market positioning, "
        f"operational strengths, and structured growth trajectories compiled for {co}.",
        new_x=XPos.LMARGIN, new_y=YPos.NEXT,
    )

    # Metadata Grid — Replaced with an elegant, unbordered vertical list stack
    pdf.set_xy(L_MARGIN, 195)
    meta = [
        ('PREPARED FOR', safe(lead.name)),
        ('COMPANY',      co),
        ('INDUSTRY',     safe(lead.industry)),
        ('DATE',         date_str),
    ]
    
    for lbl, val in meta:
        pdf.set_x(L_MARGIN)
        pdf.set_font('Helvetica', 'B', 7.5)
        pdf.set_text_color(*MUTED)
        pdf.cell(32, 6, lbl, new_x=XPos.RIGHT, new_y=YPos.TOP)
        
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(*NAVY)
        pdf.cell(0, 6, val, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(1.5)

    # Clean Cover Bottom Line Rule
    pdf.set_xy(L_MARGIN, 260)
    pdf.set_draw_color(*RULE)
    pdf.set_line_width(0.3)
    pdf.line(L_MARGIN, 260, PAGE_W - R_MARGIN, 260)
    pdf.ln(5)
    
    pdf.set_x(L_MARGIN)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(*MUTED)
    pdf.cell(0, 4, f'Confidential  ·  Generated exclusively for {co}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_x(L_MARGIN)
    pdf.cell(0, 4, f'© {cur_year()} LeadPilot  ·  Standard Evaluation Framework', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Re-enable manual spacing rule protections for subsequent content pages
    pdf.set_auto_page_break(auto=True, margin=26)


# ── Main PDF builder ───────────────────────────────────────────────────────────

async def generate_pdf(lead, report_content: dict) -> Path:

    date_str = datetime.now().strftime('%B %d, %Y')
    pdf      = LeadPilotPDF(lead.company, date_str)

    # ── PAGE 1 : COVER ────────────────────────────────────────────────────────
    draw_cover(pdf, lead, date_str)

    # ── PAGE 2 : EXECUTIVE SUMMARY + COMPANY OVERVIEW ─────────────────────────
    pdf.add_page()

    section_label(pdf, 'Executive Summary', gap_before=0)
    page_heading(pdf, 'At a Glance')

    exec_text = safe(report_content.get('executive_summary', ''))
    paras     = [p.strip() for p in exec_text.split('\n') if p.strip()]
    if not paras:
        paras = [exec_text] if exec_text else ['No summary data available.']
    
    for para in paras:
        body_para(pdf, para)

    section_label(pdf, 'Company Overview', gap_before=6)
    body_para(pdf, report_content.get('company_overview', ''))

    # ── PAGE 3 : INDUSTRY ANALYSIS ────────────────────────────────────────────
    pdf.add_page()

    section_label(pdf, 'Industry Analysis', gap_before=0)
    page_heading(pdf, 'Market Landscape & Trends')

    ind = report_content.get('industry_analysis', {})
    body_para(pdf, ind.get('current_landscape', ''))

    section_label(pdf, 'Key Trends', gap_before=4)
    trends = ind.get('key_trends', [])
    for trend in trends:
        # Subtle typographic bullet styling with strict alignment rules
        pdf.set_x(L_MARGIN)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(*NAVY)
        pdf.cell(5, 5.5, '·', new_x=XPos.RIGHT, new_y=YPos.TOP)
        
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(*BODY)
        pdf.multi_cell(CONTENT_W - 5, 5.5, safe(trend), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2)

    section_label(pdf, 'Market Opportunity', gap_before=6)
    body_para(pdf, ind.get('market_opportunity', ''))

    # ── PAGE 4 : SWOT CRITICAL MAPPING ────────────────────────────────────────
    pdf.add_page()
    page_heading(pdf, 'Strategic Matrix')

    section_label(pdf, 'Core Strengths', gap_before=0)
    for item in report_content.get('strengths', []):
        typographic_paragraph(pdf, item.get('title', ''), item.get('detail', ''), label_prefix="[STRENGTH]")

    section_label(pdf, 'Growth Opportunities', gap_before=4)
    for item in report_content.get('opportunities', []):
        typographic_paragraph(pdf, item.get('title', ''), item.get('detail', ''), label_prefix="[OPPORTUNITY]")

    section_label(pdf, 'Challenges to Address', gap_before=4)
    for item in report_content.get('challenges', []):
        typographic_paragraph(pdf, item.get('title', ''), item.get('detail', ''), label_prefix="[RISK FACTOR]")

    # ── PAGE 5 : RECOMMENDATIONS + CONCLUSION ─────────────────────────────────
    pdf.add_page()

    section_label(pdf, 'Strategic Recommendations', gap_before=0)
    page_heading(pdf, 'Action Plan')

    # Fully vertical, cleanly-spaced structural recommendations flow
    for rec in report_content.get('recommendations', []):
        priority_level = rec.get('priority', 'Medium').strip().upper()
        prefix_tag = f"[{priority_level} PRIORITY]"
        
        pdf.set_x(L_MARGIN)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(*NAVY)
        pdf.multi_cell(CONTENT_W, 6, f"{prefix_tag} {safe(rec.get('title', ''))}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(1)
        
        pdf.set_x(L_MARGIN)
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(*BODY)
        pdf.multi_cell(CONTENT_W, 5.5, safe(rec.get('detail', '')), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(1.5)
        
        pdf.set_x(L_MARGIN)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(*NAVY)
        pdf.cell(0, 5, f"Expected Outcome: {safe(rec.get('impact', ''))}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # Subtle unbordered spacer line between recommendations
        pdf.ln(3)
        pdf.set_draw_color(*RULE)
        pdf.set_line_width(0.2)
        pdf.line(L_MARGIN, pdf.get_y(), PAGE_W - R_MARGIN, pdf.get_y())
        pdf.ln(5)

    section_label(pdf, 'Conclusion', gap_before=4)
    body_para(pdf, report_content.get('conclusion', ''))
    
    pdf.ln(4)
    pdf.set_x(L_MARGIN)
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 5, f'Generated by LeadPilot Automation  ·  {date_str}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Research Sources Pipeline
    sources = report_content.get('sources', [])
    if sources:
        section_label(pdf, 'Research Sources', gap_before=6)
        for src in sources[:4]:
            pdf.set_x(L_MARGIN)
            pdf.set_font('Helvetica', '', 8)
            pdf.set_text_color(*MUTED)
            pdf.cell(0, 5, f"· {safe(src)[:95]}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ── Save Pipeline ─────────────────────────────────────────────────────────
    safe_name = (lead.company
                 .replace(' ', '_')
                 .replace('/', '-')
                 .lower())
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    pdf_path  = Path('reports') / f'{safe_name}_{timestamp}.pdf'
    pdf.output(str(pdf_path))
    return pdf_path