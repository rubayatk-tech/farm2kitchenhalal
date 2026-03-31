from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime

OUTPUT = "FCFS_Order_Priority_Report.pdf"

orders = [
    (1,  13, "Nazmul Qureshi",               "512-354-5666", "Goat 10 lb, Young Hen ×4",                                             168.00, 174.75, "Confirmed"),
    (2,  14, "Bobby Mansoor",                 "512-736-3626", "Young Hen ×5, Broiler ×5",                                             160.00, 165.00, "Confirmed"),
    (3,  15, "Syed M. Ayaz Anwar",            "734-892-4937", "Goat 10 lb, Broiler ×5, Quail ×3",                                    190.00, 196.25, "Confirmed"),
    (4,  16, "Muhammad Rahman (Rana)",         "415-859-8039", "Beef 40 lb, Goat 10 lb, Rooster ×1",                                  357.00, 364.00, "Confirmed"),
    (5,  17, "Khorshed Alam Khan",             "847-912-8219", "Beef 10 lb, Desi Skin-ON ×4, Broiler ×6, Duck ×2, Quail ×2",         232.00, 238.45, "Confirmed"),
    (6,  18, "Zahid Rahman",                   "925-918-7695", "Beef 20 lb",                                                           120.00, 126.06, "Confirmed"),
    (7,  19, "BIPUL",                          "214-770-4360", "Beef 30 lb",                                                           180.00, 187.00, "Confirmed"),
    (8,  20, "SoheL Rahaman",                  "641-451-4138", "Beef 20 lb, Rooster ×5",                                              205.00, 211.45, "Confirmed"),
    (9,  21, "Towhidul Ali Tanveer",           "512-781-9833", "Beef 40 lb, Goat 6 lb",                                               300.00, 307.14, "Confirmed"),
    (10, 22, "Aftab Sheikh",                   "512-665-2655", "Beef 25 lb",                                                           150.00, 170.00, "Confirmed"),
    (11, 23, "Iftekhar Rahman",                "512-466-3761", "Rooster ×2, Eggs 4 doz",                                               54.00,  60.45, "Confirmed"),
    (12, 24, "Sheikh Bakir",                   "505-910-5845", "Beef 10 lb, Goat 10 lb, Desi Skin-OFF ×2, Broiler ×2",               208.00, 214.67, "Confirmed"),
    (13, 25, "Md. Rezaul Haque (Reza)",        "512-825-3362", "Beef 20 lb",                                                           120.00, 126.25, "Confirmed"),
    (14, 26, "Farooqui",                       "906-370-7829", "Beef 20 lb, Goat 20 lb, Broiler ×6",                                  410.00, 416.45, "Confirmed"),
    (15, 27, "Tawfik Ahmed",                   "512-826-5718", "Beef 10 lb, Rooster ×2, Duck ×1, Eggs 2 doz",                         124.00, 130.45, "Confirmed"),
    (16, 28, "Rubayat Khan",                   "737-267-1909", "Beef 20 lb, Goat 20 lb",                                              320.00, 326.25, "Confirmed"),
    (17, 29, "Rony Khan (6 pcs/chicken)",      "512-736-5638", "Desi Skin-OFF ×20, Rooster ×1, Quail ×6",                             227.00, 234.14, "Confirmed"),
    (18, 31, "Naseef Chowdhury",               "575-418-1108", "Beef 20 lb, Young Hen ×3, Rooster ×4, Broiler ×1, Duck ×1",          274.00, 280.25, "Confirmed"),
    (19, 32, "Raihan Kabir",                   "678-620-6852", "Beef 20 lb, Young Hen ×2",                                            154.00, 160.25, "Confirmed"),
    (20, 33, "Md Zahedul Khan",                "737-410-4296", "Beef 20 lb, Desi Skin-OFF ×3, Eggs 2 doz",                            157.00, 163.45, "Confirmed"),
    (21, 34, "Mashfik Hossain",                "512-784-7408", "Young Hen ×3, Rooster ×4, Eggs 5 doz",                                144.00, 153.09, "Confirmed"),
    (22, 35, "Enam Haque (Mona)",              "512-317-8846", "Desi Skin-ON ×8, Rooster ×1",                                          81.00,  87.25, "Confirmed"),
    (23, 36, "Rezwan Rahman",                  "503-369-8533", "Goat 5 lb, Desi Skin-OFF ×2, Rooster ×2, Duck ×1",                   122.00, 128.25, "Confirmed"),
    (24, 37, "Shazzad Hossain",                "267-777-3180", "Young Hen ×4, Duck ×1, Quail ×2",                                      98.00, 104.45, "Confirmed"),
    (25, 38, "Asma Sharif",                    "512-909-0161", "Goat 15 lb, Eggs 5 doz",                                              175.00, 181.25, "Confirmed"),
    (26, 39, "Tuhin Rahman",                   "805-415-4012", "Beef 20 lb, Rooster ×2",                                              154.00, 161.69, "Confirmed"),
    (27, 40, "Nadim Islam",                    "651-354-5463", "Beef 10 lb, Young Hen ×2, Eggs 2 doz",                                104.00, 110.45, "Confirmed"),
    (28, 41, "Sonia Sharmin",                  "512-669-8109", "Beef 10 lb, Eggs 4 doz",                                               80.00,  86.45, "Confirmed"),
    (29, 42, "Masud Hassan",                   "561-629-2604", "Beef 20 lb, Eggs 5 doz",                                              145.00, 151.45, "Confirmed"),
    (30, 43, "Asif Chowdhury",                 "512-287-0602", "Beef 20 lb, Desi Skin-ON ×10, Quail ×6",                             230.00, 236.25, "Confirmed"),
    (31, 44, "Rakib Hasan",                    "917-803-3144", "Beef 30 lb",                                                           180.00, 186.45, "Confirmed"),
    (32, 45, "Mahtab Shamim",                  "512-365-0521", "Beef 10 lb",                                                            60.00,  66.25, "Confirmed"),
    (33, 46, "Tareq Hossen",                   "906-370-6402", "Young Hen ×2, Broiler ×2",                                              64.00,  70.06, "Confirmed"),
    (34, 47, "Munir Hossain",                  "347-379-6067", "Beef 30 lb, Broiler ×1",                                               195.00,   0.00, "Pending"),
]

total_value    = sum(r[5] for r in orders)
total_paid     = sum(r[6] for r in orders)
total_balance  = total_value - total_paid
confirmed      = sum(1 for r in orders if r[7] == "Confirmed")
pending        = len(orders) - confirmed

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
                              alignment=TA_CENTER, spaceAfter=10, textColor=colors.HexColor("#555555"))
cell_style  = ParagraphStyle("cell",  fontSize=7.5, fontName="Helvetica", leading=10)

header = ["Rank", "Customer", "Phone", "Items Ordered", "Total"]

GREEN   = colors.HexColor("#d4edda")
WHITE   = colors.white
HEADER  = colors.HexColor("#1a472a")
ALT     = colors.HexColor("#f4f4f4")

table_data = [header]
for rank, oid, name, phone, items, total, paid, status in orders:
    table_data.append([
        str(rank),
        Paragraph(name, cell_style),
        phone,
        Paragraph(items, cell_style),
        f"${total:,.2f}",
    ])

# Summary rows
table_data.append(["", "", "", "", ""])
table_data.append([
    "", Paragraph("<b>TOTALS</b>", cell_style), "", "",
    f"${total_value:,.2f}",
])

col_widths = [1.1*cm, 5.8*cm, 3.0*cm, 15.5*cm, 2.0*cm]

style = TableStyle([
    # Header
    ("BACKGROUND",   (0,0), (-1,0), HEADER),
    ("TEXTCOLOR",    (0,0), (-1,0), colors.white),
    ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE",     (0,0), (-1,0), 9),
    ("ALIGN",        (0,0), (-1,0), "CENTER"),
    ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
    ("ROWBACKGROUNDS", (0,1), (-1,-3), [WHITE, ALT]),
    ("FONTSIZE",     (0,1), (-1,-1), 8),
    ("ALIGN",        (0,1), (-1,-1), "CENTER"),
    ("ALIGN",        (3,1), (3,-1), "LEFT"),
    ("ALIGN",        (1,1), (1,-1), "LEFT"),
    ("GRID",         (0,0), (-1,-3), 0.4, colors.HexColor("#cccccc")),
    ("TOPPADDING",   (0,0), (-1,-1), 5),
    ("BOTTOMPADDING",(0,0), (-1,-1), 5),
    ("LEFTPADDING",  (0,0), (-1,-1), 5),
    ("RIGHTPADDING", (0,0), (-1,-1), 5),
    # Separator before totals
    ("LINEABOVE",    (0,-1), (-1,-1), 1.5, colors.HexColor("#1a472a")),
    ("BACKGROUND",   (0,-1), (-1,-1), colors.HexColor("#e8f5e9")),
    ("FONTNAME",     (0,-1), (-1,-1), "Helvetica-Bold"),
    ("SPAN",         (0,-2), (-1,-2)),
])

t = Table(table_data, colWidths=col_widths, repeatRows=1)
t.setStyle(style)

generated = datetime.now().strftime("%Y-%m-%d %H:%M")
elements = [
    Paragraph("Farm2Kitchen Halal — FCFS Order Priority Report", title_style),
    Paragraph(f"Generated: {generated} &nbsp;|&nbsp; Orders closed &nbsp;|&nbsp; Total orders: {len(orders)}", sub_style),
    t,
]

doc.build(elements)
print(f"PDF saved: {OUTPUT}")
