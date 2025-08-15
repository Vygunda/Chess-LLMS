import chess
import chess.engine
import google.generativeai as genai
import time
import pandas as pd
import matplotlib.pyplot as plt

# Configure Gemini API
api_key = ''
genai.configure(api_key=api_key)

# Path to Stockfish engine
STOCKFISH_PATH = "/opt/homebrew/bin/stockfish"

# Common and uncommon sequences
common_sequences =[

    ['e4','c5','Nf3'],
    ['e4','c5','Nf3','d6'],
    ['e4', 'e5', 'Nf3', 'Nc6'],  # Ruy-Lopez
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bc4'],  # Italian Game
    ['e4', 'c5'],                       # Sicilian Defense
    ['e4', 'e6'],                       # French Defense
    ['e4'],                       # Caro-Kann Defense
    ['e4', 'd6', 'd4'],          # Pirc Defense
    ['d4', 'd5'],                 # Queen's Gambit
    ['d4', 'Nf6', 'c4'],          # King's Indian Defense
    ['d4', 'Nf6', 'c4', 'e6', 'Nc3'],  # Nimzo-Indian Defense
    ['d4', 'Nf6', 'c4', 'g6', 'Nc3'],   # Grünfeld Defense
    ['d4', 'd5'],                # London System
    ['d4', 'd5', 'c4'],           # Slav Defense
    ['c4'],                             # English Opening
    ['e4', 'd5'],                       # Scandinavian Defense
    ['e4', 'e5', 'Nc3'],                # Vienna Game
    ['d4', 'f5'],                       # Dutch Defense
    ['e4', 'Nf6'],                      # Alekhine's Defense
    ['e4', 'g6'],                       # Modern Defense
    ['d4', 'Nf6', 'c4', 'c5'],          # Benoni Defense
    ['d4', 'd5', 'e3'],                 # Stonewall Attack
    ['f4'],                             # Bird’s Opening
    ['Nf3'],                            # Reti Opening
    ['d4', 'Nf6', 'c4', 'e6', 'g3'],    # Catalan Opening
    ['e4', 'e5', 'f4'],                 # King’s Gambit
    ['e4', 'e5', 'Nf3', 'Nc6', 'd4'],   # Scotch Game
    ['e4', 'e5', 'Nf3', 'Nc6', 'Nc3'],  # Four Knights Game
    ['e4', 'e5', 'Nf3', 'Nf6'],         # Petrov's Defense
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bc4'],  # Giuoco Piano
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bc4', 'Bc5'],  # Evans Gambit
    ['d4', 'Nf6', 'Bg5'],               # Trompowsky Attack
    ['e4', 'e5', 'Qh5', 'Nc6', 'Bc4', 'Nf6'],  # Scholar’s Mate
    ['f3', 'e5', 'g4'],         # Fool’s Mate
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'a6', 'Ba4', 'Nf6'],  # Back-Rank Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5'],  # Knight Fork Idea
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5'],  # Pin Example
    ['e4', 'e5', 'Nf3', 'Nc6', 'd4'],  # Discovered Attack Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'd4'],  # Smothered Mate Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'Nf6', 'O-O'],  # Double Check Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'a6', 'Ba4', 'd6'],  # Windmill Setup
    ['e4', 'e5', 'Qh5', 'Nc6', 'Bc4', 'g6'],  # Perpetual Check Setup
    ['e4', 'e5', 'd4', 'exd4'],  # En passant Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5'],  # Promotion Tactic Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'd4'],  # Overloading Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5'],  # Zugzwang Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5'],  # Interference Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5'],  # Undermining Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'd4', 'exd4'],  # Trapped Piece Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'a6', 'Ba4'],  # Zwischenzug Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'Nf6', 'O-O'] # Decoy Setup
]

uncommon_sequences = [
    ['b4'],                             # Orangutan Opening
    ['g4'],                             # Grob Attack
    ['e4', 'e5', 'Nf3', 'Nc6', 'Be2'],  # Hungarian Defense
    ['e4', 'e5', 'Nf3', 'd5'],          # Elephant Gambit
    ['d4', 'd5', 'c4', 'e5'],           # Albin Countergambit
    ['e4', 'e5', 'Nf3', 'f5'],          # Latvian Gambit
    ['e4', 'c5', 'd4'],                 # Smith-Morra Gambit
    ['d4', 'd5', 'e4'],                 # Blackmar-Diemer Gambit
    ['d4', 'e5'],                       # Englund Gambit
    ['e4', 'b6'],                       # Owen's Defense
    ['e4', 'Nc6'],                      # Bird's Defense
    ['a4'],                             # Ware Opening
    ['e4', 'e5', 'Ke2'],                # Bongcloud Attack
    ['e4', 'a6'],                       # St. George Defense
    ['b4'],                             # Polish Opening
    ['h4'],                             # Kadas Opening
    ['e4', 'e5', 'Nf3', 'f6'],          # Damiano Defense
    ['e4', 'e5', 'Nf3', 'Nc6', 'Nxe5'], # Irish Gambit
    ['e4', 'b6', 'd4', 'g6', 'Nf3', 'Bg7'],  # Hippopotamus Defense
    ['e4', 'e6', 'd4', 'd5', 'Nd2', 'h6'],  # Czech Defense
    ['g3'],                             # King's Fianchetto
    ['e4', 'Nc6'],                      # Nimzowitsch Defense
    ['e4', 'g6', 'Bc4', 'Bg7', 'Qf3'],  # Monkey's Bum
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bc4', 'Bc5', 'Bxf7+'],  # Jerome Gambit
    ['e4', 'e5', 'Nf3', 'Nc6', 'Nc3', 'Nf6', 'Nxe5'],   # Halloween Gambit
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'a6', 'Ba4', 'd6'],  # Bishop and Knight Mate Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'Nf6', 'O-O', 'Nxe4'],  # King March Setup
    ['e4', 'e5', 'd4', 'exd4', 'c3', 'dxc3', 'bxc3', 'd5'],  # Underpromotion Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'd6', 'd4', 'exd4'],  # Stalemate Sacrifice Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'd4', 'exd4', 'c3'],         # Fortress Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'd6', 'd4'],          # Trojan Horse Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'a6', 'Ba4', 'Nf6'],  # King Hunt Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'a6', 'Ba4', 'b5'],   # Staircase Mate Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'Nf6', 'O-O', 'a6'],  # Corridor Mate Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'a6', 'Ba4', 'd5'],   # Damiano Mate Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'a6', 'Ba4', 'b5'],   # Epaulette Mate Setup
    ['e4', 'e5', 'd4', 'exd4', 'c3'],                      # Battering Ram Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'a6', 'Ba4', 'b5'],   # Arabian Mate Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'd4', 'exd4'],              # Swindle Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'a6', 'Ba4', 'b5'],   # Domino Effect Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'd6'],               # Triangulation Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'd6', 'd4'],         # Philidor’s Legacy Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'a6'],               # Lolli’s Mate Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'a6', 'Ba4'],        # Anastasia’s Mate Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'Nf6'],              # Boden’s Mate Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'a6', 'Ba4'],        # Cross-Check Setup
    ['g3', 'd5', 'Bg2', 'c6'],                             # Hypermodern Opening
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'a6', 'd4'],         # Intermezzo Sacrifice Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'd4', 'exd4', 'c3'],        # Double Bishop Mate Setup
    ['e4', 'c5', 'f4']                                # Pawn Storm Setup
]
def get_gemini_move(sequence):
    """
    Get the next move from Gemini.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    moves_str = ', '.join(sequence)
    time.sleep(6)  # Prevent rate limits
    prompt = f"Given the following moves: {moves_str}, what is the suggested best next move for black? Only return the move."

    try:
        response = model.generate_content(prompt)
        move = response.text.strip().lstrip('. ').strip()
        print(f"Gemini suggested move: {move}")
        return move
    except Exception as e:
        print(f"Failed to get move from Gemini: {e}")
        return None

def evaluate_move_with_stockfish(stockfish, sequence, gemini_move):
    """
    Evaluate Gemini's move using Stockfish.
    """
    board = chess.Board()
    try:
        for move in sequence:
            board.push_san(move)
    except ValueError as e:
        print(f"Invalid move in sequence: {move}. Error: {e}")
        return None, None

    # print(f"Current FEN: {board.fen()}")

    legal_moves = [board.san(move) for move in board.legal_moves]
    if gemini_move not in legal_moves:
        print(f"Gemini's move '{gemini_move}' is not a legal move. Legal moves: {legal_moves}")
        return None, None

    try:
        gemini_move_obj = board.parse_san(gemini_move)
        with stockfish.analysis(board, chess.engine.Limit(depth=30)) as analysis:
            best_moves = []
            for info in analysis:
                if "pv" in info:
                    best_moves.append(info)

            rank = next((i + 1 for i, info in enumerate(best_moves) if info["pv"][0] == gemini_move_obj), None)
            best_score = best_moves[0]["score"].relative.score()
            gemini_score = best_moves[rank - 1]["score"].relative.score() if rank else None
            score_difference = best_score - gemini_score if gemini_score is not None else None
            return rank, score_difference
    except Exception as e:
        print(f"Error evaluating Gemini's move with Stockfish: {e}")
        return None, None

def analyze_sequence(sequence, stockfish, game_no, num_sessions=1):
    """
    Analyze how Gemini performs for a given sequence across multiple sessions.
    """
    results = []
    for session in range(1, num_sessions + 1):
        print(f"\nGame {game_no}, Session {session} for sequence: {sequence}")
        gemini_move = get_gemini_move(sequence)
        if gemini_move:
            rank, score_diff = evaluate_move_with_stockfish(stockfish, sequence, gemini_move)
            results.append({'Game': game_no, 'Session': session, 'Gemini Move': gemini_move, 'Rank': rank, 'Score Difference': score_diff})
            print(f"Game {game_no}, Session {session}: Rank={rank}, Score Difference={score_diff}")
        else:
            results.append({'Game': game_no, 'Session': session, 'Gemini Move': None, 'Rank': None, 'Score Difference': None})
    return results

def save_results_to_file(results, filename):
    """
    Save the analysis results to a file with game numbers.
    """
    with open(filename, 'w') as f:
        for game_no, (sequence, data) in enumerate(results.items(), start=1):
            f.write(f"Game {game_no} - Sequence: {' '.join(sequence)}\n")
            for entry in data:
                f.write(f"{entry}\n")
            f.write("\n")

def plot_results(common_results, uncommon_results):
    """
    Plot the comparison between common and uncommon sequences.
    """
    common_scores = [res['Score Difference'] for seq in common_results.values() for res in seq if res['Score Difference'] is not None]
    uncommon_scores = [res['Score Difference'] for seq in uncommon_results.values() for res in seq if res['Score Difference'] is not None]

    plt.figure(figsize=(10, 6))
    plt.boxplot([common_scores, uncommon_scores], labels=['Common', 'Uncommon'])
    plt.title('Comparison of Gemini Move Quality Between Common and Uncommon Sequences')
    plt.ylabel('Score Difference (Centipawns)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

def main():
    stockfish = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

    common_results = {}
    uncommon_results = {}

    for game_no, seq in enumerate(common_sequences, start=1):
        results = analyze_sequence(seq, stockfish, game_no)
        common_results[tuple(seq)] = results

    save_results_to_file(common_results, "common_sequence_results_with_game_no.txt")

    for game_no, seq in enumerate(uncommon_sequences, start=1):
        results = analyze_sequence(seq, stockfish, game_no)
        uncommon_results[tuple(seq)] = results

    save_results_to_file(uncommon_results, "uncommon_sequence_results_with_game_no.txt")
    stockfish.quit()

    plot_results(common_results, uncommon_results)

if __name__ == "__main__":
    main()
