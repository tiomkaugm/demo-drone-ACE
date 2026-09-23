import numpy as np
from scipy.optimize import linear_sum_assignment


def solve_optimal_assignment(current_positions: np.ndarray, target_positions: np.ndarray) -> np.ndarray:
    """
    Menyelesaikan penugasan 1-ke-1 meminimalkan total kuadrat jarak tempuh drone.
    """
    cost_matrix = np.sum((current_positions[:, np.newaxis, :] - target_positions[np.newaxis, :, :]) ** 2, axis=2)
    _, col_ind = linear_sum_assignment(cost_matrix)
    return target_positions[col_ind]
