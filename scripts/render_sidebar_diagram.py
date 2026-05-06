"""Render web sidebar -> backend container diagram as PNG."""
from PIL import Image, ImageDraw, ImageFont
import os

# ---------------------------------------------------------------- data
GROUPS = [
    ("Overview", "#1565c0", [
        ("/dashboard", "Kong -> aggregator"),
    ]),
    ("Farm Management", "#2e7d32", [
        ("/farms",      "field-management-service:3000"),
        ("/fields",     "field-management-service:3000"),
        ("/crops",      "field-management-service:3000"),
        ("/seasons",    "field-management-service:3000"),
        ("/inventory",  "inventory-service:8116"),
        ("/tasks",      "task-service:8103  (proxy)"),
        ("/scouting",   "pest-detection-service:8125  (proxy)"),
    ]),
    ("Water & Irrigation", "#0277bd", [
        ("/irrigation",        "irrigation-smart:8094  (proxy)"),
        ("/pivot-irrigation",  "irrigation-cycle-engine:8250"),
    ]),
    ("Crop Intelligence", "#558b2f", [
        ("/crop-health",                  "crop-intelligence-service:8095"),
        ("/diseases",                     "advisory-service:8093 + pest-detection:8125"),
        ("/weather",                      "weather-service:8092  (proxy)"),
        ("/satellite",                    "vegetation-analysis-service:8090  (proxy)"),
        ("/satellite-monitor",            "vegetation-analysis-service:8090"),
        ("/yield",                        "yield-prediction-service:8152"),
        ("/precision-agriculture/gdd",    "indicators-service:8091"),
        ("/crop-protection",              "advisory-service:8093"),
        ("/crop-planning",                "crop-growth-model:3023"),
        ("/epidemic",                     "alert-service:8113"),
        ("/vision",                       "yolo26-vision-service:8150"),
        ("/soil-map",                     "soil-analysis-service:8134"),
        ("/terrain",                      "terrain-core-service:8185  (proxy)"),
        ("/soil-analysis",                "soil-analysis-service:8134  (proxy)"),
    ]),
    ("IoT & Equipment", "#6a1b9a", [
        ("/iot",             "iot-service:8117"),
        ("/sensors",         "iot-sensor-hub:8251"),
        ("/equipment",       "equipment-service:8101  (proxy)"),
        ("/drone",           "drone-service:8126"),
        ("/edge-devices",    "edge-orchestrator-service:8180"),
        ("/virtual-sensors", "virtual-sensors:8119"),
    ]),
    ("Precision Ag", "#00838f", [
        ("/precision-agriculture/spray",      "advisory-service:8093"),
        ("/precision-agriculture/vra",        "drone-service:8126"),
        ("/precision-agriculture/fertilizer", "advisory-service:8093"),
    ]),
    ("Business & Community", "#ef6c00", [
        ("/marketplace",     "marketplace-service:3010"),
        ("/wallet",          "billing-core:8089"),
        ("/community",       "chat-service:8115"),
        ("/logistics",       "logistics-service:8167"),
        ("/market-prices",   "supply-chain-service:8230"),
        ("/cooperatives",    "cooperative-service:8127"),
        ("/crop-insurance",  "billing-core:8089"),
        ("/traceability",    "traceability-service:8123"),
        ("/harvest-quality", "globalgap-compliance:8128"),
    ]),
    ("Reports & Docs", "#4527a0", [
        ("/reports",                "field-intelligence:8120"),
        ("/analytics",              "field-intelligence:8120"),
        ("/documents",              "field-management-service:3000"),
        ("/analytics/field-compare", "field-intelligence:8120"),
        ("/reports/seasonal",       "field-intelligence:8120"),
    ]),
    ("Alerts & Notifications", "#c62828", [
        ("/alerts",               "alert-service:8113  (proxy)"),
        ("/notifications",        "notification-service:8110"),
        ("/disaster-assessment",  "disaster-assessment:3020"),
    ]),
    ("Tools", "#37474f", [
        ("/copilot",  "copilot-api:8088"),
        ("/support",  "chat-service:8115"),
        ("/settings", "user-service:3025"),
        ("/audit",    "audit-service:8114"),
        ("/seeds",    "field-management-service:3000"),
    ]),
]

# ---------------------------------------------------------------- layout
W = 1800
PAD = 30
COL_GAP = 30
HEADER_H = 200

# Two columns of group cards
COL_W = (W - PAD * 2 - COL_GAP) // 2

# Fonts (Windows fallback)
def load_font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

F_TITLE   = load_font(34, bold=True)
F_SUB     = load_font(18)
F_GROUP   = load_font(20, bold=True)
F_ROUTE   = load_font(15, bold=True)
F_SVC     = load_font(14)
F_LBL     = load_font(16, bold=True)

ROW_H = 40
GROUP_HEADER_H = 44
GROUP_PAD = 10

# Compute group heights and split into two columns balanced
def group_height(g):
    return GROUP_HEADER_H + len(g[2]) * ROW_H + GROUP_PAD

heights = [group_height(g) for g in GROUPS]
# Greedy split into two columns
col1, col2 = [], []
h1 = h2 = 0
for g, h in zip(GROUPS, heights):
    if h1 <= h2:
        col1.append((g, h)); h1 += h + 18
    else:
        col2.append((g, h)); h2 += h + 18

H = HEADER_H + max(h1, h2) + PAD * 2 + 60

img = Image.new("RGB", (W, H), "#fafafa")
d = ImageDraw.Draw(img)

# ---------------------------------------------------------------- header
def round_rect(xy, radius, fill, outline=None, width=1):
    d.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

# Title
d.text((PAD, PAD), "SAHOOL Web App  -  Sidebar Routes -> Backend Containers",
       font=F_TITLE, fill="#1b5e20")
d.text((PAD, PAD + 44),
       "apps/web/src/components/layouts/sidebar.tsx   |   verified against apps/web/src/app/api/*/route.ts",
       font=F_SUB, fill="#555")

# Web app + gateway boxes
def label_box(x, y, w, h, title, sub, fill, text_fill="#fff"):
    round_rect((x, y, x + w, y + h), 12, fill, outline="#222", width=2)
    d.text((x + 14, y + 10), title, font=F_LBL, fill=text_fill)
    d.text((x + 14, y + 32), sub, font=F_SUB, fill=text_fill)

ybar = PAD + 88
box_w = 320
label_box(PAD,                       ybar, box_w, 70, "apps/web", "Next.js 15 / React 19", "#1b5e20")
label_box(PAD + box_w + 30,          ybar, box_w, 70, "Kong API Gateway", "port 8000  (client-side calls)", "#bf360c")
label_box(PAD + (box_w + 30) * 2,    ybar, box_w, 70, "Next.js /api/*", "server-side proxy  ->  service:port", "#0d47a1")
# Arrow from web -> kong / proxy
d.line((PAD + box_w, ybar + 35, PAD + box_w + 30, ybar + 35), fill="#222", width=3)
d.line((PAD + box_w * 2 + 30, ybar + 35, PAD + box_w * 2 + 60, ybar + 35), fill="#222", width=3)

# Legend
lx = PAD + (box_w + 30) * 3 + 30
d.text((lx, ybar + 4), "Legend", font=F_LBL, fill="#222")
d.rectangle((lx, ybar + 28, lx + 18, ybar + 46), fill="#cfd8dc", outline="#222")
d.text((lx + 24, ybar + 28), "(proxy) = via Next.js /api route", font=F_SUB, fill="#222")
d.rectangle((lx, ybar + 50, lx + 18, ybar + 68), fill="#fff", outline="#222")
d.text((lx + 24, ybar + 50), "(no tag) = via Kong gateway", font=F_SUB, fill="#222")

# ---------------------------------------------------------------- group cards
def draw_group(x, y, group):
    name, color, items = group
    h = GROUP_HEADER_H + len(items) * ROW_H + GROUP_PAD
    # card
    round_rect((x, y, x + COL_W, y + h), 10, "#ffffff", outline="#bbb", width=1)
    # header bar
    round_rect((x, y, x + COL_W, y + GROUP_HEADER_H), 10, color)
    # bottom-correct header bar (so only top is rounded)
    d.rectangle((x, y + GROUP_HEADER_H - 12, x + COL_W, y + GROUP_HEADER_H), fill=color)
    d.text((x + 14, y + 10), name, font=F_GROUP, fill="#fff")
    d.text((x + COL_W - 90, y + 14), f"{len(items)} pages", font=F_SUB, fill="#fff")

    yy = y + GROUP_HEADER_H + 4
    for i, (route, svc) in enumerate(items):
        if i % 2 == 0:
            d.rectangle((x + 1, yy, x + COL_W - 1, yy + ROW_H), fill="#f4f7f6")
        d.text((x + 14, yy + 8), route, font=F_ROUTE, fill="#222")
        # arrow
        ax = x + 240
        d.line((ax, yy + ROW_H // 2, ax + 22, yy + ROW_H // 2), fill=color, width=2)
        d.polygon([(ax + 22, yy + ROW_H // 2 - 5),
                   (ax + 30, yy + ROW_H // 2),
                   (ax + 22, yy + ROW_H // 2 + 5)], fill=color)
        d.text((x + 280, yy + 10), svc, font=F_SVC, fill="#0d47a1")
        yy += ROW_H

def draw_column(x, items_with_h, y0):
    y = y0
    for g, h in items_with_h:
        draw_group(x, y, g)
        y += h + 18

y_start = ybar + 100
draw_column(PAD,                          col1, y_start)
draw_column(PAD + COL_W + COL_GAP,        col2, y_start)

# Footer
d.text((PAD, H - PAD - 18),
       "Source of truth: docker-compose.yml service ports + governance/services.yaml v3.3.0",
       font=F_SUB, fill="#666")

out = r"D:\projects\v91\sahoo-adel-full\docs\diagrams\web-sidebar-to-backend.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
img.save(out, "PNG")
print(f"WROTE {out}  ({W}x{H})")
