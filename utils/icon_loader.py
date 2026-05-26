import os
import customtkinter as ctk
from PIL import Image, ImageColor

# =========================
# PATH
# =========================

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

ICONS_DIR = os.path.join(
    BASE_DIR,
    "assets",
    "icons"
)

PRODUCT_IMAGES_DIR = os.path.join(
    BASE_DIR,
    "assets",
    "images",
    "products"
)

DEFAULT_PRODUCT_IMAGE = os.path.join(
    PRODUCT_IMAGES_DIR,
    "default_food.png"
)

# =========================
# ICON MAP
# =========================

ICONS = {
    "home": "house",
    "dashboard": "house",

    "cart": "shopping-cart",
    "order": "shopping-cart",

    "coffee": "coffee",

    "product": "utensils",
    "menu": "utensils",
    "utensils": "utensils",

    "history": "history",

    "receipt": "receipt-text",
    "invoice": "receipt-text",

    "report": "chart-column",
    "chart": "chart-column",
    "statistics": "chart-column",

    "money": "circle-dollar-sign",
    "revenue": "circle-dollar-sign",
    "dollar": "circle-dollar-sign",

    "shopping-bag": "shopping-bag",

    "user": "user",
    "users": "user",

    "trophy": "trophy",
    "top": "trophy",

    "flame": "flame",
    "hot": "flame",

    "plus": "plus",
    "add": "plus",

    "logout": "log-out",
    "log-out": "log-out"
}

# =========================
# EMOJI FALLBACK
# =========================

# LUCIDE_EMOJI = {
#     "house": "⌂",
#     "shopping-cart": "🛒",
#     "coffee": "☕",
#     "utensils": "🍽️",
#     "history": "↺",
#     "receipt-text": "🧾",
#     "chart-column": "📊",
#     "user": "👤",
#     "log-out": "↪",
#     "circle-dollar-sign": "💰",
#     "shopping-bag": "🛍️",
#     "trophy": "🏆",
#     "flame": "🔥",
#     "plus": "+"
# }


# =========================
# TEXT FALLBACK
# =========================

def icon_text(name, label=""):
    """
    Trả về text fallback khi không gắn được icon ảnh
    """
    if label:
        return label

    return "•"


# =========================
# LOAD IMAGE
# =========================

def load_ctk_image(path, size=(64, 64)):
    """
    Load ảnh thành CTkImage
    """

    try:

        if not path:
            return None

        if not os.path.isabs(path):
            path = os.path.join(BASE_DIR, path)

        if not os.path.exists(path):
            return None

        image = Image.open(path).convert("RGBA")

        return ctk.CTkImage(
            light_image=image,
            dark_image=image,
            size=size
        )

    except Exception as e:
        print(f"[IMAGE ERROR] {path}")
        print(e)
        return None


# =========================
# LOAD ICON
# =========================

def load_icon(name, size=(22, 22)):
    """
    Ví dụ:

    load_icon("home")
    load_icon("cart")
    load_icon("report")
    load_icon("money")
    load_icon("user")
    """

    icon_name = ICONS.get(
        name,
        name
    )

    extensions = [
        ".png",
        ".jpg",
        ".jpeg"
    ]

    for ext in extensions:

        icon_path = os.path.join(
            ICONS_DIR,
            f"{icon_name}{ext}"
        )

        icon = load_ctk_image(
            icon_path,
            size
        )

        if icon:
            return icon

    print(
        f"[ICON NOT FOUND] {icon_name}"
    )

    return None


def load_tinted_icon(name, size=(22, 22), color="#D97706"):
    icon_name = ICONS.get(
        name,
        name
    )

    extensions = [
        ".png",
        ".jpg",
        ".jpeg"
    ]

    for ext in extensions:
        icon_path = os.path.join(
            ICONS_DIR,
            f"{icon_name}{ext}"
        )

        if not os.path.exists(icon_path):
            continue

        try:
            image = Image.open(icon_path).convert("RGBA")
            alpha = image.getchannel("A")
            tinted = Image.new(
                "RGBA",
                image.size,
                ImageColor.getrgb(color) + (0,)
            )
            tinted.putalpha(alpha)

            return ctk.CTkImage(
                light_image=tinted,
                dark_image=tinted,
                size=size
            )
        except Exception as e:
            print(f"[ICON TINT ERROR] {icon_path}")
            print(e)

    return load_icon(name, size)


# =========================
# PRODUCT IMAGE
# =========================

def load_product_image(
        image_path=None,
        size=(180, 120)
):
    """
    Load ảnh sản phẩm

    Nếu không có ảnh:
    -> default_food.png
    """

    if image_path:

        if not os.path.isabs(image_path):

            image_path = os.path.join(
                PRODUCT_IMAGES_DIR,
                image_path
            )

        image = load_ctk_image(
            image_path,
            size
        )

        if image:
            return image

    return load_ctk_image(
        DEFAULT_PRODUCT_IMAGE,
        size
    )