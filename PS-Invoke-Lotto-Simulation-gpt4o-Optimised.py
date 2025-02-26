import numpy as np
from numba import cuda, jit
import time
import random

# Define the lottery parameters
draw_params = {
    "euromillions": (5, 2, 50, 12),
    "lotto": (6, 0, 59, 0),
    "thunderball": (5, 1, 39, 14),
    "setforlife": (5, 1, 47, 10)
}

# Function to generate random draw
@jit(nopython=True)
def generate_draw(balls_drawn, max_draw_number, special_balls_drawn, max_special_draw_number):
    numbers = np.random.choice(np.arange(1, max_draw_number + 1), balls_drawn, replace=False)
    if special_balls_drawn > 0:
        special_numbers = np.random.choice(np.arange(1, max_special_draw_number + 1), special_balls_drawn, replace=False)
        return np.concatenate((numbers, special_numbers))
    return numbers

# CUDA kernel to run the lottery simulation
@cuda.jit
def lottery_simulation(draw, results, num_simulations, balls_drawn, max_draw_number, special_balls_drawn, max_special_draw_number):
    idx = cuda.grid(1)
    if idx < num_simulations:
        ld = generate_draw(balls_drawn, max_draw_number, special_balls_drawn, max_special_draw_number)
        if np.array_equal(draw, ld):
            results[idx] = 1
        else:
            results[idx] = 0

def main(draw_name, simulate_draw, num_simulations=1000000):
    if draw_name not in draw_params:
        print(f"Invalid draw name: {draw_name}")
        return

    balls_drawn, special_balls_drawn, max_draw_number, max_special_draw_number = draw_params[draw_name]

    if simulate_draw.lower() in ["yes", "y"]:
        draw = generate_draw(balls_drawn, max_draw_number, special_balls_drawn, max_special_draw_number)
        results = np.zeros(num_simulations, dtype=np.int32)

        threads_per_block = 256
        blocks_per_grid = (num_simulations + (threads_per_block - 1)) // threads_per_block

        start_time = time.time()
        lottery_simulation[blocks_per_grid, threads_per_block](draw, results, num_simulations, balls_drawn, max_draw_number, special_balls_drawn, max_special_draw_number)
        cuda.synchronize()
        end_time = time.time()

        matches = np.sum(results)
        print(f"MATCHES: {matches} out of {num_simulations} simulations")
        print(f"Time taken: {end_time - start_time} seconds")

        if matches > 0:
            with open("winner.txt", "w") as f:
                f.write(f"Winning value of {draw} for a DRAW vs Lucky Dip. Matches found: {matches}. Time taken: {end_time - start_time} seconds.")
    else:
        lucky_dip = generate_draw(balls_drawn, max_draw_number, special_balls_drawn, max_special_draw_number)
        print(f"Lucky Dip: {lucky_dip}")

if __name__ == "__main__":
    draw_name = "euromillions"  # Change as needed
    simulate_draw = "yes"  # Change as needed
    main(draw_name, simulate_draw)