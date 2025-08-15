import pandas as pd
import matplotlib.pyplot as plt

# Load the data for black win rates
data = []
with open('V_black_winrate_array_progression.txt', 'r') as file:
    for line in file:
        rates = [float(x.strip('%')) for x in line.strip().split()]
        data.append(rates)

# Load the proportions for Black moves
proportions = []
with open('/Users/vyshnavigunda/Desktop/CHESS/V_proportion_games_count_progression_black.txt', 'r') as file:
    for line in file:
        props = [float(x) for x in line.strip().split()]
        proportions.append(props)

# Convert data to a DataFrame with NaN for missing values
data_df = pd.DataFrame(data)
proportions_df = pd.DataFrame(proportions)

# Calculate the average black win rate across moves (ignoring NaN values)
average_win_rate = data_df.mean(axis=0)

# Calculate the number of games still valid (non-NaN values) after each move
valid_games_count = data_df.notna().sum(axis=0)

# Calculate the average proportions across games
average_proportions = proportions_df.mean(axis=0)

# Generate x-axis values corresponding to Black move numbers (2, 4, 6, ...)
black_move_numbers = [(i + 1) for i in range(len(average_win_rate))]

# Plotting
fig, ax1 = plt.subplots(figsize=(12, 6))

# Plot average black win rate
ax1.plot(black_move_numbers, average_win_rate, color='blue', marker='o', label='Average Black Win Rate')
ax1.set_xlabel('Black Move Number')
ax1.set_ylabel('Average Black Win Rate (%)', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')

# Adding second y-axis for the count of valid games
ax2 = ax1.twinx()
ax2.plot(black_move_numbers, valid_games_count, color='green', marker='x', linestyle='--', label='Games Remaining')
ax2.set_ylabel('Number of Games Remaining', color='green')
ax2.tick_params(axis='y', labelcolor='green')

# Adding third y-axis for the proportions of Black moves
ax3 = ax1.twinx()
ax3.spines['right'].set_position(('outward', 60))  # Position the third axis outward
ax3.plot(black_move_numbers, average_proportions, color='red', marker='s', linestyle=':', label='Proportion for Black Moves')
ax3.set_ylabel('Proportion of Black Moves', color='red')
ax3.tick_params(axis='y', labelcolor='red')

# Set x-axis ticks to include whole Black move numbers
ax1.set_xticks(black_move_numbers)

# Add legends and titles
fig.tight_layout()
plt.title('Average Black Win Rate, Games Remaining, and Proportions of Black Moves Across All Moves')
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')
ax3.legend(loc='lower right')

plt.show()
# no threshold