import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time


from core.text_sampler import generate_text_targets
from core.assignment import solve_optimal_assignment
from core.trajectory import compute_interpolated_frames, generate_swarm_telemetry


st.set_page_config(page_title="Swarm Formation Studio", layout="wide")


# State Aplikasi
if "n_drones" not in st.session_state:
    st.session_state.n_drones = 1000
if "positions" not in st.session_state:
    side = int(np.ceil(np.sqrt(st.session_state.n_drones)))
    gx, gy = np.meshgrid(np.linspace(-40, 40, side), np.linspace(-40, 40, side))
    st.session_state.positions = np.column_stack((gx.ravel()[:st.session_state.n_drones], gy.ravel()[:st.session_state.n_drones], np.zeros(st.session_state.n_drones)))
if "telemetry_df" not in st.session_state:
    st.session_state.telemetry_df = None
if "current_pattern" not in st.session_state:
    st.session_state.current_pattern = "Launchpad (Ground)"


# Sidebar Menu
with st.sidebar:
    st.title("Swarm Control Unit")
    st.markdown("---")

    n_input = st.selectbox("Jumlah Drone (N)", options=[500, 1000, 1500, 2000], index=1)
    if n_input != st.session_state.n_drones:
        st.session_state.n_drones = n_input
        side = int(np.ceil(np.sqrt(n_input)))
        gx, gy = np.meshgrid(np.linspace(-50, 50, side), np.linspace(-50, 50, side))
        st.session_state.positions = np.column_stack((gx.ravel()[:n_input], gy.ravel()[:n_input], np.zeros(n_input)))
        st.session_state.telemetry_df = None
        st.session_state.current_pattern = "Launchpad (Ground)"
        st.rerun()


    text_input = st.text_input("Teks Formasi", value="UGM Yogyakarta")

    col1, col2 = st.columns(2)
    with col1:
        form_btn = st.button("Bentuk Teks", use_container_width=True)
    with col2:
        reset_btn = st.button("Reset Ground", use_container_width=True)

    st.markdown("---")
    show_stats = st.checkbox("Tampilkan Detail Statistik", value=True)


# Render Plot Visualisasi
def build_scatter_plot(points: np.ndarray, title: str):
    fig = go.Figure(data=[go.Scatter3d(
        x=points[:, 0], y=points[:, 1], z=points[:, 2],
        mode='markers',
        marker=dict(size=3, color=points[:, 2], colorscale='Viridis', opacity=0.9),
        text=[f"ID: DRN-{i+1:04d}" for i in range(len(points))],
        hoverinfo="text+x+y+z"
    )])
    fig.update_layout(
        title=f"<b>Visualisasi Formasi Swarm</b> — {title}",
        scene=dict(
            xaxis=dict(range=[-110, 110], title="X (m)"),
            yaxis=dict(range=[-60, 60], title="Y (m)"),
            zaxis=dict(range=[-5, 105], title="Z (m)"),
            aspectratio=dict(x=2.2, y=1.2, z=1.0),
            bgcolor="#0E1117"
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        template="plotly_dark",
        height=550
    )
    return fig


main_canvas = st.empty()


if reset_btn:
    side = int(np.ceil(np.sqrt(st.session_state.n_drones)))
    gx, gy = np.meshgrid(np.linspace(-40, 40, side), np.linspace(-40, 40, side))
    st.session_state.positions = np.column_stack((gx.ravel()[:st.session_state.n_drones], gy.ravel()[:st.session_state.n_drones], np.zeros(st.session_state.n_drones)))
    st.session_state.telemetry_df = None
    st.session_state.current_pattern = "Launchpad (Ground)"
    st.rerun()


if form_btn:
    raw_targets = generate_text_targets(text_input, st.session_state.n_drones)
    assigned_targets = solve_optimal_assignment(st.session_state.positions, raw_targets)
    frames = compute_interpolated_frames(st.session_state.positions, assigned_targets, n_steps=12)
    st.session_state.telemetry_df = generate_swarm_telemetry(st.session_state.n_drones, st.session_state.positions, assigned_targets)

    prog = st.progress(0)
    for idx, frame in enumerate(frames):
        prog.progress(int(((idx + 1) / len(frames)) * 100))
        fig = build_scatter_plot(frame, title=f"Manuver: '{text_input}'")
        main_canvas.plotly_chart(fig, use_container_width=True)
        time.sleep(0.04)

    st.session_state.positions = assigned_targets
    st.session_state.current_pattern = f"Text: {text_input}"
    prog.empty()
else:
    fig = build_scatter_plot(st.session_state.positions, title=st.session_state.current_pattern)
    main_canvas.plotly_chart(fig, use_container_width=True)


# Panel Statistik Bawah
if show_stats:
    st.markdown("### Ringkasan Statistik Operasional")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Agen", f"{st.session_state.n_drones} Unit")
    c2.metric("Pola Aktif", st.session_state.current_pattern)
    avg_d = st.session_state.telemetry_df["Distance_m"].mean() if st.session_state.telemetry_df is not None else 0.0
    c3.metric("Rata-rata Jarak Tempuh", f"{avg_d:.2f} m")


    if st.session_state.telemetry_df is not None:
        st.dataframe(st.session_state.telemetry_df, use_container_width=True, hide_index=True, height=220)
