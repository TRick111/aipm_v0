"""Add red highlight boxes to Dashboard screenshots that didn't get them via CSS injection."""
from PIL import Image, ImageDraw

BASE = "/Users/rikutanaka/aipm_v0/Flow/202605/2026-05-23/RestaurantAILab/BFA/screenshots"
RED = (239, 68, 68)
RED_FILL = (239, 68, 68, 40)

def annotate(src_name, out_name, boxes):
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
        for w in range(8, 0, -2):
            alpha = max(40, 80 - w*6)
            draw.rectangle((box[0]-w, box[1]-w, box[2]+w, box[3]+w), outline=(239, 68, 68, alpha), width=2)
        draw.rectangle(box, outline=RED, width=4)
    out_img.convert("RGB").save(out, "PNG")
    print(f"saved: {out}")

# 03-upload-step1-empty.png (1280x900): file selection dashed area
annotate(
    "03-upload-step1-empty.png",
    "03-upload-step1-empty-annot.png",
    [
        (110, 444, 1170, 614),  # dashed file select container
    ],
)

# 04-upload-step1-filled.png (1265x1254): Airレジ radio card + 次へ（プレビュー）button
annotate(
    "04-upload-step1-filled.png",
    "04-upload-step1-filled-annot.png",
    [
        (108, 770, 1172, 854),     # Airレジ形式 card
        (108, 1148, 1172, 1210),   # 次へ（プレビュー）button
    ],
)

print("done")
