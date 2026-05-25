"""Add red highlight boxes to Airレジ screenshots."""
from PIL import Image, ImageDraw

BASE = "/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-23/RestaurantAILab/BFA/screenshots"
RED = (239, 68, 68)
RED_FILL = (239, 68, 68, 40)  # semi-transparent

def annotate(src_name, out_name, boxes):
    """boxes: list of (x1,y1,x2,y2) tuples"""
    src = f"{BASE}/{src_name}"
    out = f"{BASE}/{out_name}"
    img = Image.open(src).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    for box in boxes:
        odraw.rectangle(box, fill=RED_FILL)
    out_img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(out_img)
    for box in boxes:
        # Draw outer glow first (lighter)
        glow = (box[0]-8, box[1]-8, box[2]+8, box[3]+8)
        for w in range(8, 0, -2):
            alpha = max(40, 80 - w*6)
            color = (239, 68, 68, alpha)
            # PIL rectangle width doesn't support alpha well; draw separate
            draw.rectangle((box[0]-w, box[1]-w, box[2]+w, box[3]+w), outline=color, width=2)
        # Main red rectangle
        draw.rectangle(box, outline=RED, width=4)
    out_img.convert("RGB").save(out, "PNG")
    print(f"saved: {out}")

# airregi-01-login (1280x900): AirID, Password, ログインボタン
annotate(
    "airregi-01-login.png",
    "airregi-01-login-annot.png",
    [
        (412, 184, 866, 226),   # AirID/email field
        (412, 253, 866, 295),   # Password field
        (412, 350, 866, 396),   # ログインボタン
    ],
)

# airregi-02-store-select: BAR FIVE Arrows row
annotate(
    "airregi-02-store-select.png",
    "airregi-02-store-select-annot.png",
    [
        (278, 252, 988, 310),   # BAR FIVE Arrows row
    ],
)

# airregi-03-top: 売上・分析 menu (already expanded) + 日別売上 link
annotate(
    "airregi-03-top.png",
    "airregi-03-top-annot.png",
    [
        (0, 397, 187, 433),     # 売上・分析 menu header
        (0, 442, 187, 480),     # 日別売上 link
    ],
)

# airregi-04-daily-sales: 集計対象+年月 selectors and 表示する + CSVダウンロードボタン
annotate(
    "airregi-04-daily-sales.png",
    "airregi-04-daily-sales-annot.png",
    [
        (332, 158, 660, 204),   # 日別/年/月 selectors row
        (818, 158, 922, 204),   # 表示する button
        (1043, 778, 1234, 814), # CSVデータをダウンロードする
    ],
)

# airregi-05-csv-download-menu: dropdown menu (会計明細 option needs to be highlighted)
# The menu shows 売上集計 visible; 会計明細 would be below — highlight the area where dropdown is
annotate(
    "airregi-05-csv-download-menu.png",
    "airregi-05-csv-download-menu-annot.png",
    [
        (1003, 838, 1240, 900), # 売上集計 row + indication that 会計明細 follows
    ],
)

# 06-upload-step3-mapping is currently identical to 03 (broken). Will need re-capture.
print("done")
