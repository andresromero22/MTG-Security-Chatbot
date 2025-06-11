import matplotlib.pyplot as plt

# Data
tools_needed = [
    "Tire handler", "Soft face hammer", "Heavy gauge wire", "Lock ring bars",
    "Valve accessories", "Wrenches", "Disc grinder", "49” O-ring", "Pliers",
    "Screwdriver", "Knife/Scissors", "Hydraulic Jack and Support Stand",
    "Hydraulic power pack", "Hydraulic ram / bead breaker", "Pressure Washer",
    "Soap spray", "Wheel gauges"
]
number_of_tools = [1] * len(tools_needed)  # Each tool counts as one

# Plot
plt.figure(figsize=(10, 6))
plt.barh(tools_needed, number_of_tools, color='skyblue')
plt.xlabel('Number of Tools')
plt.title('Tools Needed for Tire Change')
plt.xlim(0, 1.5)
plt.tight_layout()
plt.show()
