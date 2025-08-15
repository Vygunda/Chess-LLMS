import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress

# Load data from the file
data = []
with open('V_black_winrate_array_progression.txt', 'r') as file:
    for line in file:
        rates = [float(x.strip('%')) for x in line.strip().split()]
        data.append(rates)

# Convert to DataFrame and transpose for moves along columns
data_df = pd.DataFrame(data).transpose()

# Calculate average win rate per move (ignoring NaN values)
average_win_rate = data_df.mean(axis=1)

# Prepare x-axis as the move numbers
moves = np.arange(1, len(average_win_rate) + 1)

# Perform linear regression to get the trendline
slope, intercept, r_value, p_value, std_err = linregress(moves, average_win_rate)
regression_line = slope * moves + intercept

# Plotting
plt.figure(figsize=(12, 6))

# Plot the average win rates
plt.plot(moves, average_win_rate, marker='o', color='blue', label='Average Black Win Rate')

# Plot the regression line
plt.plot(moves, regression_line, color='red', linestyle='--', label=f'Trendline (slope={slope:.2f})')

# Add labels and title
plt.xlabel('Move Number')
plt.ylabel('Average Black Win Rate (%)')
plt.title('Trend of Black Win Rate Progression Across Moves')
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.show()
