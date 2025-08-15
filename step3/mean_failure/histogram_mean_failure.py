import pandas as pd
import matplotlib.pyplot as plt

# Load data
moves_to_failure = []
with open('V_black_winrate_array_progression.txt', 'r') as file:
    for line in file:
        # Count the moves (each line is a sequence of moves until failure)
        rates = [float(x.strip('%')) for x in line.strip().split()]
        moves_to_failure.append(len(rates))  # Number of moves until failure

# Convert to DataFrame
moves_df = pd.DataFrame(moves_to_failure, columns=['Moves to Failure'])

# Print total number of games to verify data
total_games = len(moves_to_failure)
print("Total number of games:", total_games)  # Should print 1752

# Plotting the histogram
plt.figure(figsize=(10, 6))
bin_counts, bins, _ = plt.hist(moves_df['Moves to Failure'], bins=range(1, max(moves_to_failure) + 2), color='lightblue', edgecolor='black')

# Print the bin counts to verify that the total is correct
print("Counts in each bin:", bin_counts)
print("Total games in bins:", sum(bin_counts))  # Should also sum to 1752

# Add a vertical line for the mean
mean_value = moves_df['Moves to Failure'].mean()
plt.axvline(mean_value, color='red', linestyle='dashed', linewidth=1, label=f'Mean = {mean_value:.2f}')

# Set y-axis limit based on total number of games
plt.ylim(0, 1800)  # Adjust this to 1752 or slightly above for clarity

# Adding labels and title
plt.xlabel('Number of Moves Before Failure')
plt.ylabel('Number of Games')
plt.title('Distribution of Moves to Failure for Gemini')
plt.legend()
plt.show()
