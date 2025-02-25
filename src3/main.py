from prediction import Predictor
from scanner import ChessBoardScanner
from mouse_control import MouseController
from generation import ChessBoardGeneration
from init_config import init_chess_detection
# Pip install method (recommended)
import torch
torch.cuda.is_available()
device = "cuda" if torch.cuda.is_available else "cpu"
torch.cuda.empty_cache()
import chess
# when voice is called, it will take the last frame and run the detection on it,
class ObjectDetection( Predictor, ChessBoardScanner, MouseController, ChessBoardGeneration):
    def __init__(self, capture_index):
        init_chess_detection(self, capture_index)

    def __call__(self):
        self.screen_index = int(input("Select screen: "))
        begin_board_position = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
        count = 0
        while (True):
            frame = self.screenshot(self.screen_index)
            corners = self.detect_corners(frame)
            if corners is not None:
                x_coords = [corner[0] for corner in corners]
                y_coords = [corner[1] for corner in corners]
                if (any(v is None for v in [frame, x_coords, y_coords])):
                    continue
                self.square_coord_orig, self.coord_notation_orig = self.generate_notations_position(frame, x_coords, y_coords)
                if (any(v is None for v in [self.square_coord_orig, self.coord_notation_orig])):
                    continue
                frame, resized_x_min, resized_y_min, resized_x_max, resized_y_max = self.crop_frame(frame,x_coords, y_coords)
                if (any(v is None for v in [frame, resized_x_min, resized_y_min, resized_x_max, resized_y_max])):
                    continue
                self.square_coords, self.coord_notation = self.generate_notations_position_resized(frame, 
                                                                                                    resized_x_max, 
                                                                                                    resized_x_min, 
                                                                                                    resized_y_max, 
                                                                                                    resized_y_min)
                if (any(v is None for v in [self.square_coords, self.coord_notation])):
                    continue
                results = self.predict(frame)
                predicted_img, self.piece_coords = self.map_piece_coords(results) # give the predicted image and add the coordinates of the piece to self.piece_coords
                self.Piece_Notation = self.place_piece_notation(self.square_coords, self.piece_coords) # {"a1" : "rook"}
                fen_key = self.generate_fen_key(self.Piece_Notation, self.flip, self.required_move_side, self.move_side, self.previous_board)
                self.board = chess.Board(fen_key)
                self.board = chess.Board(self.board.fen())

        self.engine.quit()
        cv2.destroyAllWindows() 
        return self.square_coords, self.piece_coords, self.board

if __name__ == "__main__":
    square_coords, piece_coords, board = ObjectDetection(0)()
                