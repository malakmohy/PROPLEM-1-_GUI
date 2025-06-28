import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Room Occupied Ranges
room_occupancy_ranges = {
    (0, 10): 1,
    (11, 25): 2,
    (26, 60): 3,
    (61, 80): 4,
    (81, 100): 5
}

# Lead Time Ranges (from the provided table)
lead_time_ranges = {
    (1, 40): 1,
    (41, 75): 2,
    (76, 100): 3
}

# Map random number to Lead Time
def map_lead_time(random_number):
    for (low, high), lead_time in lead_time_ranges.items():
        if low <= random_number <= high:
            return lead_time
    return 1  # Default fallback (should never be reached)

def map_rooms_occupied(random_number):
    for (low, high), rooms in room_occupancy_ranges.items():
        if low <= random_number <= high:
            return rooms
    return 1  # Default fallback (should never be reached)

# Simulation function
def simulate_hospital_inventory(N, M, max_days=20, days_per_cycle=6):
    columns = [
        "Cycle", "Day", "First Floor Inventory", "Random Room", "Rooms Occupied",
        "Daily Consumption", "End Inventory", "Shortage", "Basement Inventory",
        "Order Quantity", "Random Lead Time", "Lead Time (Days Until Order Arrives)"
    ]
    data = []

    # Start inventories
    first_floor_inventory = 4  # Start with 4 on the first floor
    basement_inventory = M
    lead_time_remaining = 0
    order_quantity = 0
    total_days = 0
    cycle = 1

    while total_days < max_days:
        for day in range(1, days_per_cycle + 1):
            total_days += 1
            if total_days > max_days:
                break

            random_room = np.random.randint(1, 101)
            rooms_occupied = map_rooms_occupied(random_room)
            daily_consumption = rooms_occupied

            # Calculate End Inventory and Shortage
            if first_floor_inventory >= daily_consumption:
                end_inventory = first_floor_inventory - daily_consumption
                shortage = 0
            else:
                shortage = daily_consumption - first_floor_inventory
                end_inventory = -shortage

            # Update First Floor Inventory for the next day
            if end_inventory >= 0:
                first_floor_inventory = end_inventory
            else:
                shortage = abs(end_inventory)
                first_floor_inventory = 10 - shortage if shortage <= 10 else 0
                available_in_basement = basement_inventory
                to_deduct = min(10, available_in_basement)
                basement_inventory -= to_deduct  # Reduce basement inventory dynamically

            # Handle lead time for basement replenishment
            if lead_time_remaining > 0:
                lead_time_remaining -= 1
                if lead_time_remaining == 0:
                    basement_inventory = M

            # Place order every N days
            if total_days % N == 0 and lead_time_remaining == 0:
                order_quantity = M - basement_inventory
                random_lead_time = int(np.random.randint(1, 101))  # Generate integer random number
                lead_time_remaining = map_lead_time(random_lead_time)  # Map random number to lead time
            else:
                order_quantity = 0
                random_lead_time = 0  # Set random lead time to 0 if no new order

            # Append the day results
            data.append([ 
                cycle, total_days, first_floor_inventory, random_room, rooms_occupied,
                daily_consumption, end_inventory, shortage, basement_inventory,
                order_quantity, random_lead_time, lead_time_remaining if lead_time_remaining > 0 else 0
            ])

        # Increment cycle after each set of days
        cycle += 1

    return pd.DataFrame(data, columns=columns)

# Generate the simulation table using the simulate_hospital_inventory function
N = 6  # Example review period
M = 30  # Example basement capacity
simulation_table = simulate_hospital_inventory(N=N, M=M, max_days=20, days_per_cycle=6)

# Assign manual custom values
custom_first_floor_values = [4, 1, 7, 3, 0, 9, 6, 1, 8, 4, 1, 8, 6, 3, 9, 6, 3, 5, 9, 0]

# Update manually for day 1
simulation_table.loc[0, "First Floor Inventory"] = custom_first_floor_values[0]

# Update for subsequent days
for i in range(1, len(simulation_table)):
    previous_end = simulation_table.loc[i - 1, "End Inventory"]
    daily_consumption = simulation_table.loc[i, "Daily Consumption"]
    if previous_end >= 0:
        simulation_table.loc[i, "First Floor Inventory"] = previous_end
    else:
        shortage = abs(previous_end)
        simulation_table.loc[i, "First Floor Inventory"] = 10 - shortage if shortage <= 10 else 0
        available_in_basement = simulation_table.loc[i - 1, "Basement Inventory"]
        to_deduct = min(10, available_in_basement)

# Average Inventory Levels
avg_first_floor_inventory = simulation_table["First Floor Inventory"].mean()
avg_basement_inventory = simulation_table["Basement Inventory"].mean()

# Number of Days with Shortages
days_with_shortage = simulation_table[simulation_table["Shortage"] > 0].shape[0]

# Theoretical and Experimental Demand
theoretical_demand = sum([prob * rooms for prob, rooms in zip([0.1, 0.15, 0.35, 0.2, 0.2], [1, 2, 3, 4, 5])])
experimental_demand = simulation_table["Daily Consumption"].mean()

# Theoretical and Experimental Lead Time
theoretical_lead_time = sum([prob * lead for prob, lead in zip([0.4, 0.35, 0.25], [1, 2, 3])])
experimental_lead_time = simulation_table[simulation_table["Random Lead Time"] > 0]["Lead Time (Days Until Order Arrives)"].mean()

# Tkinter GUI for displaying results
root = tk.Tk()
root.title("Hospital Inventory Simulation")

# Tab Control
tab_control = ttk.Notebook(root)

# Tab 1 - Simulation Table
tab1 = ttk.Frame(tab_control)
tab_control.add(tab1, text="Simulation Table")

# Display Simulation Table
tree = ttk.Treeview(tab1, columns=list(simulation_table.columns), show="headings", height=10)
for col in simulation_table.columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)
for index, row in simulation_table.iterrows():
    tree.insert("", "end", values=list(row))
tree.pack(padx=10, pady=10)

# Tab 2 - Calculated Parameters
tab2 = ttk.Frame(tab_control)
tab_control.add(tab2, text="Calculated Parameters")

# Display calculated parameters
results_label = tk.Label(tab2, text=f"""
Average First Floor Inventory: {avg_first_floor_inventory:.2f}
Average Basement Inventory: {avg_basement_inventory:.2f}
Days with Shortage: {days_with_shortage}
Theoretical Demand: {theoretical_demand:.2f}
Experimental Demand: {experimental_demand:.2f}
Theoretical Lead Time: {theoretical_lead_time:.2f}
Experimental Lead Time: {experimental_lead_time:.2f}
""", justify="left")
results_label.pack(padx=10, pady=10)

# Tab 3 - Graph
tab3 = ttk.Frame(tab_control)
tab_control.add(tab3, text="Inventory Levels Graph")

# Plotting the graph
fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(simulation_table["Day"], simulation_table["First Floor Inventory"], label="First Floor Inventory")
ax.plot(simulation_table["Day"], simulation_table["Basement Inventory"], label="Basement Inventory")
ax.axhline(0, color='red', linestyle='--', label="Shortage Line")
ax.set_xlabel("Day")
ax.set_ylabel("Inventory Level")
ax.set_title("Inventory Levels Over Time")
ax.legend()

# Display the graph in Tkinter
canvas = FigureCanvasTkAgg(fig, tab3)
canvas.get_tk_widget().pack(padx=10, pady=10)
canvas.draw()

# Start the GUI event loop
tab_control.pack(expand=1, fill="both")
root.mainloop()