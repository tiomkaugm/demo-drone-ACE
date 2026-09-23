import numpy as np
from PIL import Image, ImageDraw, ImageFont


def generate_text_targets(text: str, n_drones: int, canvas_width: int = 800, canvas_height: int = 300) -> np.ndarray:
    """
    Me-render teks ke kanvas 2D dan mengekstrak N titik target koordinat di udara.
    """
    if not text.strip():
        text = "UGM"


    # Buat kanvas biner (hitam-putih)
    img = Image.new("1", (canvas_width, canvas_height), 0)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    # Hitung batas dimensi teks
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Skala proporsional agar mengisi kanvas
    scale = min((canvas_width * 0.75) / max(text_w, 1), (canvas_height * 0.65) / max(text_h, 1))
    scale_w = int(max(text_w * scale, 10))
    scale_h = int(max(text_h * scale, 10))

    img_temp = Image.new("1", (max(text_w, 1), max(text_h, 1)), 0)
    draw_temp = ImageDraw.Draw(img_temp)
    draw_temp.text((-bbox[0], -bbox[1]), text, fill=1, font=font)

    img_resized = img_temp.resize((scale_w, scale_h), Image.Resampling.NEAREST)
    offset_x = (canvas_width - scale_w) // 2
    offset_y = (canvas_height - scale_h) // 2
    img.paste(img_resized, (offset_x, offset_y))

    # Ekstrak piksel teks yang menyala
    pixels = np.array(img)
    y_coords, x_coords = np.where(pixels > 0)

    if len(x_coords) == 0:
        x_coords = np.random.uniform(0, canvas_width, n_drones)
        y_coords = np.random.uniform(0, canvas_height, n_drones)

    # Sampling tepat N titik
    indices = np.random.choice(len(x_coords), size=n_drones, replace=(len(x_coords) < n_drones))

    # Konversi koordinat piksel ke satuan meter di udara
    target_x = ((x_coords[indices].astype(float) / canvas_width) - 0.5) * 200.0
    target_z = 30.0 + ((canvas_height - y_coords[indices]).astype(float) / canvas_height) * 60.0
    target_y = np.zeros(n_drones)  # Kanvas 2D display di y = 0

    return np.column_stack((target_x, target_y, target_z))
