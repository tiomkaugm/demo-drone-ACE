import numpy as np
import pandas as pd


def compute_interpolated_frames(start_pos: np.ndarray, target_pos: np.ndarray, n_steps: int = 12) -> list:
    """
    Menghasilkan langkah posisi frame transisi menggunakan interpolasi Cosine (S-Curve)
    dengan pemisahan koridor kedalaman (sumbu Y) untuk menghindari tabrakan.
    """
    frames = []
    n_drones = len(start_pos)
    y_corridor = np.sin(np.linspace(0, np.pi, n_drones)) * 15.0

    for step in range(n_steps + 1):
        progress = step / n_steps
        s = 0.5 * (1 - np.cos(np.pi * progress))

        curr_x = (1 - s) * start_pos[:, 0] + s * target_pos[:, 0]
        curr_z = (1 - s) * start_pos[:, 2] + s * target_pos[:, 2]
        curr_y = (1 - s) * start_pos[:, 1] + s * target_pos[:, 1] + (y_corridor * np.sin(np.pi * progress))

        frames.append(np.column_stack((curr_x, curr_y, curr_z)))
    return frames


def generate_swarm_telemetry(n_drones: int, start_pos: np.ndarray, target_pos: np.ndarray) -> pd.DataFrame:
    """
    Menghitung statistik telemetri operasional per drone.
    """
    distances = np.linalg.norm(target_pos - start_pos, axis=1)
    energy_used = 3.5 + (distances * 0.08)

    return pd.DataFrame({
        "Drone_ID": [f"DRN-{i+1:04d}" for i in range(n_drones)],
        "Distance_m": np.round(distances, 2),
        "Est_Battery_Loss_%": np.round(energy_used, 2),
        "Target_X": np.round(target_pos[:, 0], 2),
        "Target_Y": np.round(target_pos[:, 1], 2),
        "Target_Z": np.round(target_pos[:, 2], 2),
        "Status": ["Ready / Locked"] * n_drones
    })
