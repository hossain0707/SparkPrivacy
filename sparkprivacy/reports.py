"""Generate aggregate-only PDF assessment (no prompts or model output)."""
from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen.canvas import Canvas


def make_pdf(statistics: dict, events: list[dict], actions: dict) -> bytes:
    output = BytesIO()
    pdf = Canvas(output, pagesize=A4)
    page_width, page_height = A4
    def text(x, y, s, size=10, color="#314358", bold=False):
        pdf.setFillColor(colors.HexColor(color))
        pdf.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        pdf.drawString(x, y, s[:100])
    pdf.setFillColor(colors.HexColor("#0B1D2D"))
    pdf.rect(0, page_height-122, page_width, 122, stroke=0, fill=1)
    text(42,page_height-62,"SPARKPRIVACY",22,"#64E4BF",True)
    text(42,page_height-87,"Local-first data protection | Assessment report",11,"#D5F6EA")
    y = page_height-151
    text(42,y,"Generated (UTC): "+datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),10)
    y-=29
    text(42,y,"Audited events: "+str(statistics["total"]),15,"#0D2437",True)
    y-=27
    text(42,y,f"Blocked: {statistics['blocked']}   Redacted: {statistics['redacted']}   Observed: {statistics['observed']}   Allowed: {statistics['allowed']}")
    y-=35
    text(42,y,"Active category policies",13,"#0D2437",True)
    y-=25
    for category, action in sorted(actions.items()):
        text(50,y,f"{category}: {action.upper()}",10)
        y-=19
    y-=20
    text(42,y,"Recent metadata-only security events",13,"#0D2437",True)
    y-=23
    for event in events[:16]:
        label = f"{event['at'][:19]}   {event['channel']}   {event['disposition']}   findings: {event['count']}"
        text(45,y,label,8)
        y-=16
        if y<120:
            pdf.showPage();y=page_height-55
    y=min(y-30,110)
    text(42,y,"Assessment limitations",10,"#0D2437",True)
    text(42,y-16,"Pattern and policy checks are partial safeguards, not a DLP or compliance certification.",8)
    text(42,y-29,"No prompt content, personal data, raw model responses, credentials, or SSH keys are saved.",8)
    text(42,y-43,"Do not rely on this report alone to establish regulatory or enterprise compliance.",8)
    pdf.setAuthor("Md Najmul Hossain")
    pdf.setTitle("SparkPrivacy evidence report")
    pdf.save()
    return output.getvalue()
