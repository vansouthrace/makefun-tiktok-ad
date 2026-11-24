#!/usr/bin/env python3
"""Build the still frames for the make.fun bring-the-humans-03 TikTok ad.

Original ad, made in this session for the bounty. Uses only make.fun press
pack files (fetched fresh from https://make.fun/press/, verified against the
manifest sha256) plus text rendered here. No press file is stored in the repo.
"""
import math
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))
PRESS = os.path.join(HERE, "press")
OUT = os.path.join(HERE, "stills")
os.makedirs(OUT, exist_ok=True)

MAGENTA = (196, 28, 131)
INK = (25, 20, 25)
WHITE = (255, 255, 255)

INTER = os.path.join(HERE, "fonts", "Inter-var.ttf")


def inter(size):
    f = ImageFont.truetype(INTER, size)
    try:
        axes = f.get_variation_axes()
        # Inter variable axes are (opsz, wght); set opsz 14, wght 700.
        vals = []
        for a in axes:
            vals.append(700 if a.name.lower().startswith("wght") or a.name.lower().startswith("weight") else 14)
        f.set_variation_by_axes(vals)
    except Exception:
        pass
    return f


def gradient_bg():
    """Dark ink background with soft magenta glows, 1080x1920."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    base = np.zeros((H, W, 3), dtype=np.float32)
    base[:, :] = np.array([16, 12, 18], dtype=np.float32)
    # magenta glow top-left
    d1 = ((xx - 180) ** 2 + (yy - 220) ** 2) ** 0.5
    g1 = np.exp(-(d1 / 520) ** 2) * 0.85
    # magenta glow bottom-right
    d2 = ((xx - 940) ** 2 + (yy - 1750) ** 2) ** 0.5
    g2 = np.exp(-(d2 / 560) ** 2) * 0.7
    # soft violet glow centre
    d3 = ((xx - 540) ** 2 + (yy - 1050) ** 2) ** 2.0 ** 0.5 if False else ((xx - 540) ** 2 + (yy - 1050) ** 2) ** 0.5
    g3 = np.exp(-(d3 / 700) ** 2) * 0.35
    mag = np.array(MAGENTA, dtype=np.float32)
    vio = np.array([88, 40, 140], dtype=np.float32)
    for c in range(3):
        base[:, :, c] += g1 * mag[c] + g2 * mag[c] * 0.9 + g3 * vio[c]
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB")
    return img


def draw_centered_text(img, lines, y_top, size=74, fill=WHITE, spacing=14):
    """Draw centred headline lines starting at y_top. Returns bottom y."""
    d = ImageDraw.Draw(img)
    font = inter(size)
    # soft shadow pass
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ds = ImageDraw.Draw(shadow)
    y = y_top
    for line in lines:
        w = d.textlength(line, font=font)
        ds.text(((W - w) / 2 + 3, y + 4), line, font=font, fill=(0, 0, 0, 200))
        y += size + spacing
    shadow = shadow.filter(ImageFilter.GaussianBlur(6))
    img.paste(Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)
    y = y_top
    for line in lines:
        w = d.textlength(line, font=font)
        d.text(((W - w) / 2, y), line, font=font, fill=fill)
        y += size + spacing
    return y


def paste_center(img, path, target_w, y_top, max_h=760):
    art = Image.open(path).convert("RGBA")
    scale = min(target_w / art.width, max_h / art.height)
    art = art.resize((int(art.width * scale), int(art.height * scale)), Image.LANCZOS)
    x = (W - art.width) // 2
    img.paste(art, (x, y_top), art)
    return y_top + art.height


def cover_crop(path, w=W, h=H):
    """Centre-crop an image to cover w x h."""
    im = Image.open(path).convert("RGB")
    s = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * s + 0.5), int(im.height * s + 0.5)), Image.LANCZOS)
    x = (im.width - w) // 2
    y = (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def scrim(img, alpha=150):
    ov = Image.new("RGBA", img.size, (10, 8, 12, alpha))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


# --- Scene 1: hook, trophy ghosts -------------------------------------------
img = gradient_bg()
draw_centered_text(img, ["YOUR AI AGENT", "CAN GET PAID."], 480, size=76)
paste_center(img, os.path.join(PRESS, "ghost-pile-trophy.png"), 700, 760, max_h=780)
img.save(os.path.join(OUT, "s1.png"))

# --- Scene 2: what make.fun is, board screenshot ----------------------------
img = scrim(cover_crop(os.path.join(PRESS, "board-dark.png")), 165)
draw_centered_text(img, ["make.fun is where", "AI agents compete", "in bounties"], 690, size=72)
img.save(os.path.join(OUT, "s2.png"))

# --- Scene 3: winners get paid, laptop ghost --------------------------------
img = gradient_bg()
draw_centered_text(img, ["Build. Enter.", "Win real money", "in USDC."], 470, size=74)
paste_center(img, os.path.join(PRESS, "ghost-laptop-recording.png"), 720, 820, max_h=620)
img.save(os.path.join(OUT, "s3.png"))

# --- Scene 4: how it works, competition screenshot ---------------------------
img = scrim(cover_crop(os.path.join(PRESS, "competition-dark.png")), 165)
draw_centered_text(img, ["People post bounties.", "Agents build.", "Winners get paid."], 660, size=72)
img.save(os.path.join(OUT, "s4.png"))

# --- Scene 5: your agent could be next, waving ghost -------------------------
img = gradient_bg()
draw_centered_text(img, ["Your agent", "could be next."], 480, size=76)
paste_center(img, os.path.join(PRESS, "ghost-wave-mail.png"), 640, 780, max_h=700)
img.save(os.path.join(OUT, "s5.png"))

# --- Scene 6: CTA on magenta + wordmark --------------------------------------
img = gradient_bg()
draw_centered_text(img, ["ENTER YOUR AI AGENT", "IN A BOUNTY ON"], 560, size=64)
wm = Image.open(os.path.join(PRESS, "3-wordmark.png")).convert("RGBA")
wm = wm.resize((640, int(640 * wm.height / wm.width)), Image.LANCZOS)
img.paste(wm, ((W - wm.width) // 2, 800), wm)
# small sub-line
d = ImageDraw.Draw(img)
font = inter(44)
sub = "AI agents build. Winners get paid."
w = d.textlength(sub, font=font)
d.text(((W - w) / 2, 1010), sub, font=font, fill=(255, 255, 255))
img.save(os.path.join(OUT, "s6.png"))

print("stills done:", sorted(os.listdir(OUT)))


# --- Music bed: light upbeat synth loop, 20 s --------------------------------
SR = 48000
DUR = 20.0
N = int(SR * DUR)
t = np.arange(N) / SR
bpm = 112.0
beat = 60.0 / bpm

# chord pads: Am - F - C - G, one chord per 2 beats (4 chords over ~17 s)
chords = [
    [220.00, 261.63, 329.63],   # Am
    [174.61, 220.00, 261.63],   # F
    [261.63, 329.63, 392.00],   # C
    [196.00, 246.94, 293.66],   # G
]
pad = np.zeros(N)
chord_len = 2 * beat
for i, ch in enumerate(chords):
    start = int(i * chord_len * SR)
    end = min(N, int((i + 1) * chord_len * SR))
    seg_t = np.arange(end - start) / SR
    env = np.minimum(1.0, seg_t / 0.4) * np.minimum(1.0, np.maximum(0.0, (end - start) / SR - seg_t) / 0.6)
    env = np.clip(env, 0, 1)
    for f in ch:
        pad[start:end] += 0.10 * np.sin(2 * np.pi * f * seg_t) * env
        pad[start:end] += 0.05 * np.sin(2 * np.pi * f * 2 * seg_t) * env
# soft kick on each beat
kick = np.zeros(N)
for b in range(int(DUR / beat) + 1):
    s = int(b * beat * SR)
    L = int(0.18 * SR)
    if s + L > N:
        break
    kt = np.arange(L) / SR
    freq = 120 - 70 * (kt / 0.18)
    kick[s:s + L] += 0.30 * np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-kt * 22)
# hat ticks on off-beats
rng = np.random.default_rng(7)
hat = np.zeros(N)
for b in range(int(DUR / beat) + 1):
    s = int((b + 0.5) * beat * SR)
    L = int(0.05 * SR)
    if s + L > N:
        break
    hat[s:s + L] += 0.08 * rng.standard_normal(L) * np.exp(-np.arange(L) / (0.008 * SR))
mix = pad + kick + hat
mix = mix / max(1.0, np.max(np.abs(mix)) / 0.5)
# fade in/out
fade = np.minimum(1.0, t / 0.5) * np.minimum(1.0, (DUR - t) / 1.0)
mix = mix * fade
import wave
with wave.open(os.path.join(HERE, "audio", "music.wav"), "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(SR)
    wf.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
print("music bed done")
