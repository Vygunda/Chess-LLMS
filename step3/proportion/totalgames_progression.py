import sqlite3
from typing import List, Optional

class ChessDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_total_games(self, move_sequence: List[str]) -> Optional[int]:
        """Get total number of games for a move sequence."""
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

            # Calculate total number of games for the final move in the sequence
            total_games = sum(row[1:])
            return total_games if total_games > 0 else 0

def process_move_sequences(input_file: str, output_file: str, db: ChessDatabase):
    """Process each move sequence from an input file and save total game counts as space-separated values in the output file."""
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for game_number, line in enumerate(infile, start=1):
            move_sequence = line.strip().split()
            cumulative_moves = []
            total_games_counts = []  # Array to store total game counts for this game
            
            print(f"\nProcessing Game {game_number} with move sequence: {line.strip()}")
            
            for i, move in enumerate(move_sequence):
                cumulative_moves.append(move)
                
                # Only fetch stats after Black's moves (odd indices)
                if i % 2 != 0:  # i is odd for Black moves in the sequence
                    total_games = db.get_total_games(cumulative_moves)
                    if total_games is None:
                        # If move not found, stop further processing for this game
                        cumulative_moves.pop()  # Remove the move that wasn't found
                        break
                    total_games_counts.append(str(total_games))

            # Write only the total game counts as space-separated values to the output file
            outfile.write(" ".join(total_games_counts) + "\n")
            print(f"Written Game {game_number} results to output file")

def main():
    db = ChessDatabase('chess_game_data.db')
    input_file = '/Users/vyshnavigunda/Desktop/CHESS/commonseq/V_version_move_sequences_cleaned.txt'   # Input file with move sequences
    output_file = 'V_total_games_count_progression.txt'  # Output file for total games count progression
    
    process_move_sequences(input_file, output_file, db)
    print("Total games count progression for each game saved to", output_file)

if __name__ == "__main__":
    main()
