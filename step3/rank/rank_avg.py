import sqlite3
import matplotlib.pyplot as plt
import signal
import sys

def get_move_rank(cursor, parent_id, gemini_move):
    """
    Find the rank of Gemini's move among the top moves for a given parent position.
    """
    cursor.execute('''
        SELECT id, move, white_win_count + black_win_count + draw_count + unfinished_count AS total_games
        FROM Moves
        WHERE parent_id = ?
        ORDER BY total_games DESC
        LIMIT 10
    ''', (parent_id,))
    moves = cursor.fetchall()

    for rank, (move_id, move, total_games) in enumerate(moves, start=1):
        if move == gemini_move:
            return rank
    return 11  # Return 11 if the move is not in the top 10

def analyze_gemini_moves_for_game(cursor, move_sequence, game_number):
    """
    Analyze the rank of each move made by Gemini (Black) in a single game sequence.
    """
    ranks = []  # Store ranks for this game
    parent_id = None

    for move_index, move in enumerate(move_sequence):
        if move_index % 2 == 1:  # Gemini moves are on odd indices (Black's turn)
            rank = get_move_rank(cursor, parent_id, move)
            ranks.append(str(rank))  # Append rank as a string

        # Update the parent_id to the current move's ID
        cursor.execute("SELECT id FROM Moves WHERE move = ? AND parent_id IS ?", (move, parent_id))
        result = cursor.fetchone()
        if result:
            parent_id = result[0]
        else:
            break  # Stop if no further moves can be processed

    print(f"Processed Game {game_number}: Ranks - {ranks}")
    return " ".join(ranks)  # Return space-separated ranks for this game

def analyze_multiple_games_from_file(file_path, db_path='chess_game_data.db', rank_file='ranks_results.txt'):
    """
    Read multiple games from a file and analyze Gemini's move rankings.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Open the output file in append mode
    with open(rank_file, 'a') as rank_file_writer:
        def save_progress(ranks):
            """
            Save the ranks for a single game.
            """
            rank_file_writer.write(ranks + "\n")
            rank_file_writer.flush()  # Ensure the data is written immediately

        # Process each game
        with open(file_path, 'r') as file:
            for game_number, line in enumerate(file, start=1):
                move_sequence = line.strip().split()
                if not move_sequence:
                    continue  # Skip empty lines

                print(f"Analyzing Game {game_number} with moves: {move_sequence}")
                game_ranks = analyze_gemini_moves_for_game(cursor, move_sequence, game_number)
                save_progress(game_ranks)  # Save ranks immediately after processing

    conn.close()

def plot_ranks_from_file(rank_file):
    """
    Plot the average rank and rank distribution from the saved rank file.
    """
    # Read the file
    with open(rank_file, 'r') as f:
        lines = f.readlines()

    # Parse the ranks
    ranks = [[int(rank) for rank in line.strip().split()] for line in lines]

    # Flatten the ranks and calculate average ranks per game
    all_ranks = [rank for game in ranks for rank in game]
    avg_ranks_per_game = [sum(game) / len(game) for game in ranks]

    # Plot the average rank per game
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, len(avg_ranks_per_game) + 1), avg_ranks_per_game, marker='o', label='Average Rank per Game')
    plt.xlabel('Game Number')
    plt.ylabel('Average Rank')
    plt.title('Average Rank of Gemini’s Moves per Game')
    plt.gca().invert_yaxis()  # Rank 1 should be at the top
    plt.grid(True)
    plt.legend()
    plt.show()

    # Plot the distribution of all ranks
    plt.figure(figsize=(10, 6))
    plt.hist(all_ranks, bins=range(1, 13), edgecolor='black', align='left', rwidth=0.8, label='Rank Distribution')
    plt.xlabel('Rank')
    plt.ylabel('Frequency')
    plt.title('Distribution of Gemini’s Move Ranks')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend()
    plt.show()

def main():
    # File path to the file containing games
    file_path = 'V_version_move_sequences_cleaned.txt'
    rank_file = 'ranks_results.txt'

    try:
        analyze_multiple_games_from_file(file_path, rank_file=rank_file)
        print(f"\nAnalysis completed. Results saved to '{rank_file}'.")
        plot_ranks_from_file(rank_file)
    except KeyboardInterrupt:
        print("\nAnalysis interrupted. Progress saved automatically.")

if __name__ == "__main__":
    main()
