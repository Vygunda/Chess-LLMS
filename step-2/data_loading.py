import sqlite3
from tqdm import tqdm
from typing import List, Tuple, Optional

class ChessDatabase:
    def __init__(self, db_path: str, batch_size: int = 1000):
        self.db_path = db_path
        self.batch_size = batch_size  # Batching size for better performance
        self.move_count = 0  # To keep track of moves processed in the current batch

    def insert_move(self, conn: sqlite3.Connection, move_sequence: List[str], result: str):
        """Insert or update a move sequence and update stats at each level."""
        cursor = conn.cursor()
        parent_id = None

        try:
            # Loop through each move in the sequence
            for move in move_sequence:
                # Check if move already exists in the database
                cursor.execute("""
                    SELECT id FROM Moves WHERE move = ? AND parent_id IS ?
                """, (move, parent_id))
                row = cursor.fetchone()

                if row:
                    move_id = row[0]
                else:
                    # If move doesn't exist, insert it
                    cursor.execute("""
                        INSERT INTO Moves (move, parent_id, white_win_count, black_win_count, 
                                           draw_count, unfinished_count)
                        VALUES (?, ?, 0, 0, 0, 0)
                    """, (move, parent_id))
                    move_id = cursor.lastrowid # built-in in sqlite cursor object

                # Update statistics for this move
                self._update_statistics(cursor, move_id, result)
                
                # Move to the next level in the tree
                parent_id = move_id

            # Record the game result in the GameStats table
            cursor.execute("""
                INSERT INTO GameStats (result) VALUES (?);
            """, (result,))

            self.move_count += 1

            # Commit transaction after every batch
            if self.move_count % self.batch_size == 0:
                conn.commit()
                self.move_count = 0  # Reset move count after batch commit

        except Exception as e:
            conn.rollback()
            raise Exception(f"Error inserting move sequence: {e}")

    def _update_statistics(self, cursor: sqlite3.Cursor, move_id: int, result: str):
        """Update statistics for a single move."""
        if move_id is None:
            return
        
        # Update query for the stats
        update_sql = """
            UPDATE Moves SET 
                white_win_count = white_win_count + ?,
                black_win_count = black_win_count + ?,
                draw_count = draw_count + ?,
                unfinished_count = unfinished_count + ?
            WHERE id = ?
        """

        stats = {
            '1-0': (1, 0, 0, 0),
            '0-1': (0, 1, 0, 0),
            '1/2-1/2': (0, 0, 1, 0),
            '*': (0, 0, 0, 1)
        }.get(result, (0, 0, 0, 1))

        cursor.execute(update_sql, (*stats, move_id))
        # print(f"Updating stats for move ID {move_id}: W: {stats[0]}, B: {stats[1]}, D: {stats[2]}, U: {stats[3]}")

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

    def process_pgn_file(self, pgn_file: str):
        """Process a PGN file and insert moves."""
        with sqlite3.connect(self.db_path) as conn:
            # Get total number of lines in the file for the progress bar
            total_lines = sum(1 for _ in open(pgn_file))
            with open(pgn_file, 'r') as file:
                with tqdm(total=total_lines, desc="Processing PGN") as pbar:
                    for line_num, line in enumerate(file):
                        line = line.strip()
                        if line:
                            try:
                                moves, result = self._parse_pgn_line(line)
                                self.insert_move(conn, moves, result)
                            except Exception as e:
                                # Log errors with line numbers in error_log.txt
                                with open("error_log.txt", "a") as log_file:
                                    log_file.write(f"Error processing line {line_num + 1}: {line}. Error: {e}\n")
                                continue
                        pbar.update(1)  # Update progress bar

            # Final commit after processing all moves
            conn.commit()

    @staticmethod
    def _parse_pgn_line(line: str) -> Tuple[List[str], str]:
        """Parse a PGN line."""
        parts = line.split()
        if len(parts) < 2:
            raise ValueError("Invalid PGN line format")
        
        result = parts[-1]
        if result not in ['1-0', '0-1', '1/2-1/2', '*']:
            raise ValueError(f"Invalid result: {result}")
        
        moves = parts[:-1]
        return moves, result

def main():
    # Initialize the database and process a PGN file
    db = ChessDatabase('chess_game_data.db', batch_size=1000)  # Set batch size for performance
    db.process_pgn_file('formatted_extracted_moves.pgn')
    
    # Get statistics for a sequence of moves
    stats = db.get_statistics(['e4','e5','Nf3'])
    if stats:
        print("\nStatistics for e4 e5 Nf3:")
        for key, value in stats.items():
            print(f"{key}: {value}")

if __name__ == "__main__":
    main()
