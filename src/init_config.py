import torch
import chess
import chess.engine

def init_chess_detection(self, capture_index):
    self.capture_index = capture_index
    self.device = "cuda" if torch.cuda.is_available() else "cpu"
    torch.cuda.empty_cache()
    self.model = self.load_model("weights/pavel_moveside.pt")
    self.board_model = self.load_model("weights/board_flip_detect.pt")
    self.stockfish_path = "stockfish"
    self.engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)
    self.square_coords = {}  # The square coordinates that have been cropped, key: notation, value: center x, center y
    self.coord_notation = {}  # The square coordinates that have been cropped, value: notation, key: center x, center y
    self.piece_coords = {} # coordinates of each piece, key : piece_name, value: coordinates
    self.Piece_notation = {} # piece and notation, key : notation, value : piece_name
    self.square_coord_orig = {} # The square coordinates that have not been cropped, key: notation, value: center x, center y
    self.coord_notation_orig = {} # The square coordinates that have been cropped, value: notation, key: center x, center y
    self.pieces_names = ["knight", "king", "queen", "bishop", "rook"]
    self.notations_names = [chess.square_name(name) for name in chess.SQUARES] # list of notations
    self.board = None
    self.flip = None
    self.move_side = None
    self.previous_board = None
    self.required_move_side = None
    self.screen_index = None