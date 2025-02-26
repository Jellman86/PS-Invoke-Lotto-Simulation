import numpy as np
from numba import cuda
from numba.cuda.random import create_xoroshiro128p_states, xoroshiro128p_uniform_float32
import time
import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque

# Define the lottery parameters
draw_params = {
    "euromillions": (5, 2, 50, 12),
    "lotto": (6, 0, 59, 0),
    "thunderball": (5, 1, 39, 14),
    "setforlife": (5, 1, 47, 10)
}

@cuda.jit
def generate_draw_kernel(rng_states, out, balls_drawn, max_draw_number, special_balls_drawn, max_special_draw_number):
    thread_id = cuda.grid(1)
    if thread_id < out.shape[0]:
        # Generate main numbers (ensuring uniqueness)
        used = cuda.local.array(50, dtype=np.int32)  # Max possible number is 50
        for i in range(50):
            used[i] = 0
            
        count = 0
        while count < balls_drawn:
            num = int(xoroshiro128p_uniform_float32(rng_states, thread_id) * max_draw_number) + 1
            if used[num-1] == 0:
                used[num-1] = 1
                out[thread_id, count] = num
                count += 1
        
        # Generate special numbers if needed (ensuring uniqueness)
        if special_balls_drawn > 0:
            used_special = cuda.local.array(12, dtype=np.int32)  # Max possible special number is 12
            for i in range(12):
                used_special[i] = 0
                
            count = 0
            while count < special_balls_drawn:
                num = int(xoroshiro128p_uniform_float32(rng_states, thread_id) * max_special_draw_number) + 1
                if used_special[num-1] == 0:
                    used_special[num-1] = 1
                    out[thread_id, balls_drawn + count] = num
                    count += 1

@cuda.jit
def compare_draws_kernel(draw, results, draws):
    thread_id = cuda.grid(1)
    if thread_id < results.size:
        match = True
        for i in range(draw.size):
            if draw[i] != draws[thread_id, i]:
                match = False
                break
        if match:
            results[thread_id] = 1
        else:
            results[thread_id] = 0  # Initialize to 0

def main(draw_name, simulate_draw, num_simulations=1000000):
    if draw_name not in draw_params:
        print(f"Invalid draw name: {draw_name}")
        return

    balls_drawn, special_balls_drawn, max_draw_number, max_special_draw_number = draw_params[draw_name]
    total_balls = balls_drawn + special_balls_drawn

    if simulate_draw.lower() in ["yes", "y"]:
        # Initialize visualization
        plt.ion()  # Enable interactive mode
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Setup real-time plotting
        max_points = 100
        x_data = deque(maxlen=max_points)
        y_data = deque(maxlen=max_points)
        line, = ax1.plot([], [], 'r-')
        ax1.set_xlim(0, max_points)
        ax1.set_ylim(0, 10)  # Adjust based on expected matches
        ax1.set_title('Real-time Matches')
        ax1.set_xlabel('Time Window')
        ax1.set_ylabel('Matches Found')

        # Initialize histogram
        ax2.set_title('Number Frequency Distribution')
        ax2.set_xlabel('Numbers')
        ax2.set_ylabel('Frequency')

        # Initialize random number generator states
        rng_states = create_xoroshiro128p_states(num_simulations, seed=random.randint(0, 1000000))
        
        # Allocate memory for draws and results
        draws = cuda.device_array((num_simulations, total_balls), dtype=np.int32)
        results = cuda.device_array(num_simulations, dtype=np.int32)
        cuda.device_array_like(results).copy_to_device(results)  # Initialize results to 0
        
        # Generate winning draw on CPU with unique numbers
        draw = np.zeros(total_balls, dtype=np.int32)
        numbers = random.sample(range(1, max_draw_number + 1), balls_drawn)
        for i in range(balls_drawn):
            draw[i] = numbers[i]
        if special_balls_drawn > 0:
            special_numbers = random.sample(range(1, max_special_draw_number + 1), special_balls_drawn)
            for i in range(special_balls_drawn):
                draw[balls_drawn + i] = special_numbers[i]
        
        # Copy winning draw to GPU
        d_draw = cuda.to_device(draw)

        # Set up grid dimensions
        threads_per_block = 256
        blocks_per_grid = (num_simulations + (threads_per_block - 1)) // threads_per_block

        # Generate draws and compare
        start_time = time.time()
        
        batch_size = num_simulations // 100  # Process in batches for visualization
        total_matches = 0
        all_numbers = []

        for batch in range(0, num_simulations, batch_size):
            # Generate and compare batch
            generate_draw_kernel[blocks_per_grid, threads_per_block](
                rng_states, draws[batch:batch+batch_size], 
                balls_drawn, max_draw_number, special_balls_drawn, max_special_draw_number
            )
            compare_draws_kernel[blocks_per_grid, threads_per_block](
                d_draw, results[batch:batch+batch_size], draws[batch:batch+batch_size]
            )
            
            # Update visualization
            batch_results = draws[batch:batch+batch_size].copy_to_host()
            batch_matches = np.sum(results[batch:batch+batch_size].copy_to_host())
            total_matches += batch_matches
            
            # Update line plot
            x_data.append(batch)
            y_data.append(batch_matches)
            line.set_data(range(len(x_data)), y_data)
            
            # Update histogram
            all_numbers.extend(batch_results.flatten())
            ax2.clear()
            ax2.hist(all_numbers, bins=max_draw_number, range=(1, max_draw_number))
            ax2.set_title('Number Frequency Distribution')
            
            # Refresh the plot
            plt.pause(0.01)

        end_time = time.time()

        print(f"Winning numbers: {draw}")
        print(f"MATCHES: {total_matches} out of {num_simulations} simulations")
        print(f"Time taken: {end_time - start_time} seconds")

        if total_matches > 0:
            with open("winner.txt", "w") as f:
                f.write(f"Winning value of {draw} for a DRAW vs Lucky Dip. "
                       f"Matches found: {total_matches}. "
                       f"Time taken: {end_time - start_time} seconds.")
        
        # Keep plot window open
        plt.ioff()
        plt.show()

    else:
        # Generate single lucky dip
        numbers = np.random.choice(np.arange(1, max_draw_number + 1), balls_drawn, replace=False)
        if special_balls_drawn > 0:
            special_numbers = np.random.choice(np.arange(1, max_special_draw_number + 1), special_balls_drawn, replace=False)
            lucky_dip = np.concatenate((numbers, special_numbers))
        else:
            lucky_dip = numbers
        print(f"Lucky Dip: {lucky_dip}")

if __name__ == "__main__":
    draw_name = "euromillions"  # Change as needed
    simulate_draw = "yes"  # Change as needed
    main(draw_name, simulate_draw)