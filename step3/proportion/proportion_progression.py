import sqlite3
from typing import List, Optional


class ChessDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_total_games(self, move_sequence: List[str]) -> Optional[int]:
        """Get the total number of games for a given move sequence."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            parent_id = None

            for move in move_sequence:
                cursor.execute("""
                    SELECT id, black_win_count, white_win_count, draw_count, unfinished_count
                    FROM Moves 
                    WHERE move = ? AND parent_id IS ?
                """, (move, parent_id))

                row = cursor.fetchone()
                if not row:
                    print(f"Move not found in DB for sequence: {' '.join(move_sequence)}")
                    return None  # Stop if any move is not found in the database

                parent_id = row[0]  # Move to the next move's parent ID

            # Calculate the total number of games for the final move in the sequence
            total_games = sum(row[1:])
            print(f"Total games for sequence {' '.join(move_sequence)}: {total_games}")
            return total_games if total_games > 0 else 0

    def get_total_games_in_db(self) -> int:
        """Get the total number of games in the entire database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT SUM(black_win_count + white_win_count + draw_count + unfinished_count) 
                FROM Moves
                WHERE parent_id IS NULL
            """)
            result = cursor.fetchone()
            print(f"Total games in database: {result[0] if result else 0}")
            return result[0] if result and result[0] else 0


def process_move_sequences(input_file: str, output_file: str, db: ChessDatabase):
    """Process each move sequence and save proportions for Black moves only."""
    total_games_in_db = db.get_total_games_in_db()
    if total_games_in_db == 0:
        print("Total games in database is 0. Exiting.")
        return

    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for game_number, line in enumerate(infile, start=1):
            move_sequence = line.strip().split()
            cumulative_moves = []
            proportions = []  # Array to store proportions for Black moves

            print(f"\nProcessing Game {game_number} with move sequence: {line.strip()}")

            previous_total_games = total_games_in_db  # Start with the total games in the database

            for i, move in enumerate(move_sequence):
                cumulative_moves.append(move)
                print(f"Processing move {i + 1}: {move}")

                # Fetch the total games for the current cumulative sequence
                total_games = db.get_total_games(cumulative_moves)
                if total_games is None:
                    # If move not found, stop further processing for this game
                    print(f"Stopping processing for Game {game_number}: move '{move}' not found.")
                    cumulative_moves.pop()
                    break

                # Calculate proportion based on the previous total games
                proportion = total_games / previous_total_games if previous_total_games > 0 else 0

                # Process only Black moves (odd indices)
                if i % 2 != 0:  # Black moves have odd indices (1-based indexing)
                    print(f"Black move proportion for move {move}: {proportion:.4f}")
                    proportions.append(f"{proportion:.4f}")

                # Update the previous total games for the next iteration
                previous_total_games = total_games

            # Write proportions for Black moves as space-separated values to the output file
            outfile.write(" ".join(proportions) + "\n")
            print(f"Game {game_number}: Written proportions for Black moves to output file.")


def main():
    db = ChessDatabase('chess_game_data.db')
    # input_file = 'sample_proportion_moves.txt'  # Input file with move sequences
    input_file = '/Users/vyshnavigunda/Desktop/CHESS/commonseq/V_version_move_sequences_cleaned.txt'  # Input file with move sequences
    output_file = 'V_proportion_games_count_progression_black.txt'  # Output file for Black moves proportions

    process_move_sequences(input_file, output_file, db)
    print("Proportions progression for Black moves saved to", output_file)


if __name__ == "__main__":
    main()
