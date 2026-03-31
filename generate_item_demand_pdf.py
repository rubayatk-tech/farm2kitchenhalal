from reportlab.lib.pagesizes import portrait, A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime

OUTPUT = "Item_Demand_Breakdown.pdf"

items = [
    # (Item,                            Qty,  Unit,       Unit Price, Subtotal)
    ("Beef / Cow",                      475,  "lb",        6.00,  2850.00),
    ("Goat",                            106,  "lb",       10.00,  1060.00),
    ("Rooster (4–5 lbs)",                24,  "each",     17.00,   408.00),
    ("Young Hen / Poulette (3–4 lbs)",   25,  "each",     17.00,   425.00),
    ("Broiler (8–9 lbs)",                28,  "each",     15.00,   420.00),
    ("Desi Hard Chicken (Skin-OFF)",      27,  "each",      9.00,   243.00),
    ("Desi Hard Chicken (Skin-ON)",       22,  "each",      8.00,   176.00),
    ("Chicken Eggs",                      29,  "dozen",     5.00,   145.00),
    ("Young Peaking Duck",                 6,  "each",     20.00,   120.00),
    ("Quail",                             19,  "each",      5.00,    95.00),
]

grand_total = sum(r[4] for r in items)

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=portrait(A4),
    leftMargin=2.0*cm, rightMargin=2.0*cm,
    topMargin=2.0*cm, bottomMargin=2.0*cm,
)

styles = getSampleStyleSheet()
title_style = ParagraphStyle("title", fontSize=15, fontName="Helvetica-Bold",
                              alignment=TA_CENTER, spaceAfter=4)
sub_style   = ParagraphStyle("sub",   fontSize=9,  fontName="Helvetica",
                              alignment=TA_CENTER, spaceAfter=14,
                              textColor=colors.HexColor("#555555"))

HEADER_BG = colors.HexColor("#1a472a")
ALT       = colors.HexColor("#f4f4f4")
WHITE     = colors.white
TOTAL_BG  = colors.HexColor("#e8f5e9")

header = ["Item", "Total Qty", "Unit", "Unit Price", "Subtotal"]

table_data = [header]
for name, qty, unit, unit_price, subtotal in items:
    table_data.append([
        name,
        str(qty),
        unit,
        f"${unit_price:,.2f}",
        f"${subtotal:,.2f}",
    ])

# Spacer row then grand total
table_data.append(["", "", "", "", ""])
table_data.append(["GRAND TOTAL", "", "", "", f"${grand_total:,.2f}"])

col_widths = [7.5*cm, 2.5*cm, 2.5*cm, 3.0*cm, 3.0*cm]

style = TableStyle([
    # Header
    ("BACKGROUND",    (0, 0), (-1, 0), HEADER_BG),
    ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
    ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE",      (0, 0), (-1, 0), 10),
    ("ALIGN",         (0, 0), (-1, 0), "CENTER"),
    # Data rows
    ("ROWBACKGROUNDS",(0, 1), (-1, -3), [WHITE, ALT]),
    ("FONTSIZE",      (0, 1), (-1, -1), 9),
    ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ("ALIGN",         (0, 1), (0, -1), "LEFT"),
    ("ALIGN",         (1, 1), (-1, -1), "CENTER"),
    ("ALIGN",         (4, 1), (4, -1), "RIGHT"),
    ("ALIGN",         (3, 1), (3, -1), "RIGHT"),
    ("GRID",          (0, 0), (-1, -3), 0.4, colors.HexColor("#cccccc")),
    ("TOPPADDING",    (0, 0), (-1, -1), 7),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ("LEFTPADDING",   (0, 0), (-1, -1), 8),
    ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
    # Grand total row
    ("LINEABOVE",     (0, -1), (-1, -1), 1.5, HEADER_BG),
    ("BACKGROUND",    (0, -1), (-1, -1), TOTAL_BG),
    ("FONTNAME",      (0, -1), (-1, -1), "Helvetica-Bold"),
    ("FONTSIZE",      (0, -1), (-1, -1), 10),
    ("SPAN",          (0, -1), (3, -1)),
    ("ALIGN",         (0, -1), (3, -1), "RIGHT"),
    ("SPAN",          (0, -2), (-1, -2)),
])

t = Table(table_data, colWidths=col_widths, repeatRows=1)
t.setStyle(style)

generated = datetime.now().strftime("%Y-%m-%d %H:%M")
elements = [
    Paragraph("Farm2Kitchen Halal — Item Demand Breakdown", title_style),
    Paragraph(f"Generated: {generated} &nbsp;|&nbsp; 34 orders &nbsp;|&nbsp; Grand Total: ${grand_total:,.2f}", sub_style),
    t,
]

doc.build(elements)
print(f"PDF saved: {OUTPUT}")
