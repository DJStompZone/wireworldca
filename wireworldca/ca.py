import os
import argparse
import numpy as np
import random
import imageio
import cv2

from tqdm import tqdm

# Wireworld States
EMPTY = 0
CONDUCTOR = 1
HEAD = 2
TAIL = 3

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)

def generate_random_half_adder_field(grid_size, num_adders=10):
    field = np.zeros(grid_size, dtype=int)
    adder_positions = []

    for _ in range(num_adders):
        x = random.randint(0, grid_size[0] - 15)
        y = random.randint(0, grid_size[1] - 20)

        # Ensure no overlap by checking previous positions
        if any(abs(px - x) < 15 and abs(py - y) < 20 for px, py in adder_positions):
            continue

        adder_positions.append((x, y))

        # Local Half-Adder conductors
        for dx, dy in [
            (2, 5), (2, 6), (2, 7), (4, 5), (4, 6), (4, 7),
            (3, 8), (3, 9), (3, 10), (3, 11), (4, 8), (4, 9), (4, 10), (4, 11),
            (5, 8), (5, 9), (5, 10), (5, 11), (6, 12), (6, 13), (6, 14),
            (7, 15), (7, 16), (7, 17)
        ]:
            field_x, field_y = x + dx, y + dy
            if 0 <= field_x < grid_size[0] and 0 <= field_y < grid_size[1]:
                field[field_x, field_y] = CONDUCTOR

        if random.choice([True, False]):
            field[x + 2, y + 5] = HEAD  # A = 1
        if random.choice([True, False]):
            field[x + 4, y + 5] = HEAD  # B = 1

    return field

def count_heads(grid, x, y):
    neighbors = [(-1, -1), (-1, 0), (-1, 1),
                 (0, -1),         (0, 1),
                 (1, -1), (1, 0), (1, 1)]
    return sum(grid[x+dx, y+dy] == HEAD for dx, dy in neighbors if 0 <= x+dx < grid.shape[0] and 0 <= y+dy < grid.shape[1])

def update_wireworld(grid):
    new_grid = np.copy(grid)
    for x in range(grid.shape[0]):
        for y in range(grid.shape[1]):
            if grid[x, y] == HEAD:
                new_grid[x, y] = TAIL
            elif grid[x, y] == TAIL:
                new_grid[x, y] = CONDUCTOR
            elif grid[x, y] == CONDUCTOR:
                if 1 <= count_heads(grid, x, y) <= 2:
                    new_grid[x, y] = HEAD
    return new_grid

def grid_to_image(grid, scale=20):
    color_map = {EMPTY: (255, 255, 255), CONDUCTOR: (255, 255, 0), HEAD: (0, 0, 255), TAIL: (255, 0, 0)}
    h, w = grid.shape
    img = np.zeros((h * scale, w * scale, 3), dtype=np.uint8)
    for x in range(h):
        for y in range(w):
            img[x*scale:(x+1)*scale, y*scale:(y+1)*scale] = color_map[grid[x, y]]
    return img

def run_experiment(test_num, grid_size, num_adders, max_steps, output_dir, experiment_num=0):
    test_dir = os.path.join(output_dir, f"test{test_num}")
    os.makedirs(test_dir, exist_ok=True)

    field = generate_random_half_adder_field(grid_size, num_adders=num_adders)
    previous_frame = None

    for frame_num in tqdm(range(max_steps), desc=f"Running experiment #{experiment_num or '??'}", unit="step", dynamic_ncols=True):
        frame_path = os.path.join(test_dir, f"step{frame_num}.png")
        frame_image = grid_to_image(field)
        imageio.imwrite(frame_path, frame_image)

        new_field = update_wireworld(field)

        if previous_frame is not None and np.array_equal(previous_frame, new_field):
            break

        previous_frame = np.copy(new_field)
        field[:] = new_field