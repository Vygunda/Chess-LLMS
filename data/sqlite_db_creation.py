import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('chess_game_data2.db')
cursor = conn.cursor()

# Create Moves table
cursor.execute('''CREATE TABLE IF NOT EXISTS Moves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER,
    move TEXT NOT NULL,
    white_win_count INTEGER DEFAULT 0,
    black_win_count INTEGER DEFAULT 0,
    draw_count INTEGER DEFAULT 0,
    unfinished_count INTEGER DEFAULT 0,
    FOREIGN KEY (parent_id) REFERENCES Moves(id)
)''')

# Create GameStats table (its not needed )
cursor.execute('''CREATE TABLE IF NOT EXISTS GameStats (
    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
    result TEXT CHECK(result IN ('1-0', '0-1', '1/2-1/2', '*')) NOT NULL
)''')

# Commit changes and close the connection
conn.commit()
conn.close()
