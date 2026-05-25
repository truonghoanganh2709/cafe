import os
import customtkinter as ctk
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ICONS_DIR = os.path.join(BASE_DIR, "assets", "icons")
PRODUCT_IMAGES_DIR = os.path.join(BASE_DIR, "assets", "images", "products")
DEFAULT_PRODUCT_IMAGE = os.path.join(PRODUCT_IMAGES_DIR, "default_food.png")

LUCIDE_EMOJI = {
    "home": "⌂",
    "shopping-cart": "🛒",
    "coffee": "☕",
    "utensils": "🍽️",
    "history": "↺",
    "receipt": "🧾",
    "chart-column": "📊",
    "users": "👥",
    "log-out": "↪",
    "dollar-sign": "💰",
    "shopping-bag": "🛍️",
    "trophy": "🏆",
    "flame": "🔥",
    "plus": "+",
}


def icon_text(name, label=""):
    # Trả về chuỗi icon unicode theo phong cách lucide kèm nhãn.
    icon = LUCIDE_EMOJI.get(name, "•")
    return f"{icon}  {label}" if label else icon


def load_ctk_image(path, size=(64, 64)):
    # Load ảnh PNG/JPG bằng PIL rồi chuyển sang CTkImage; lỗi thì trả None.
    if not path:
        return None
    if not os.path.isabs(path):
        path = os.path.join(BASE_DIR, path)
    if not os.path.exists(path):
        return None
    try:
        image = Image.open(path).convert("RGBA")
        return ctk.CTkImage(light_image=image, dark_image=image, size=size)
    except Exception:
        return None


def load_icon(name, size=(22, 22)):
    # Ưu tiên icon PNG trong assets/icons, nếu không có thì view dùng emoji fallback.
    for ext in [".png", ".jpg", ".jpeg"]:
        icon_path = os.path.join(ICONS_DIR, f"{name}{ext}")
        image = load_ctk_image(icon_path, size)
        if image:
            return image
    return None


def load_product_image(image_path="", size=(180, 110)):
    # Load ảnh món ăn; nếu sản phẩm chưa có ảnh thì dùng default_food.png.
    image = load_ctk_image(image_path, size)
    if image:
        return image
    return load_ctk_image(DEFAULT_PRODUCT_IMAGE, size)
