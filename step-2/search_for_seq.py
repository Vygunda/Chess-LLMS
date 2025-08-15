import sqlite3
from typing import List, Optional

class ChessDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_statistics(self, move_sequence: List[str]) -> Optional[dict]:
        """Get cumulative statistics for a move sequence."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            parent_id = None

            for move in move_sequence:
                cursor.execute("""
                    SELECT id, white_win_count, black_win_count, 
                           draw_count, unfinished_count
                    FROM Moves 
                    WHERE move = ? AND parent_id IS ?
                """, (move, parent_id))

                row = cursor.fetchone()
                if not row:
                    print(f"Move not found: {move_sequence}")
                    return None

                parent_id = row[0]
                
            total_games = sum(row[1:])
            if total_games == 0:
                return {
                    'white_win_rate': 0,
                    'black_win_rate': 0,
                    'draw_rate': 0,
                    'unfinished_rate': 0,
                    'total_games': 0
                }

            return {
                'white_win_rate': row[1],
                'black_win_rate': row[2],
                'draw_rate': row[3],
                'unfinished_rate': row[4],
                'total_games': total_games
            }

def main():
    # Initialize the database connection
    db = ChessDatabase('chess_game_data.db')
    
    # Set the move sequence you want to search for (replace with any sequence)
    move_sequence = ['e4', 'c5']

    # Get statistics for the move sequence
    stats = db.get_statistics(move_sequence)
    
    if stats:
        print(f"\nStatistics for {' '.join(move_sequence)}:")
        for key, value in stats.items():
            print(f"{key}: {value}")
    else:
        print(f"No statistics found for {' '.join(move_sequence)}.")

if __name__ == "__main__":
    main()
