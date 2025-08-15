import chess
import chess.engine
import pygame
import google.generativeai as genai
import time

# Gemini API docs
api_key = ''

# Configure the Gemini API
genai.configure(api_key=api_key)

SQUARE_SIZE = 100
WIDTH, HEIGHT = SQUARE_SIZE * 8, SQUARE_SIZE * 8
#Chess pieces from images folder
PIECE_IMAGES = {
    'bB': 'images/bB.png', 'bK': 'images/bK.png', 'bN': 'images/bN.png',
    'bP': 'images/bP.png', 'bQ': 'images/bQ.png', 'bR': 'images/bR.png',
    'wB': 'images/wB.png', 'wK': 'images/wK.png', 'wN': 'images/wN.png',
    'wP': 'images/wP.png', 'wQ': 'images/wQ.png', 'wR': 'images/wR.png'
}
STOCKFISH_PATH = "/opt/homebrew/bin/stockfish"

#Loading the chess images and checking if it loaded properly
def load_images():
    pieces = {}
    for piece, path in PIECE_IMAGES.items():
        try:
            pieces[piece] = pygame.transform.scale(pygame.image.load(path), (SQUARE_SIZE, SQUARE_SIZE))
            print(f"Image {piece}.png loaded successfully.")
        except pygame.error as e:
            print(f"Error loading image {piece}.png: {e}")
    return pieces

#chess board 
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

def log_to_file(session_id, prompt_no, prompt_or_response, is_prompt):
    with open("gemini_responses.txt", "a") as log_file:
        p_or_r = "P" if is_prompt else "R"
        log_entry = f"{session_id}${prompt_no}${p_or_r}${prompt_or_response}\n"
        log_file.write(log_entry)

#gemini API docs
def get_gemini_move(fen, session_id, prompt_no, delay=6):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"Given the chess position {fen}, what is the best move for black in UCI (Universal Chess Interface) format ([Starting Square][Ending Square])? Do not give any other thing other than the move itself."
    
    log_to_file(session_id, prompt_no, prompt, True)  

    try:
        response = model.generate_content(prompt)
        print("Response from Gemini:", response.text)
        time.sleep(delay)  # Rate limit
        move = response.text.strip()
        
        log_to_file(session_id, prompt_no, response.text, False) 
        
        return move
    except Exception as e:
        print(f"Failed to get move from Gemini: {e}")
        return None

# stockfish vs gemini , we give FEN as input to gemini , and ask for next move in UCI
def run_single_game(screen, engine, pieces, session_id):
    board = chess.Board()
    invalid_move_by_gemini = False
    clock = pygame.time.Clock()
    prompt_no = 1

    while not board.is_game_over() and not invalid_move_by_gemini:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, False
                
# Here gemini is considered for black and white for stockfish
        if board.turn == chess.WHITE:
            result = engine.play(board, chess.engine.Limit(time=0.1))
            move = result.move
            board.push(move)
            print("Stockfish move: ", move.uci())  # Stockfish move
        else:
            fen = board.fen()
            print("Current FEN:")
            print(fen)
            move_uci = get_gemini_move(fen, session_id, prompt_no)
            prompt_no += 1
            if move_uci:
                try:
                    move = chess.Move.from_uci(move_uci)
                    if move in board.legal_moves:  # check legal moves
                        board.push(move)
                        print("Gemini move: ", move.uci())  # Gemini move
                    else:
                        print("Invalid move by Gemini.")
                        invalid_move_by_gemini = True
                except Exception as e:
                    print(f"Failed to process move from Gemini: {e}")
                    invalid_move_by_gemini = True
            else:
                print("No move returned by Gemini.")
                invalid_move_by_gemini = True

        screen.fill((200, 200, 200))
        draw_board(screen, board, pieces)
        pygame.display.flip()
        clock.tick(15)

    return True, invalid_move_by_gemini

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess Game: Stockfish vs Gemini")
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    pieces = load_images()

    session_count = 0
    max_sessions = 100

    while session_count < max_sessions:
        session_id = session_count + 1
        print(f"Starting game session {session_id}...")
        session_active, gemini_invalid = run_single_game(screen, engine, pieces, session_id)

        if gemini_invalid:
            print(f"Gemini gave an invalid move in session {session_id}, moving to the next session.")
            session_count += 1
        else:
            print(f"Game over, restarting session {session_id}.")

    engine.quit()
    pygame.quit()

if __name__ == "__main__":
    main()
