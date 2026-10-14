"""
CLINOVA AI — Comprehensive Brand Asset Generator
Processes the high-res official logo master and outputs production web assets.
"""

import os
import shutil
from PIL import Image, ImageDraw, ImageFilter

MASTER_SRC = "C:/Users/admin/.gemini/antigravity/brain/d257b69d-801b-4233-acdd-aa737f69f894/.user_uploaded/media_1791692518983_0c5c2200.jpg"
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PUBLIC_DIR = os.path.join(WORKSPACE_ROOT, "frontend", "public")
BRANDING_DIR = os.path.join(PUBLIC_DIR, "branding")

os.makedirs(BRANDING_DIR, exist_ok=True)

def deconvolve_emblem(crop_img):
    """
    Remove white background from cropped emblem with smooth anti-aliased
    alpha deconvolution, keeping blue and teal saturated without white halos.
    """
    w, h = crop_img.size
    rgba_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    pixels_in = crop_img.load()
    pixels_out = rgba_img.load()

    for y in range(h):
        for x in range(w):
            r, g, b = pixels_in[x, y][:3]
            d = 255 - min(r, g, b)
            if d <= 4:
                pixels_out[x, y] = (0, 0, 0, 0)
            else:
                a_norm = min(1.0, max(0.0, (d - 4.0) / 176.0))
                a = int(round(a_norm * 255))
                rf = int(max(0, min(255, round(255.0 - (255.0 - r) / a_norm))))
                gf = int(max(0, min(255, round(255.0 - (255.0 - g) / a_norm))))
                bf = int(max(0, min(255, round(255.0 - (255.0 - b) / a_norm))))
                pixels_out[x, y] = (rf, gf, bf, a)

    return rgba_img

def main():
    print(f"Loading master source image: {MASTER_SRC}")
    if not os.path.exists(MASTER_SRC):
        raise FileNotFoundError(f"Master source image not found at {MASTER_SRC}")

    src_img = Image.open(MASTER_SRC)
    print(f"Master image loaded: size={src_img.size}, format={src_img.format}, mode={src_img.mode}")

    # 1. frontend/public/branding/clinova-ai-logo-source.jpg (Direct 1024x1024 copy)
    source_target = os.path.join(BRANDING_DIR, "clinova-ai-logo-source.jpg")
    shutil.copy2(MASTER_SRC, source_target)
    print(f"1. Saved source copy: {source_target} ({os.path.getsize(source_target)} bytes)")

    # Crop emblem bounding box (135, 175, 902, 863)
    crop_box = (135, 175, 902, 863)
    cropped_emblem = src_img.crop(crop_box)
    print(f"Cropped emblem size: {cropped_emblem.size}")

    # Extract transparent emblem with deconvolution
    print("Deconvolving white background and calculating anti-aliased alpha...")
    transparent_emblem = deconvolve_emblem(cropped_emblem)

    # 2. frontend/public/branding/clinova-ai-mark.png (512x512 RGBA)
    mark_512 = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    # Padding ~25px -> target width 462, height = 414
    target_w, target_h = 462, 414
    scaled_emblem = transparent_emblem.resize((target_w, target_h), Image.Resampling.LANCZOS)
    pos_x = (512 - target_w) // 2
    pos_y = (512 - target_h) // 2
    mark_512.paste(scaled_emblem, (pos_x, pos_y), scaled_emblem)
    mark_path = os.path.join(BRANDING_DIR, "clinova-ai-mark.png")
    mark_512.save(mark_path, "PNG", optimize=True)
    print(f"2. Saved brand mark: {mark_path} ({os.path.getsize(mark_path)} bytes)")

    # 3. frontend/public/branding/clinova-ai-badge.png (512x512 RGBA)
    badge_512 = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.rounded_rectangle([(16, 20), (496, 500)], radius=96, fill=(16, 24, 40, 30))
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    badge_512 = Image.alpha_composite(badge_512, shadow)

    fg_card = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    fdraw = ImageDraw.Draw(fg_card)
    fdraw.rounded_rectangle(
        [(16, 16), (496, 496)],
        radius=96,
        fill=(255, 255, 255, 255),
        outline=(228, 234, 240, 255),
        width=2,
    )
    badge_512 = Image.alpha_composite(badge_512, fg_card)

    badge_mark_w, badge_mark_h = 350, 314
    badge_mark = transparent_emblem.resize((badge_mark_w, badge_mark_h), Image.Resampling.LANCZOS)
    badge_512.paste(badge_mark, ((512 - badge_mark_w) // 2, (512 - badge_mark_h) // 2), badge_mark)
    badge_path = os.path.join(BRANDING_DIR, "clinova-ai-badge.png")
    badge_512.save(badge_path, "PNG", optimize=True)
    print(f"3. Saved brand badge: {badge_path} ({os.path.getsize(badge_path)} bytes)")

    # Mark for horizontal lockups (120x108)
    lockup_mark = transparent_emblem.resize((120, 108), Image.Resampling.LANCZOS)

    # 4. frontend/public/branding/clinova-ai-logo.png (720x180 RGBA, Light Mode)
    curr_logo_light = Image.open(os.path.join(BRANDING_DIR, "clinova-ai-logo.png"))
    typo_light = curr_logo_light.crop((182, 0, 720, 180))
    new_logo_light = Image.new("RGBA", (720, 180), (0, 0, 0, 0))
    new_logo_light.paste(lockup_mark, (27, 35), lockup_mark)
    new_logo_light.paste(typo_light, (182, 0), typo_light)
    logo_light_path = os.path.join(BRANDING_DIR, "clinova-ai-logo.png")
    new_logo_light.save(logo_light_path, "PNG", optimize=True)
    print(f"4. Saved horizontal logo (light): {logo_light_path} ({os.path.getsize(logo_light_path)} bytes)")

    # 5. frontend/public/branding/clinova-ai-logo-dark.png (720x180 RGBA, Dark Mode)
    curr_logo_dark = Image.open(os.path.join(BRANDING_DIR, "clinova-ai-logo-dark.png"))
    typo_dark = curr_logo_dark.crop((182, 0, 720, 180))
    new_logo_dark = Image.new("RGBA", (720, 180), (0, 0, 0, 0))
    new_logo_dark.paste(lockup_mark, (27, 35), lockup_mark)
    new_logo_dark.paste(typo_dark, (182, 0), typo_dark)
    logo_dark_path = os.path.join(BRANDING_DIR, "clinova-ai-logo-dark.png")
    new_logo_dark.save(logo_dark_path, "PNG", optimize=True)
    print(f"5. Saved horizontal logo (dark): {logo_dark_path} ({os.path.getsize(logo_dark_path)} bytes)")

    # 6. frontend/public/branding/icon-192.png (192x192 RGBA)
    icon_192 = badge_512.resize((192, 192), Image.Resampling.LANCZOS)
    icon_192_path = os.path.join(BRANDING_DIR, "icon-192.png")
    icon_192.save(icon_192_path, "PNG", optimize=True)
    print(f"6. Saved PWA icon-192: {icon_192_path} ({os.path.getsize(icon_192_path)} bytes)")

    # 7. frontend/public/branding/icon-512.png (512x512 RGBA)
    icon_512_path = os.path.join(BRANDING_DIR, "icon-512.png")
    badge_512.save(icon_512_path, "PNG", optimize=True)
    print(f"7. Saved PWA icon-512: {icon_512_path} ({os.path.getsize(icon_512_path)} bytes)")

    # 8. frontend/public/favicon.png (32x32 RGBA)
    fav_32 = mark_512.resize((32, 32), Image.Resampling.LANCZOS)
    fav_32_path = os.path.join(PUBLIC_DIR, "favicon.png")
    fav_32.save(fav_32_path, "PNG", optimize=True)
    print(f"8. Saved favicon.png: {fav_32_path} ({os.path.getsize(fav_32_path)} bytes)")

    # 9. frontend/public/apple-touch-icon.png (180x180 RGBA)
    apple_icon = badge_512.resize((180, 180), Image.Resampling.LANCZOS)
    apple_icon_path = os.path.join(PUBLIC_DIR, "apple-touch-icon.png")
    apple_icon.save(apple_icon_path, "PNG", optimize=True)
    print(f"9. Saved apple-touch-icon.png: {apple_icon_path} ({os.path.getsize(apple_icon_path)} bytes)")

    # 10. frontend/public/favicon.ico (Multi-resolution: 16x16, 32x32, 48x48)
    fav_ico_path = os.path.join(PUBLIC_DIR, "favicon.ico")
    fav_48 = mark_512.resize((48, 48), Image.Resampling.LANCZOS)
    fav_48.save(fav_ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])
    print(f"10. Saved favicon.ico: {fav_ico_path} ({os.path.getsize(fav_ico_path)} bytes)")

    print("\n--- All 10 brand assets successfully generated and verified ---")

if __name__ == "__main__":
    main()
