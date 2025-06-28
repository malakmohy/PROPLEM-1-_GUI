import random
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
#------------------------------------------------------------------------------------------------------------------------------------
# Parameters
arrival_probabilities = [0.17, 0.23, 0.25, 0.35]  # For 0, 1, 2, 3 minutes
a_and_b_service_probs = [0.2, 0.3, 0.5]  # For 1, 2, 3 minutes
c_service_probs = [0.2, 0.5, 0.3]  # For 3, 5, 7 minutes
categories = ["A", "B", "C"]
category_probs = [0.2, 0.35, 0.45]

# Queues for pumps
pump_95 = []
pump_90 = []
pump_gas = []

# Metrics
cars_served = 0
total_wait_time = 0
waiting_times = {"95 Octane": [], "90 Octane": [], "Gas": []}
queue_lengths = {"95 Octane": [], "90 Octane": [], "Gas": []}
service_times = {"A": [], "B": [], "C": []}
idle_times = {"95 Octane": 0, "90 Octane": 0, "Gas": 0}
pump_last_end_time = {"95 Octane": 0, "90 Octane": 0, "Gas": 0}
waiting_cars = {"95 Octane": 0, "90 Octane": 0, "Gas": 0}
#-----------------------------------------------------------------------------------------------------------------------------
# Table to store simulation details
simulation_table = []

def get_cumulative_intervals(probabilities): #[0.17, 0.23, 0.25, 0.35]
                                             #[17,40,65,100]
    #Convert probabilities to cumulative intervals
    cumulative = []
    total = 0
    for p in probabilities:
        total += p
        cumulative.append(total * 100)  # Convert to percentage scale (0-100)
    return cumulative

def map_random_to_value(random_num, cumulative_intervals, values): 
    #Map a random number (0-100) to a value based on cumulative intervals.
    for i, upper_bound in enumerate(cumulative_intervals):
        if random_num < upper_bound:
            return values[i]
    return values[-1]  # Default to last value if no match

def simulate(n_cars):
    global cars_served, total_wait_time 
    time = 0
    car_number = 0

    # Compute cumulative intervals
    arrival_intervals = get_cumulative_intervals(arrival_probabilities)
    a_and_b_service_intervals = get_cumulative_intervals(a_and_b_service_probs)
    c_service_intervals = get_cumulative_intervals(c_service_probs)
    category_intervals = get_cumulative_intervals(category_probs)

    while car_number < n_cars:
        # Generate car arrival
        random_arrival = random.randint(0, 99)
        inter_arrival_time = map_random_to_value(random_arrival, arrival_intervals, [0, 1, 2, 3])
        time += inter_arrival_time
        random_category = random.randint(0, 99)
        car_category = map_random_to_value(random_category, category_intervals, categories)

        if car_category == "A":
            random_service = random.randint(0, 99)
            service_time = map_random_to_value(random_service, a_and_b_service_intervals, [1, 2, 3])
            pump = "95 Octane"
            queue = pump_95

        elif car_category == "B":
            if len(pump_90) > 3 and random.random() < 0.6:
                random_service = random.randint(0, 99)
                service_time = map_random_to_value(random_service, a_and_b_service_intervals, [1, 2, 3])
                pump = "95 Octane"
                queue = pump_95
            else:
                random_service = random.randint(0, 99)
                service_time = map_random_to_value(random_service, a_and_b_service_intervals, [1, 2, 3])
                pump = "90 Octane"
                queue = pump_90

        elif car_category == "C":
            if len(pump_gas) > 4 and random.random() < 0.4:
                random_service = random.randint(0, 99)
                service_time = map_random_to_value(random_service, c_service_intervals, [3, 5, 7])
                pump = "90 Octane"
                queue = pump_90
            else:
                random_service = random.randint(0, 99)
                service_time = map_random_to_value(random_service, c_service_intervals, [3, 5, 7])
                pump = "Gas"
                queue = pump_gas

        # Record service start and end times
        service_start = max(time, queue[-1][2] if queue else 0)
        service_end = service_start + service_time

        # Update idle time
        idle_times[pump] += max(0, service_start - pump_last_end_time[pump])
        pump_last_end_time[pump] = service_end

        # Append to queue
        queue.append((time, service_time, service_end))

        # waiting times and queue lengths
        waiting_times[pump].append(service_start - time)
        waiting_cars[pump] += 1 if service_start > time else 0
        queue_lengths[pump].append(len(queue))

        # service times
        service_times[car_category].append(service_time)

        # simulation details
        simulation_table.append({
            "Car Number": car_number + 1,
            "Random Category Number": random_category,
            "Category": car_category,
            "Random Arrival Time": random_arrival,
            "Time Between Arrivals": inter_arrival_time,
            "Time in Clock": time,
            "Random Service Time": random_service,
            "Service Start (95 Octane)": service_start if pump == "95 Octane" else None,
            "Service Time (95 Octane)": service_time if pump == "95 Octane" else None,
            "Service End (95 Octane)": service_end if pump == "95 Octane" else None,
            "Service Start (90 Octane)": service_start if pump == "90 Octane" else None,
            "Service Time (90 Octane)": service_time if pump == "90 Octane" else None,
            "Service End (90 Octane)": service_end if pump == "90 Octane" else None,
            "Service Start (Gas)": service_start if pump == "Gas" else None,
            "Service Time (Gas)": service_time if pump == "Gas" else None,
            "Service End (Gas)": service_end if pump == "Gas" else None
        })

        car_number += 1
        
    # Results
    df = pd.DataFrame(simulation_table)
    print(df.to_string(index=False))

# Function to run the simulation
def run_simulation():
    try:
        n_cars = int(num_cars_entry.get())  # Get the number of cars from the input box
        if n_cars <= 0:
            raise ValueError(" cars should be positive.")
    except ValueError as e:
        showinfo("Input Error", f"Invalid input for number of cars: {e}")
        return

    simulation_table.clear()  # Clear previous simulation data
    simulate(n_cars)  # Run the simulation with the specified number of cars

    # Update the table with simulation results
    for row in tree.get_children():
        tree.delete(row)
    for entry in simulation_table:
        tree.insert("", tk.END, values=[entry[col] for col in columns])

    # Update statistics
    stats_text.set(get_statistics())

    # Update histograms
    update_histograms()

def get_statistics():
    # Compute and format statistics
    avg_service_times = {cat: (sum(times) / len(times) if times else 0) for cat, times in service_times.items()}
    avg_wait_times = {pump: (sum(times) / len(times) if times else 0) for pump, times in waiting_times.items()}
    max_queue_lengths = {pump: max(lengths) if lengths else 0 for pump, lengths in queue_lengths.items()}
    prob_car_waits = {pump: (waiting_cars[pump] / len(simulation_table)) for pump in waiting_cars}
    total_time = max(pump_last_end_time.values())
    idle_portions = {pump: (idle_times[pump] / total_time) for pump in idle_times}

    # Analyze the effect of adding one extra pump
    reduction_effect = {}
    for pump in waiting_times:
        if waiting_times[pump]:
            original_avg_wait = sum(waiting_times[pump]) / len(waiting_times[pump])
            hypothetical_wait = [time * 0.5 for time in waiting_times[pump]]  # Assume 50% reduction
            reduced_avg_wait = sum(hypothetical_wait) / len(hypothetical_wait)
            reduction_effect[pump] = original_avg_wait - reduced_avg_wait

    best_pump = max(reduction_effect, key=reduction_effect.get)

    stats = "--- Statistics ---\n"
    stats += "1. Average Service Times:\n"
    for cat, avg_time in avg_service_times.items():
        stats += f"   Category {cat}: {avg_time:.2f} minutes\n"

    stats += "\n2. Average Waiting Times:\n"
    for pump, avg_wait in avg_wait_times.items():
        stats += f"   {pump}: {avg_wait:.2f} minutes\n"
    overall_avg_wait = sum(sum(times) for times in waiting_times.values()) / sum(len(times) for times in waiting_times.values())
    stats += f"   Overall: {overall_avg_wait:.2f} minutes\n"

    stats += "\n3. Maximum Queue Lengths:\n"
    for pump, max_length in max_queue_lengths.items():
        stats += f"   {pump}: {max_length} cars\n"

    stats += "\n4. Probability that a car waits:\n"
    for pump, prob in prob_car_waits.items():
        stats += f"   {pump}: {prob:.2%}\n"

    stats += "\n5. Portion of Idle Time:\n"
    for pump, portion in idle_portions.items():
        stats += f"   {pump}: {portion:.2%}\n"

    stats += "\n6. Impact of Adding One Extra Pump:\n"
    for pump, reduction in reduction_effect.items():
        stats += f"   {pump}: Reduction in avg wait time = {reduction:.2f} minutes\n"
    stats += f"   Best pump to add: {best_pump}\n"

    return stats

def update_histograms():
    # Clear existing figures
    for widget in histogram_frame.winfo_children():
        widget.destroy()

    # Create histograms for each pump
    for pump, times in waiting_times.items():
        if times:
            fig, ax = plt.subplots(figsize=(4, 3))
            ax.hist(times, bins=10, color='blue', alpha=0.7, edgecolor='black')
            ax.set_title(f"{pump} Wait Times")
            ax.set_xlabel("Wait Time (minutes)")
            ax.set_ylabel("Frequency")

            canvas = FigureCanvasTkAgg(fig, master=histogram_frame)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(side="left", padx=10, pady=10)

# Create the GUI window
root = tk.Tk()
root.title("Simulation Results")

# Input frame for the number of cars
input_frame = ttk.Frame(root)
input_frame.pack(pady=10, padx=10, fill="x")

num_cars_label = ttk.Label(input_frame, text="Number of Cars:")
num_cars_label.pack(side="left", padx=5)

num_cars_entry = ttk.Entry(input_frame)
num_cars_entry.pack(side="left", padx=5)

run_button = ttk.Button(input_frame, text="Run Simulation", command=run_simulation)
run_button.pack(side="left", padx=10)

# Create a notebook for section tabs
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=10, pady=10)

# Create a frame for the table
table_frame = ttk.Frame(notebook)
notebook.add(table_frame, text="Simulation Table")

# Define columns for the treeview
columns = ["Car Number", "Random Category Number", "Category", "Random Arrival Time", "Time Between Arrivals", "Time in Clock", "Random Service Time", "Service Start (95 Octane)", "Service Time (95 Octane)", "Service End (95 Octane)", "Service Start (90 Octane)", "Service Time (90 Octane)", "Service End (90 Octane)", "Service Start (Gas)", "Service Time (Gas)", "Service End (Gas)"]

# Create the treeview widget
tree = ttk.Treeview(table_frame, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120, anchor="center")
tree.pack(side="left", fill="both", expand=True)

# Add a scrollbar
scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
scrollbar.pack(side="right", fill="y")
tree.configure(yscroll=scrollbar.set)

# Create a frame for statistics
stats_frame = ttk.Frame(notebook)
notebook.add(stats_frame, text="Statistics")

# Label for statistics
stats_text = tk.StringVar()
stats_label = ttk.Label(stats_frame, textvariable=stats_text, justify="left")
stats_label.pack(anchor="w", padx=10, pady=5)

# Create a frame for histograms
histogram_frame = ttk.Frame(notebook)
notebook.add(histogram_frame, text="Histograms")

# Start the GUI loop
root.mainloop()




