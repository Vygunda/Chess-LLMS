import sqlite3
from typing import List, Optional

class ChessDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_black_win_rate(self, move_sequence: List[str]) -> Optional[float]:
        """Get cumulative Black win rate for a move sequence."""
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
            
            total_games = sum(row[1:])
            if total_games == 0:
                print("No games found for the final sequence")
                return 0.0  # No games found, return 0% win rate

            black_win_rate = row[1] / total_games  # Calculate Black win rate
            return black_win_rate

def process_move_sequences(input_file: str, output_file: str, db: ChessDatabase):
    """Process each move sequence from an input file and save only Black win rates as space-separated values in the output file."""
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for game_number, line in enumerate(infile, start=1):
            move_sequence = line.strip().split()
            cumulative_moves = []
            black_win_rates = []  # Array to store black win rates for this game
            
            print(f"\nProcessing Game {game_number} with move sequence: {line.strip()}")
            
            for i, move in enumerate(move_sequence):
                cumulative_moves.append(move)
                
                # Only fetch stats after Black's moves (odd indices)
                if i % 2 != 0:  # i is odd for Black moves in the sequence
                    black_win_rate = db.get_black_win_rate(cumulative_moves)
                    if black_win_rate is None:
                        # If move not found, stop further processing for this game
                        cumulative_moves.pop()  # Remove the move that wasn't found
                        break
                    black_win_rates.append(f"{black_win_rate:.2%}")

            # Write only the Black win rates as space-separated values to the output file
            outfile.write(" ".join(black_win_rates) + "\n")
            print(f"Written Game {game_number} results to output file")

def main():
    db = ChessDatabase('chess_game_data.db')
    input_file = 'move_sequences_cleaned.txt'   # Input file with move sequences
    output_file = 'black_winrate_array_progression.txt'  # Output file for Black winrate array progression
    
    process_move_sequences(input_file, output_file, db)
    print("Black winrate array progression for each game saved to", output_file)

if __name__ == "__main__":
    main() 
