from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime

OUTPUT = "Orders_Dashboard_Snapshot.pdf"

SHARED_COST_POOL = 200.00
NUM_ORDERS = 34
SHARED_PER_ORDER = SHARED_COST_POOL / NUM_ORDERS  # exact: ~5.882352...

# (rank, name, phone, items, total, paid, status)
orders = [
    ( 1, "Nazmul Qureshi",              "512-354-5666", "Goat 10 lb, Young Hen ×4",                                            168.00, 174.75, "Confirmed"),
    ( 2, "Bobby Mansoor",                "512-736-3626", "Young Hen ×5, Broiler ×5",                                            160.00, 165.00, "Confirmed"),
    ( 3, "Syed M. Ayaz Anwar",           "734-892-4937", "Goat 10 lb, Broiler ×5, Quail ×3",                                   190.00, 196.25, "Confirmed"),
    ( 4, "Muhammad Rahman (Rana)",        "415-859-8039", "Beef 40 lb, Goat 10 lb, Rooster ×1",                                 357.00, 364.00, "Confirmed"),
    ( 5, "Khorshed Alam Khan",            "847-912-8219", "Beef 10 lb, Desi Skin-ON ×4, Broiler ×6, Duck ×2, Quail ×2",        232.00, 238.45, "Confirmed"),
    ( 6, "Zahid Rahman",                  "925-918-7695", "Beef 20 lb",                                                          120.00, 126.06, "Confirmed"),
    ( 7, "BIPUL",                         "214-770-4360", "Beef 30 lb",                                                          180.00, 187.00, "Confirmed"),
    ( 8, "SoheL Rahaman",                 "641-451-4138", "Beef 20 lb, Rooster ×5",                                             205.00, 211.45, "Confirmed"),
    ( 9, "Towhidul Ali Tanveer",          "512-781-9833", "Beef 40 lb, Goat 6 lb",                                              300.00, 307.14, "Confirmed"),
    (10, "Aftab Sheikh",                  "512-665-2655", "Beef 25 lb",                                                          150.00, 170.00, "Confirmed"),
    (11, "Iftekhar Rahman",               "512-466-3761", "Rooster ×2, Eggs 4 doz",                                              54.00,  60.45, "Confirmed"),
    (12, "Sheikh Bakir",                  "505-910-5845", "Beef 10 lb, Goat 10 lb, Desi Skin-OFF ×2, Broiler ×2",              208.00, 214.67, "Confirmed"),
    (13, "Md. Rezaul Haque (Reza)",       "512-825-3362", "Beef 20 lb",                                                          120.00, 126.25, "Confirmed"),
    (14, "Farooqui",                      "906-370-7829", "Beef 20 lb, Goat 20 lb, Broiler ×6",                                 410.00, 416.45, "Confirmed"),
    (15, "Tawfik Ahmed",                  "512-826-5718", "Beef 10 lb, Rooster ×2, Duck ×1, Eggs 2 doz",                        124.00, 130.45, "Confirmed"),
    (16, "Rubayat Khan",                  "737-267-1909", "Beef 20 lb, Goat 20 lb",                                             320.00, 326.25, "Confirmed"),
    (17, "Rony Khan (6 pcs/chicken)",     "512-736-5638", "Desi Skin-OFF ×20, Rooster ×1, Quail ×6",                            227.00, 234.14, "Confirmed"),
    (18, "Naseef Chowdhury",              "575-418-1108", "Beef 20 lb, Young Hen ×3, Rooster ×4, Broiler ×1, Duck ×1",         274.00, 280.25, "Confirmed"),
    (19, "Raihan Kabir",                  "678-620-6852", "Beef 20 lb, Young Hen ×2",                                           154.00, 160.25, "Confirmed"),
    (20, "Md Zahedul Khan",               "737-410-4296", "Beef 20 lb, Desi Skin-OFF ×3, Eggs 2 doz",                           157.00, 163.45, "Confirmed"),
    (21, "Mashfik Hossain",               "512-784-7408", "Young Hen ×3, Rooster ×4, Eggs 5 doz",                               144.00, 153.09, "Confirmed"),
    (22, "Enam Haque (Mona)",             "512-317-8846", "Desi Skin-ON ×8, Rooster ×1",                                         81.00,  87.25, "Confirmed"),
    (23, "Rezwan Rahman",                 "503-369-8533", "Goat 5 lb, Desi Skin-OFF ×2, Rooster ×2, Duck ×1",                  122.00, 128.25, "Confirmed"),
    (24, "Shazzad Hossain",               "267-777-3180", "Young Hen ×4, Duck ×1, Quail ×2",                                     98.00, 104.45, "Confirmed"),
    (25, "Asma Sharif",                   "512-909-0161", "Goat 15 lb, Eggs 5 doz",                                             175.00, 181.25, "Confirmed"),
    (26, "Tuhin Rahman",                  "805-415-4012", "Beef 20 lb, Rooster ×2",                                             154.00, 161.69, "Confirmed"),
    (27, "Nadim Islam",                   "651-354-5463", "Beef 10 lb, Young Hen ×2, Eggs 2 doz",                               104.00, 110.45, "Confirmed"),
    (28, "Sonia Sharmin",                 "512-669-8109", "Beef 10 lb, Eggs 4 doz",                                              80.00,  86.45, "Confirmed"),
    (29, "Masud Hassan",                  "561-629-2604", "Beef 20 lb, Eggs 5 doz",                                             145.00, 151.45, "Confirmed"),
    (30, "Asif Chowdhury",                "512-287-0602", "Beef 20 lb, Desi Skin-ON ×10, Quail ×6",                            230.00, 236.25, "Confirmed"),
    (31, "Rakib Hasan",                   "917-803-3144", "Beef 30 lb",                                                          180.00, 186.45, "Confirmed"),
    (32, "Mahtab Shamim",                 "512-365-0521", "Beef 10 lb",                                                           60.00,  66.25, "Confirmed"),
    (33, "Tareq Hossen",                  "906-370-6402", "Young Hen ×2, Broiler ×2",                                             64.00,  70.06, "Confirmed"),
    (34, "Munir Hossain",                 "347-379-6067", "Beef 30 lb, Broiler ×1",                                             195.00, 200.88, "Confirmed"),
]

grand_order_total = sum(r[4] for r in orders)
grand_paid        = sum(r[5] for r in orders)
grand_adj_total   = grand_order_total + SHARED_COST_POOL
net_remaining     = grand_adj_total - grand_paid

HEADER_BG    = colors.HexColor("#1a472a")
ALT          = colors.HexColor("#f4f4f4")
WHITE        = colors.white
FOOTER_BG    = colors.HexColor("#e8f5e9")
CREDIT_COLOR = colors.HexColor("#888888")
OWED_COLOR   = colors.HexColor("#c0392b")

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=landscape(A4),
    leftMargin=1.2*cm, rightMargin=1.2*cm,
    topMargin=1.5*cm, bottomMargin=1.5*cm,
)

styles = getSampleStyleSheet()
title_style = ParagraphStyle("title", fontSize=15, fontName="Helvetica-Bold",
                              alignment=TA_CENTER, spaceAfter=4)
sub_style   = ParagraphStyle("sub",   fontSize=9,  fontName="Helvetica",
                              alignment=TA_CENTER, spaceAfter=10,
                              textColor=colors.HexColor("#555555"))
cell_style   = ParagraphStyle("cell",  fontSize=7.5, fontName="Helvetica", leading=10)
credit_style = ParagraphStyle("credit", fontSize=7.5, fontName="Helvetica-Oblique",
                               leading=10, textColor=CREDIT_COLOR)
owed_style   = ParagraphStyle("owed",  fontSize=7.5, fontName="Helvetica-Bold",
                               leading=10, textColor=OWED_COLOR)

header = ["Rank", "Customer", "Phone", "Items Ordered",
          "Order Total", "Shared Cost", "Adj. Total", "Paid", "Remaining Due", "Status"]

table_data = [header]
for rank, name, phone, items, total, paid, status in orders:
    adj_total = total + SHARED_PER_ORDER
    remaining = adj_total - paid

    if remaining > 0.005:
        rem_cell = Paragraph(f"${remaining:,.2f}", owed_style)
    else:
        rem_cell = Paragraph(f"–${abs(remaining):,.2f}", credit_style)

    table_data.append([
        str(rank),
        Paragraph(name, cell_style),
        phone,
        Paragraph(items, cell_style),
        f"${total:,.2f}",
        f"${SHARED_PER_ORDER:,.2f}",
        f"${adj_total:,.2f}",
        f"${paid:,.2f}",
        rem_cell,
        status,
    ])

# Spacer + footer
table_data.append([""] * 10)
net_cell = (
    Paragraph(f"<b>–${abs(net_remaining):,.2f}</b>", credit_style)
    if net_remaining <= 0
    else Paragraph(f"<b>${net_remaining:,.2f}</b>", owed_style)
)
table_data.append([
    "",
    Paragraph("<b>TOTALS — 34 Orders | All Confirmed</b>", cell_style),
    "", "",
    f"${grand_order_total:,.2f}",
    f"${SHARED_COST_POOL:,.2f}",
    f"${grand_adj_total:,.2f}",
    f"${grand_paid:,.2f}",
    net_cell,
    "",
])

# Col widths: total ~27.1cm (fits in landscape A4 with 1.2cm margins each side)
col_widths = [0.8*cm, 4.1*cm, 2.7*cm, 8.3*cm, 1.9*cm, 1.9*cm, 1.9*cm, 1.9*cm, 2.2*cm, 2.0*cm]

style = TableStyle([
    # Header
    ("BACKGROUND",    (0, 0), (-1, 0), HEADER_BG),
    ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
    ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE",      (0, 0), (-1, 0), 8.5),
    ("ALIGN",         (0, 0), (-1, 0), "CENTER"),
    # Data rows
    ("ROWBACKGROUNDS",(0, 1), (-1, -3), [WHITE, ALT]),
    ("FONTSIZE",      (0, 1), (-1, -1), 7.5),
    ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ("ALIGN",         (0, 1), (-1, -1), "CENTER"),
    ("ALIGN",         (1, 1), (1, -1), "LEFT"),   # Customer
    ("ALIGN",         (3, 1), (3, -1), "LEFT"),   # Items
    ("ALIGN",         (4, 1), (8, -1), "RIGHT"),  # Numeric cols
    ("GRID",          (0, 0), (-1, -3), 0.4, colors.HexColor("#cccccc")),
    ("TOPPADDING",    (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("LEFTPADDING",   (0, 0), (-1, -1), 5),
    ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
    # Footer
    ("SPAN",          (0, -2), (-1, -2)),
    ("LINEABOVE",     (0, -1), (-1, -1), 1.5, HEADER_BG),
    ("BACKGROUND",    (0, -1), (-1, -1), FOOTER_BG),
    ("FONTNAME",      (0, -1), (-1, -1), "Helvetica-Bold"),
    ("ALIGN",         (4, -1), (8, -1), "RIGHT"),
])

t = Table(table_data, colWidths=col_widths, repeatRows=1)
t.setStyle(style)

generated = datetime.now().strftime("%Y-%m-%d %H:%M")
elements = [
    Paragraph("Farm2Kitchen Halal — Orders Dashboard Snapshot", title_style),
    Paragraph(
        f"Generated: {generated} &nbsp;|&nbsp; 34 Orders &nbsp;|&nbsp; All Confirmed"
        f" &nbsp;|&nbsp; Order Total: ${grand_order_total:,.2f}"
        f" &nbsp;|&nbsp; Shared Cost Pool: ${SHARED_COST_POOL:,.2f}"
        f" &nbsp;|&nbsp; Adj. Total: ${grand_adj_total:,.2f}"
        f" &nbsp;|&nbsp; Collected: ${grand_paid:,.2f}"
        f" &nbsp;|&nbsp; Net Credit: –${abs(net_remaining):,.2f}",
        sub_style
    ),
    t,
]

doc.build(elements)
print(f"PDF saved: {OUTPUT}")
