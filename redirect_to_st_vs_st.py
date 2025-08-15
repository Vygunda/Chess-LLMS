import chess
import chess.engine
import pygame
import google.generativeai as genai
import time

# Gemini API key setup
api_key = 'AIzaSyCgcpWcH4s4ZnjEYW8nin1TPQv0HBWHwJ4'
genai.configure(api_key=api_key)

SQUARE_SIZE = 100
WIDTH, HEIGHT = SQUARE_SIZE * 8, SQUARE_SIZE * 8
PIECE_IMAGES = {
    'bB': 'images/bB.png', 'bK': 'images/bK.png', 'bN': 'images/bN.png',
    'bP': 'images/bP.png', 'bQ': 'images/bQ.png', 'bR': 'images/bR.png',
    'wB': 'images/wB.png', 'wK': 'images/wK.png', 'wN': 'images/wN.png',
    'wP': 'images/wP.png', 'wQ': 'images/wQ.png', 'wR': 'images/wR.png'
}
STOCKFISH_PATH = "/opt/homebrew/bin/stockfish"

# Function to convert SAN move history to FEN
def get_fen_from_moves(move_history):
    board = chess.Board()  
    for san_move in move_history:
        board.push_san(san_move)  # Apply each SAN move
    return board.fen()

def load_images():
    pieces = {}
    for piece, path in PIECE_IMAGES.items():
        try:
            pieces[piece] = pygame.transform.scale(pygame.image.load(path), (SQUARE_SIZE, SQUARE_SIZE))
            print(f"Image {piece}.png loaded successfully.")
        except pygame.error as e:
            print(f"Error loading image {piece}.png: {e}")
    return pieces

def draw_board(screen, board, pieces):
    colors = [(255, 223, 186), (139, 69, 19)]  # Light and dark brown
    for r in range(8):
        for c in range(8):
            color = colors[(r + c) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            piece = board.piece_at(r * 8 + c)
            if piece:
                piece_color = 'w' if piece.color else 'b'
                piece_key = f"{piece_color}{'PNBRQK'[piece.piece_type - 1]}"
                if piece_key in pieces:
                    screen.blit(pieces[piece_key], pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def get_gemini_move(move_list, delay=6):
    model = genai.GenerativeModel("gemini-1.5-flash")
    moves_str = ', '.join(move_list)
    full_prompt = f"Given the following moves: {moves_str}, what is the suggested best next move for black based on these previous moves, do not give any other thing give only black move"
    try:
        response = model.generate_content(full_prompt)
        exact_response = response.text 
        print("Response from Gemini:", exact_response)
        time.sleep(delay)  # Rate limit
        move = exact_response.strip().lstrip('. ').strip() 
        print("Gemini move:", move)
        return move, full_prompt, exact_response  
    except Exception as e:
        print(f"Failed to get move from Gemini: {e}")
        return None, full_prompt, "Error: No response from Gemini"

def run_game(session_number, combined_log_file):
    print(f"Starting Game {session_number}...")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(f"Chess Game {session_number}: Stockfish vs Gemini")
    clock = pygame.time.Clock()
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    board = chess.Board()
    move_history = []
    pieces = load_images()
    
    prompt_no = 0  
    running = True
    switch_to_stockfish_vs_stockfish = False  # Flag to switch to Stockfish vs Stockfish
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not board.is_game_over():
            # Stockfish 1's turn (white moves)
            if board.turn == chess.WHITE or switch_to_stockfish_vs_stockfish:
                result = engine.play(board, chess.engine.Limit(time=0.1))
                move = result.move
                san_move = board.san(move)  
                move_history.append(san_move)  
                board.push(move)
                print("Stockfish 1 move: ", san_move)

                # Log Stockfish 1 move if it's White's turn or Stockfish has taken over both sides
                with open(combined_log_file, 'a') as f:
                    if board.turn == chess.WHITE:
                        f.write(f"{session_number}${prompt_no}$Stockfish 1 Move${san_move}\n")  # Stockfish 1 move as white
                    else:
                        f.write(f"{session_number}${prompt_no}$Stockfish 2 Move${san_move}\n")  # Stockfish 2 move as black

                fen = get_fen_from_moves(move_history)
                print("Current FEN:", fen)

            # Gemini's turn (black moves)
            else:
                if not switch_to_stockfish_vs_stockfish:
                    print("Move history:", move_history)
                    prompt_no += 1 
                    gemini_san_move, full_prompt, exact_response = get_gemini_move(move_history)

                    with open(combined_log_file, 'a') as f:
                        f.write(f"{session_number}${prompt_no}$P${full_prompt}\n")  
                        f.write(f"{session_number}${prompt_no}$R${exact_response}\n")  

                    if gemini_san_move:
                        try:
                            if gemini_san_move in [board.san(move) for move in board.legal_moves]:
                                board.push_san(gemini_san_move)
                                move_history.append(gemini_san_move) 
                                print("Gemini move: ", gemini_san_move)

                                fen = get_fen_from_moves(move_history)
                                print("Current FEN:", fen)
                            else:
                                print("Invalid move by Gemini.")
                                switch_to_stockfish_vs_stockfish = True  # Switch to Stockfish vs Stockfish
                                prompt_no += 1  # Increment prompt number for logging
                        except Exception as e:
                            print(f"Failed to process move from Gemini: {e}")
                            switch_to_stockfish_vs_stockfish = True  # Switch to Stockfish vs Stockfish
                            prompt_no += 1  # Increment prompt number for logging
                    else:
                        print("No move returned by Gemini.")
                        switch_to_stockfish_vs_stockfish = True  # Switch to Stockfish vs Stockfish
                        prompt_no += 1  # Increment prompt number for logging

        # Check if the game is over and if so, exit the loop
        if board.is_game_over():
            print(f"Game over. Result: {board.result()}")
            running = False

        screen.fill((200, 200, 200))
        draw_board(screen, board, pieces)
        pygame.display.flip()
        clock.tick(15)

    engine.quit()
    pygame.quit()

    print(f"Game {session_number} over. Move history:", move_history)
    return True


def main():
    combined_log_file = "combined_game_sessions.txt"  # One file for all 10 games
    
    with open(combined_log_file, 'w') as f:
        f.write("SessionID$PromptNo$P/R$PromptOrResponse\n")

    for game_number in range(1, 3):  # Run 10 games
        game_result = run_game(game_number, combined_log_file)
        if not game_result:
            print(f"Game {game_number} stopped due to invalid move by Gemini. Moving to the next game.")
            continue  
    print("Session finished.")

if __name__ == "__main__":
    main()
