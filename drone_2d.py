import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.textpath import TextPath
from matplotlib.transforms import Affine2D
from matplotlib.path import Path
import re
import time


# Konfigurasi Halaman Streamlit
st.set_page_config(page_title="Word Formation & Morphing Animation", layout="centered")


st.title("🚁 Word Formation & Morphing Animation")
st.write("Aplikasi web interaktif untuk simulasi formasi kata dan *morphing* titik/drone berdasarkan skrip matplotlib[cite: 1].")


# ---- Sidebar Settings ----
st.sidebar.header("Pengaturan Animasi")
raw_input_words = st.sidebar.text_input("Masukkan Kata (pisahkan spasi/koma)", "I Love AI")
n_points = st.sidebar.slider("Jumlah Titik (N_POINTS)", 200, 2000, 1000, 100)
dwell_sec = st.sidebar.slider("Waktu Tahan Kata (Dwell Sec)", 0.5, 5.0, 2.0, 0.5)
morph_sec = st.sidebar.slider("Durasi Morphing (Morph Sec)", 0.5, 3.0, 1.5, 0.5)
fps = st.sidebar.slider("FPS (Frame per Second)", 10, 50, 25, 5)


CANVAS_W, CANVAS_H = 18.0, 10.0
SAMPLE_STEP = 0.02
TARGET_RADIUS = 0.02
DOT_SIZE = 16


# ---- Utilities ----
def text_to_points(word, n_points=n_points,
                  canvas_w=CANVAS_W, canvas_h=CANVAS_H,
                  sample_step=SAMPLE_STEP, target_radius=TARGET_RADIUS):
   """Mengubah kata menjadi n_points (x,y) yang terdistribusi pada bentuk huruf."""
   tp = TextPath((0, 0), word, size=1.0, prop=dict(family='DejaVu Sans', weight='bold'))
   bbox = tp.get_extents()
   gw, gh = bbox.width, bbox.height
   if gw == 0 or gh == 0:
       raise ValueError(f"Kata '{word}' menghasilkan bounding box kosong.")
   scale = 0.9 * min(canvas_w/gw, canvas_h/gh)
   T = Affine2D().scale(scale).translate(
       (canvas_w - gw*scale)/2 - bbox.x0*scale,
       (canvas_h - gh*scale)/2 - bbox.y0*scale)
   tp = T.transform_path(tp)
   xs = np.arange(0, canvas_w, sample_step)
   ys = np.arange(0, canvas_h, sample_step)
   grid_x, grid_y = np.meshgrid(xs, ys)
   pts = np.vstack([grid_x.ravel(), grid_y.ravel()]).T
  
   counts = np.zeros(len(pts), dtype=int)
   for poly in tp.to_polygons(closed_only=True):
       counts += Path(poly).contains_points(pts, radius=target_radius)
   pts_in = pts[counts % 2 == 1]
   if len(pts_in) == 0:
       raise ValueError(f"Kata '{word}' tidak menghasilkan titik interior.")
  
   rng = np.random.default_rng()
   idx = rng.choice(len(pts_in), n_points, replace=len(pts_in) < n_points)
   chosen = pts_in[idx]
   jitter = (np.random.rand(len(chosen), 2) - 0.5) * sample_step * 0.5
   return chosen + jitter


def parse_words(inp: str):
   tokens = re.split(r"[,; ]+", inp.strip())
   tokens = [t for t in tokens if t]
   if not tokens:
       raise ValueError("Tidak ada kata yang ditemukan. Contoh: I Love AI")
   return tokens


# ---- Main Execution Button ----
if st.button("Mulai Animasi", type="primary"):
   try:
       seq = parse_words(raw_input_words)
   except ValueError as e:
       st.error(f"[ERROR] {e}")
       st.stop()


   st.info(f"Urutan Kata: {seq}")
  
   # Placeholder penampung plot
   plot_placeholder = st.empty()


   with st.spinner("Memproses posisi titik untuk setiap kata..."):
       try:
           points = {w: text_to_points(w, n_points=n_points) for w in seq}
       except ValueError as e:
           st.error(f"[ERROR] {e}")
           st.stop()


   first = seq[0]
   P = points[first]


   def render_frame(P_curr, title_text):
       fig, ax = plt.subplots(figsize=(8, 5))
       ax.scatter(P_curr[:, 0], P_curr[:, 1], s=DOT_SIZE, color='#1f77b4')
       ax.set_title(title_text)
       ax.set_xlim(0.0, CANVAS_W)
       ax.set_ylim(0.0, CANVAS_H)
       ax.set_aspect("equal")
       ax.grid(True, linestyle=":", linewidth=0.5)
       plot_placeholder.pyplot(fig)
       plt.close(fig)


   # 1. Tampilkan kata pertama + dwell
   render_frame(P, f"Word: {first}")
   time.sleep(dwell_sec)


   # 2. Loop animasi morphing antar kata
   for i in range(1, len(seq)):
       prev_word = seq[i-1]
       nxt = seq[i]
       P_next = points[nxt]
       steps = max(1, int(morph_sec * fps))
      
       for k in range(1, steps + 1):
           a = k / steps
           Pk = (1 - a) * P + a * P_next
           render_frame(Pk, f"Morphing {prev_word} → {nxt}")
           time.sleep(1.0 / fps)
          
       P = P_next
       render_frame(P, f"Word: {nxt}")
       time.sleep(dwell_sec)
      
   st.success("Animasi selesai!")
