from pathlib import Path
import math
import textwrap

from PIL import Image, ImageDraw, ImageFont, ImageOps
import qrcode


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
OUTDIR = ROOT / "poster"
OUTDIR.mkdir(exist_ok=True)

WIDTH = 1600
HEIGHT = 2400

BG = "#f6f3ff"
LILAC = "#c9c6e8"
LILAC_DEEP = "#adb0db"
WHITE = "#ffffff"
INK = "#18181c"
MUTED = "#4c5060"
ACCENT = "#226f79"
ACCENT_2 = "#7c4fd0"
GOLD = "#d5843f"

URL = "https://cv-ac.github.io/SEI_HHAI2026/"


def load_font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


FONT_BOLD = load_font(ASSETS / "fonts" / "RobotoSlab-Bold.ttf", 28)
FONT_TITLE = load_font(ASSETS / "fonts" / "RobotoSlab-Bold.ttf", 78)
FONT_TITLE_SMALL = load_font(ASSETS / "fonts" / "RobotoSlab-Bold.ttf", 58)
FONT_H2 = load_font(ASSETS / "fonts" / "RobotoSlab-Bold.ttf", 42)
FONT_H3 = load_font(ASSETS / "fonts" / "RobotoSlab-Bold.ttf", 30)
FONT_BODY = load_font(ASSETS / "fonts" / "PT_Sans-Web-Regular.ttf", 28)
FONT_BODY_SMALL = load_font(ASSETS / "fonts" / "PT_Sans-Web-Regular.ttf", 24)
FONT_BODY_BOLD = load_font(ASSETS / "fonts" / "PT_Sans-Web-Bold.ttf", 28)
FONT_SMALL = load_font(ASSETS / "fonts" / "PT_Sans-Web-Regular.ttf", 22)
FONT_SMALL_BOLD = load_font(ASSETS / "fonts" / "PT_Sans-Web-Bold.ttf", 22)


def fit_text(draw, text, max_width, start_font, min_size=28, line_spacing=10):
    size = start_font.size
    font_path = start_font.path
    while size >= min_size:
        font = ImageFont.truetype(font_path, size=size)
        wrapped = wrap_text(draw, text, font, max_width)
        bbox = draw.multiline_textbbox((0, 0), wrapped, font=font, spacing=line_spacing)
        if bbox[2] - bbox[0] <= max_width:
            return font, wrapped
        size -= 2
    font = ImageFont.truetype(font_path, size=min_size)
    return font, wrap_text(draw, text, font, max_width)


def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        w = draw.textbbox((0, 0), trial, font=font)[2]
        if w <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return "\n".join(lines)


def draw_wrapped(draw, xy, text, font, fill, max_width, spacing=10):
    wrapped = wrap_text(draw, text, font, max_width)
    draw.multiline_text(xy, wrapped, font=font, fill=fill, spacing=spacing)
    bbox = draw.multiline_textbbox(xy, wrapped, font=font, spacing=spacing)
    return bbox


def rounded_box(draw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def make_qr(url: str, size: int) -> Image.Image:
    qr = qrcode.QRCode(border=2, box_size=12, error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    return img.resize((size, size), Image.Resampling.NEAREST)


def cover_crop(img: Image.Image, size):
    return ImageOps.fit(img.convert("RGB"), size, Image.Resampling.LANCZOS)


img = Image.new("RGB", (WIDTH, HEIGHT), BG)
draw = ImageDraw.Draw(img)

# soft background accents
draw.ellipse((-120, 220, 700, 1100), fill="#ece9ff")
draw.ellipse((980, -80, 1700, 620), fill="#efe9ff")
draw.ellipse((1030, 1400, 1800, 2260), fill="#ece9ff")

# top ribbons / badges
rounded_box(draw, (70, 56, 325, 176), 28, fill=GOLD)
draw.text((110, 90), "HHAI", font=FONT_H2, fill=WHITE)
draw.text((235, 90), "2026", font=FONT_H2, fill=WHITE)

rounded_box(draw, (380, 56, 620, 176), 28, fill=WHITE, outline="#d7d2ef", width=2)
draw.text((437, 92), "SEI", font=FONT_H2, fill=ACCENT_2)

draw.text((800, 90), "Social & Embodied Intelligence", font=FONT_H3, fill=ACCENT, anchor="ma")
draw.text((800, 132), "for Multimodal Human-AI Interaction", font=FONT_H3, fill=INK, anchor="ma")

# title
draw.text((800, 245), "HHAI 2026 Workshop", font=FONT_H2, fill=ACCENT, anchor="ma")
title = "Social & Embodied Intelligence for\nMultimodal Human-AI Interaction"
draw.multiline_text((800, 320), title, font=FONT_TITLE_SMALL, fill=INK, anchor="ma", align="center", spacing=18)
draw.text((800, 500), "July 7, 2026  ·  Brussels, Belgium  ·  Workshop Day 2 (Afternoon)", font=FONT_BODY_BOLD, fill=MUTED, anchor="ma")

# website + qr
qr = make_qr(URL, 245)
img.paste(qr, (1260, 275))
draw.text((1195, 555), "Website", font=FONT_SMALL_BOLD, fill=INK, anchor="ra")
draw.text((1215, 555), URL, font=FONT_SMALL_BOLD, fill=ACCENT_2, anchor="la")

# overview
rounded_box(draw, (80, 610, 1520, 835), 36, fill=WHITE, outline="#ded8f0", width=2)
draw.text((800, 650), "Workshop Overview", font=FONT_H2, fill=INK, anchor="ma")
overview = (
    "This half-day workshop brings together research on multimodal perception, affective computing, "
    "speech and vision, embodied AI, and human-centered interaction design. We focus on AI systems that "
    "can perceive, interpret, and generate socially relevant multimodal behavior for more natural human-AI interaction."
)
draw_wrapped(draw, (145, 715), overview, FONT_BODY, MUTED, 1310, spacing=10)

# two column sections
left_x1, left_x2 = 80, 760
right_x1, right_x2 = 840, 1520
top_y, box_h = 890, 740
rounded_box(draw, (left_x1, top_y, left_x2, top_y + box_h), 36, fill=LILAC, outline="#9ea6d7", width=2)
rounded_box(draw, (right_x1, top_y, right_x2, top_y + box_h), 36, fill=WHITE, outline="#ded8f0", width=2)

draw.text(((left_x1 + left_x2) // 2, top_y + 36), "Workshop Topics", font=FONT_H2, fill=INK, anchor="ma")
topic_sections = [
    ("Socially Intelligent AI", [
        "Emotion recognition, social signal understanding, and engagement modeling",
        "Affective computing and multimodal interaction",
    ]),
    ("Embodied and Interactive Systems", [
        "Embodied agents, digital humans, avatars, and social robots",
        "Adaptive and context-aware interactive systems",
    ]),
    ("Applications and Evaluation", [
        "Collaboration, healthcare, education, and accessibility",
        "Human-centered evaluation, ethics, trust, and social impact",
    ]),
]
y = top_y + 96
for title_s, bullets in topic_sections:
    draw.text((left_x1 + 40, y), title_s, font=FONT_BODY_BOLD, fill=ACCENT_2)
    y += 42
    for bullet in bullets:
        draw.text((left_x1 + 52, y), "•", font=FONT_BODY_BOLD, fill=INK)
        bbox = draw_wrapped(draw, (left_x1 + 82, y), bullet, FONT_BODY_SMALL, INK, left_x2 - left_x1 - 130, spacing=6)
        y = bbox[3] + 10
    y += 14

draw.text(((right_x1 + right_x2) // 2, top_y + 36), "Call for Contributions", font=FONT_H2, fill=INK, anchor="ma")
cfp_items = [
    ("Abstract (250 words)", "Presentation-focused summary of research focus or relevant studies."),
    ("Short Paper (5–9 pages)", "Work-in-progress findings or pilot study results."),
    ("Full Research Paper (10–12 pages)", "Comprehensive study results, empirical findings, or methodological advances."),
]
y = top_y + 96
for label, desc in cfp_items:
    draw.text((right_x1 + 40, y), label, font=FONT_BODY_BOLD, fill=ACCENT)
    y += 34
    bbox = draw_wrapped(draw, (right_x1 + 40, y), desc, FONT_BODY_SMALL, INK, right_x2 - right_x1 - 80, spacing=6)
    y = bbox[3] + 16

y += 8
draw.text((right_x1 + 40, y), "Important Dates", font=FONT_H3, fill=ACCENT_2)
y += 42
dates = [
    ("Mar 14, 2026", "Call for submissions"),
    ("May 15, 2026", "Submission deadline"),
    ("May 29, 2026", "Notification to authors"),
    ("Jun 5, 2026", "Camera-ready deadline"),
    ("Jul 7, 2026", "Workshop day"),
]
for date, desc in dates:
    draw.text((right_x1 + 40, y), date, font=FONT_SMALL_BOLD, fill=INK)
    draw.text((right_x1 + 220, y), desc, font=FONT_SMALL, fill=MUTED)
    y += 34

y += 18
draw.text((right_x1 + 40, y), "Submission", font=FONT_H3, fill=ACCENT_2)
y += 40
bbox = draw_wrapped(draw, (right_x1 + 40, y), "Website: " + URL, FONT_SMALL_BOLD, ACCENT, right_x2 - right_x1 - 80, spacing=6)
y = bbox[3] + 10
bbox = draw_wrapped(draw, (right_x1 + 40, y), "CMT: https://cmt3.research.microsoft.com/SEIHHAI2026", FONT_SMALL_BOLD, ACCENT, right_x2 - right_x1 - 80, spacing=6)

# organisers section
org_y = 1710
draw.text((800, org_y), "Organising Committee", font=FONT_H2, fill=INK, anchor="ma")
draw.text((800, org_y + 48), "University of Oulu and TU Delft", font=FONT_BODY, fill=MUTED, anchor="ma")

organisers = [
    ("Fang Kang", "University of Oulu", ASSETS / "organizers" / "fangkang.jpg"),
    ("Haoyu Chen", "University of Oulu", ASSETS / "organizers" / "chenhaoyu1.png"),
    ("Guoying Zhao", "University of Oulu", ASSETS / "organizers" / "guoying-1.JPG"),
    ("Stephanie Tan", "TU Delft", ASSETS / "organizers" / "Stephanie_an.jpg"),
    ("Yueyi Yang", "University of Oulu", ASSETS / "organizers" / "yueyiyang.jpg"),
]

card_w = 220
photo_size = (180, 180)
gap = 58
total_w = card_w * len(organisers) + gap * (len(organisers) - 1)
start_x = (WIDTH - total_w) // 2
card_y = 1825

for i, (name, aff, path) in enumerate(organisers):
    x = start_x + i * (card_w + gap)
    photo = cover_crop(Image.open(path), photo_size)
    img.paste(photo, (x + 20, card_y))
    draw.text((x + card_w // 2, card_y + 198), name, font=FONT_SMALL_BOLD, fill=INK, anchor="ma")
    wrapped_aff = wrap_text(draw, aff, FONT_SMALL, card_w - 10)
    draw.multiline_text((x + card_w // 2, card_y + 232), wrapped_aff, font=FONT_SMALL, fill=MUTED, anchor="ma", align="center", spacing=4)

# footer
footer_y = 2240
draw.line((100, footer_y, 1500, footer_y), fill="#d9d4ec", width=2)
draw.text((800, footer_y + 28), "Workshop website: " + URL, font=FONT_SMALL_BOLD, fill=ACCENT, anchor="ma")

png_path = OUTDIR / "SEI_HHAI2026_poster.png"
img.save(png_path, quality=95)
print(png_path)
