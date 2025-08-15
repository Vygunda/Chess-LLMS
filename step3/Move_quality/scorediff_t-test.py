import chess
import chess.engine
import google.generativeai as genai
import time
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind, f_oneway
# https://python-chess.readthedocs.io/en/latest/engine.html

# Configure Gemini API
api_key = ''
genai.configure(api_key=api_key)

# Path to Stockfish engine
STOCKFISH_PATH = "/opt/homebrew/bin/stockfish"

# Common and uncommon sequences # min 5 digits or more  for common
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
    ['e4', 'e5', 'Nf3', 'Nc6', 'Nc3'],  # Four Knights Game
    ['e4', 'e5', 'Nf3', 'Nf6'],         # Petrov's Defense
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bc4'],  # Giuoco Piano
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bc4', 'Bc5'],  # Evans Gambit
    ['d4', 'Nf6', 'Bg5'],               # Trompowsky Attack
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'a6', 'Ba4', 'Nf6'],  # Back-Rank Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5'],  # Knight Fork Idea
    ['e4', 'e5', 'Nf3', 'Nc6', 'd4'],  # Smothered Mate Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'Nf6', 'O-O'],  # Double Check Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'a6', 'Ba4', 'd6'],  # Windmill Setup
    ['e4', 'e5', 'd4', 'exd4'],  # En passant Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'd4'],  # Overloading Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'd4', 'exd4'],  # Trapped Piece Setup
    ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'a6', 'Ba4'],  # Zwischenzug Setup
]

uncommon_sequences = [ # max count in db is upto 4 digits so <=4
   ['g4'],         #Grob Opening                    
    ['e4', 'e5', 'Nf3', 'Nc6', 'Be2'],  
    ['e4', 'e5', 'Nf3', 'd5'],          
    ['e4', 'e5', 'Nf3', 'f5'],          
    ['d4', 'd5', 'e4'],              
    ['d4', 'e5'],                    
    ['a4'],                           
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

def get_gemini_move(sequence):
    """
    Get the next move from Gemini.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    moves_str = ', '.join(sequence)
    time.sleep(5)  # Prevent rate limits
    prompt = f"Given the following moves: {moves_str}, what is the suggested best next move for black? Only return the move."
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error getting move from Gemini: {e}")
        return None

def evaluate_move_with_stockfish(stockfish, sequence, gemini_move):
    """
    Evaluate Gemini's move using Stockfish and calculate centipawn difference, legality, and probability shift.
    """
    board = chess.Board()
    for move in sequence:
        try:
            board.push_san(move)
        except ValueError:
            print(f"Invalid move in sequence: {move}")
            return None, None, None, None

    legal_moves = [board.san(move) for move in board.legal_moves]
    if not gemini_move or gemini_move not in legal_moves:
        print(f"Gemini's move '{gemini_move}' is not a legal move.")
        return None, False, None, None

    # Evaluate using Stockfish
    with stockfish.analysis(board, chess.engine.Limit(depth=15)) as analysis:
        best_score = None
        gemini_score = None
        pre_prob = None
        post_prob = None

        # Get best score from Stockfish analysis
        for info in analysis:
            if "pv" in info and "score" in info:
                best_score = info["score"].relative.score()
                pre_prob = 1 / (1 + 10 ** (-best_score / 400)) if best_score is not None else None
                break

        # Check if best_score is valid
        if best_score is None:
            print("Best score from Stockfish is None. Skipping.")
            return None, True, None, None

        # Evaluate Gemini's move
        try:
            gemini_move_obj = board.parse_san(gemini_move)
            board.push(gemini_move_obj)
            gemini_analysis = stockfish.analyse(board, chess.engine.Limit(depth=15))
            gemini_score = gemini_analysis["score"].relative.score() if "score" in gemini_analysis else None
            post_prob = 1 / (1 + 10 ** (-gemini_score / 400)) if gemini_score is not None else None
        except Exception as e:
            print(f"Error evaluating Gemini's move: {e}")
            return None, True, None, None

        # Check if gemini_score is valid
        if gemini_score is None:
            print("Gemini's score from Stockfish is None. Skipping.")
            return None, True, None, None

        centipawn_diff = best_score - gemini_score
        prob_shift = post_prob - pre_prob if post_prob is not None and pre_prob is not None else None

        return centipawn_diff, True, prob_shift, best_score


def analyze_sequences(stockfish, sequences, label):
    """
    Analyze sequences and calculate metrics.
    """
    results = []
    for i, sequence in enumerate(sequences, start=1):
        print(f"Analyzing {label} sequence {i}: {sequence}")
        gemini_move = get_gemini_move(sequence)
        if gemini_move:
            centipawn_diff, is_legal, prob_shift, best_score = evaluate_move_with_stockfish(stockfish, sequence, gemini_move)
            results.append({
                'Sequence': ' '.join(sequence),
                'Centipawn Difference': centipawn_diff,
                'Is Legal': is_legal,
                'Win Probability Shift': prob_shift,
                'Best Score': best_score
            })
    return results

def classify_moves(results):
    """
    Classify moves into blunders, mistakes, and good moves based on centipawn difference.
    """
    for result in results:
        if result['Centipawn Difference'] is not None:
            if result['Centipawn Difference'] > 300:
                result['Move Quality'] = 'Blunder'
            elif 100 < result['Centipawn Difference'] <= 300:
                result['Move Quality'] = 'Mistake'
            else:
                result['Move Quality'] = 'Good'
    return results

def save_to_file(results, filename):
    """
    Save results to a CSV file.
    """
    df = pd.DataFrame(results)
    df.to_csv(filename, index=False)
    print(f"Results saved to {filename}")

def perform_statistical_tests(metric1, metric2, label1, label2):
    """
    Perform t-test and ANOVA on two metrics.
    """
    t_stat, t_pvalue = ttest_ind(metric1, metric2, equal_var=False)
    f_stat, f_pvalue = f_oneway(metric1, metric2)

    print(f"\nStatistical Tests ({label1} vs. {label2}):")
    print(f"T-Test: t-statistic = {t_stat:.2f}, p-value = {t_pvalue:.4f}")
    print(f"ANOVA: F-statistic = {f_stat:.2f}, p-value = {f_pvalue:.4f}")

def plot_results(common_results, uncommon_results):
    """
    Plot comparisons for centipawn differences, legal move proportions, and win probability shifts.
    """
    common_cd = [res['Centipawn Difference'] for res in common_results if res['Centipawn Difference'] is not None]
    uncommon_cd = [res['Centipawn Difference'] for res in uncommon_results if res['Centipawn Difference'] is not None]

    common_prob = [res['Win Probability Shift'] for res in common_results if res['Win Probability Shift'] is not None]
    uncommon_prob = [res['Win Probability Shift'] for res in uncommon_results if res['Win Probability Shift'] is not None]

    common_legal = sum(res['Is Legal'] for res in common_results) / len(common_results)
    uncommon_legal = sum(res['Is Legal'] for res in uncommon_results) / len(uncommon_results)

    plt.figure(figsize=(10, 6))
    plt.boxplot([common_cd, uncommon_cd], labels=['Common', 'Uncommon'])
    plt.title('Centipawn Difference: Common vs. Uncommon Sequences')
    plt.ylabel('Centipawn Difference')
    plt.grid(True)
    plt.show()

    plt.figure(figsize=(10, 6))
    plt.boxplot([common_prob, uncommon_prob], labels=['Common', 'Uncommon'])
    plt.title('Win Probability Shift: Common vs. Uncommon Sequences')
    plt.ylabel('Win Probability Shift')
    plt.grid(True)
    plt.show()

    plt.figure(figsize=(6, 6))
    plt.bar(['Common', 'Uncommon'], [common_legal, uncommon_legal])
    plt.title('Proportion of Legal Moves')
    plt.ylabel('Proportion')
    plt.ylim(0, 1)
    plt.grid(axis='y')
    plt.show()

def main():
    stockfish = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

    # Analyze common and uncommon sequences
    common_results = analyze_sequences(stockfish, common_sequences, "Common")
    uncommon_results = analyze_sequences(stockfish, uncommon_sequences, "Uncommon")

    # Classify moves
    common_results = classify_moves(common_results)
    uncommon_results = classify_moves(uncommon_results)

    # Save to files
    save_to_file(common_results, "common_scores2.csv")
    save_to_file(uncommon_results, "uncommon_scores2.csv")

    # Perform statistical tests
    perform_statistical_tests(
        [res['Centipawn Difference'] for res in common_results if res['Centipawn Difference'] is not None],
        [res['Centipawn Difference'] for res in uncommon_results if res['Centipawn Difference'] is not None],
        "Common", "Uncommon"
    )

    # Plot results
    plot_results(common_results, uncommon_results)

    stockfish.quit()

if __name__ == "__main__":
    main()
