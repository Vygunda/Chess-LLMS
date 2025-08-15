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
                    return None

                parent_id = row[0]
                
            total_games = sum(row[1:])
            return {
                'total_games': total_games
            }

def main():
    # Initialize the database connection
    db = ChessDatabase('chess_game_data.db')

    # List of move sequences to search for
    move_sequences = [
    ['g4'],                             # Grob Attack
    ['e4', 'e5', 'Nf3', 'Nc6', 'Be2'],  # Hungarian Defense
    ['e4', 'e5', 'Nf3', 'd5'],          # Elephant Gambit
    ['e4', 'e5', 'Nf3', 'f5'],          # Latvian Gambit
    ['d4', 'd5', 'e4'],                 # Blackmar-Diemer Gambit
    ['d4', 'e5'],                       # Englund Gambit
    ['a4'],                             # Ware Opening
    ['e4', 'e5', 'Ke2'],                # Bongcloud Attack
    ['e4', 'a6'],                       # St. George Defense
    ['h4'],                             # Kadas Opening
    ['e4', 'e5', 'Nf3', 'f6'],          # Damiano Defense
    ['e4', 'e5', 'Nf3', 'Nc6', 'Nxe5'], # Irish Gambit
    ['e4', 'b6', 'd4', 'g6', 'Nf3', 'Bg7'],  # Hippopotamus Defense
    ['e4', 'e6', 'd4', 'd5', 'Nd2', 'h6'],  # Czech Defense
    ['e4', 'g6', 'Bc4', 'Bg7', 'Qf3'],  # Monkey's Bum
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bc4', 'Bc5', 'Bxf7+'],  # Jerome Gambit
    ['e4', 'e5', 'Nf3', 'Nc6', 'Nc3', 'Nf6', 'Nxe5'],   # Halloween Gambit
    ['e4', 'e5', 'd4', 'exd4', 'c3', 'dxc3', 'bxc3', 'd5'],  # Underpromotion Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'd6', 'd4', 'exd4'],  # Stalemate Sacrifice Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'd4', 'exd4', 'c3'],         # Fortress Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'd6', 'd4'],          # Trojan Horse Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'a6', 'Ba4', 'b5'],   # Staircase Mate Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'Nf6', 'O-O', 'a6'],  # Corridor Mate Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'a6', 'Ba4', 'd5'],   # Damiano Mate Setup
    ['e4', 'e5', 'd4', 'exd4', 'c3'],                      # Battering Ram Setup
    ['g3', 'd5', 'Bg2', 'c6'],                             # Hypermodern Opening
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'a6', 'd4'],         # Intermezzo Sacrifice Setup
    ['e4', 'f6'],                     # Barnes Opening
    ['Nh3'],                          # Amar Opening
    ['a3'],                           # Anderssen Opening
    ['Na3'],                          # Durkin Opening
    ['h3'],                           # Clemenz Opening
    ['a4', 'e5'],                     # Desprez Opening
    ['e4', 'e5', 'Qh5'],              # King's Head Opening
    ['e4', 'f5'],                     # Fried Fox Defense
    ['e4', 'd5', 'Nf3'],              # Tennison Gambit
    ['f3', 'e5', 'g4', 'Qh4#'],       # Hammerschlag Opening (Fool's Mate)
    ['h3', 'a5'],                     # Creepy Crawly Opening
    ['g4', 'h5'],                     # Toilet Variation
    ['b4', 'd5']
    ]

    # Iterate over the move sequences and retrieve statistics
    for move_sequence in move_sequences:
        stats = db.get_statistics(move_sequence)
        if stats and stats['total_games']>0:  # Check for total_games > 5 digits
            print(f"Sequence: {' '.join(move_sequence)}, Total Games: {stats['total_games']}")

if __name__ == "__main__":
    main()
