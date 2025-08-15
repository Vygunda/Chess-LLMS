import pygame
import chess
import chess.engine
import os

SQUARE_SIZE = 100
WIDTH, HEIGHT = SQUARE_SIZE * 8, SQUARE_SIZE * 8

#Chess pieces from images folder
PIECE_IMAGES = {
    'bB': 'images/bP.png', 'bK': 'images/bN.png', 'bN': 'images/bB.png',
    'bP': 'images/bR.png', 'bQ': 'images/bQ.png', 'bR': 'images/bK.png',
    'wB': 'images/wP.png', 'wK': 'images/wN.png', 'wN': 'images/wB.png',
    'wP': 'images/wR.png', 'wQ': 'images/wQ.png', 'wR': 'images/wK.png'
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
    colors = [(255, 223, 186), (139, 69, 19)]  # Light brown and dark brown
    for r in range(8):
        for c in range(8):
            color = colors[(r + c) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            piece = board.piece_at(r * 8 + c)
            if piece:
                piece_color = 'w' if piece.color else 'b'
                piece_key = f"{piece_color}{'BKNPQR'[piece.piece_type - 1]}"
                if piece_key in pieces:
                    screen.blit(pieces[piece_key], pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def main():
    pygame.init()
    print("Pygame initialized.")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess Board")
    clock = pygame.time.Clock()

    try:
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        print("Stockfish engine initialized.")
    except Exception as e:
        print(f"Error initializing Stockfish engine: {e}")
        return

    board = chess.Board()
    print("New chess board created.")

    pieces = load_images()

    running = True
    game_over = False
    result_text = ""

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not game_over:
            if board.turn == chess.WHITE:
                side = "White"
            else:
                side = "Black"

            try:
                result = engine.play(board, chess.engine.Limit(time=2.0))
                move = result.move
                if move:
                    board.push(move)
                    print(f"{side} move made: {move}")

                    # Check if the game is over
                    if board.is_game_over():
                        game_over = True
                        result_text = f"Game over! Result: {board.result()}"
                        if board.result() == "1-0":
                            result_text += " White wins!"
                        elif board.result() == "0-1":
                            result_text += " Black wins!"
                        elif board.result() == "1/2-1/2":
                            result_text += " It's a draw!"
                else:
                    print("No move suggested by Stockfish.")
            except Exception as e:
                print(f"Error getting move from Stockfish: {e}")

            screen.fill((200, 200, 200)) 
            draw_board(screen, board, pieces)
            
            if game_over:
                font = pygame.font.Font(None, 74)
                text_surface = font.render(result_text, True, (255, 0, 0))  
                screen.blit(text_surface, (50, HEIGHT // 2 - 40))
            
            pygame.display.flip()
            clock.tick(30)

    # Close the engine
    engine.quit()
    pygame.quit()
    print("Engine closed and Pygame quit.")

if __name__ == "__main__":
    main()
