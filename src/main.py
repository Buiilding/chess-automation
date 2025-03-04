from prediction import Predictor
from scanner import ChessBoardScanner
from mouse_control import MouseController
from generation import ChessBoardGeneration
from init_config import init_chess_detection
# Pip install method (recommended)
import torch
import cv2
torch.cuda.is_available()
device = "cuda" if torch.cuda.is_available else "cpu"
torch.cuda.empty_cache()
import chess
import numpy as np
import time
import tkinter as tk
# when voice is called, it will take the last frame and run the detection on it,
class ObjectDetection( Predictor, ChessBoardScanner, MouseController, ChessBoardGeneration):
    def __init__(self, capture_index):
        init_chess_detection(self, capture_index)


    def is_valid_next_board(self, prev_board, next_board):
        """Check if next_board is a valid state after one legal move from prev_board."""
        next_board2 = next_board.copy() 
        for move in prev_board.legal_moves:
            temp_board = prev_board.copy()
            temp_board.push(move)
            fen_parts = temp_board.fen().split()[:2]
            new_fen = " ".join(fen_parts)
            temp_board.set_fen(new_fen)
            fen_parts = next_board2.fen().split()[:2]
            new_fen = " ".join(fen_parts)
            next_board2.set_fen(new_fen)
            if temp_board.fen() == next_board2.fen():
                return True
        return False
    def update_board(self):
        result = self.engine.play(self.board, chess.engine.Limit(time = 1.0))
        move = result.move
        fsquare = move.uci()[:2]  # First two characters (e.g., "e2")
        tsquare = move.uci()[2:4]  # Next two characters (e.g., "e4")
        from_x, from_y = self.square_coord_orig[fsquare]
        to_x, to_y = self.square_coord_orig[tsquare]
        self.move_mouse(from_x, from_y, to_x, to_y)
        print("board.fen() in update_board", self.board.fen())
        self.previous_board = self.board.copy(stack = True)
        self.previous_board.push(move)
        print("self.previous_board after push", self.previous_board.fen())
        split2 = self.previous_board.fen().split()
        move_side_prev = split2[1]
        if (move_side_prev == "w"):
            self.required_move_side =  True
        elif (move_side_prev == "b"):
            self.required_move_side = False
    def __call__(self):
        self.screen_index = int(input("Select screen: "))
        begin_board_position = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
        count = 0
        recheck = 0
        while (True):
            frame = self.screenshot(self.screen_index)
            corners = self.detect_corners(frame)
            if corners is not None:
                x_coords = [corner[0] for corner in corners]
                y_coords = [corner[1] for corner in corners]
                if (any(v is None for v in [frame, x_coords, y_coords])):
                    continue
                # original coordinates of the notations
                self.square_coord_orig, self.flip = self.generate_notations_position(frame, x_coords, y_coords)

                if (any(v is None for v in [self.square_coord_orig])):
                    continue

                self.Piece_Notation, predicted_img = self.generate_notation_piece(frame, x_coords, y_coords) #{"a1":"rook"}
                if (any(v is None for v in [self.Piece_Notation, predicted_img])):
                    continue
                # clear_output(wait=True)
                # display(self.square_coords)
                # display(self.piece_coords)
                ## Calling the two functions above will map the coordinates of the pieces to a board and we will be
                # be able to move the board with a mouse according to self.square_coord_orig before being cropped
                # cv2.imshow("lmao", predicted_img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                fen_key = self.generate_fen_key(self.Piece_Notation, self.flip, self.required_move_side, self.move_side, self.previous_board)
                self.board = chess.Board(fen_key)
                self.board = chess.Board(self.board.fen())
                print("current_board", self.board.fen())
                if (self.previous_board is not None):
                    print("previous_board", self.previous_board.fen())
                if (self.board.is_game_over()):
                    self.previous_board = None
                    self.move_side = None
                    self.required_move_side = None
                    self.flip = None
                    print("game over current board")
                    continue
                elif (self.previous_board is not None):
                    if (self.previous_board.is_game_over()):
                        self.previous_board = None
                        self.move_side = None
                        self.required_move_side = None
                        self.flip = None
                        print("game over prev board")
                        continue
                split = self.board.copy().fen().split()
                current_board_position = split[0]
                if (current_board_position == begin_board_position and not self.flip):
                    print('first move')
                    self.update_board()
                    count = 0
                elif (current_board_position == begin_board_position and self.flip):
                    print("waiting for white")
                    self.previous_board = None
                    self.move_side = None
                    self.required_move_side = None
                    self.flip = None
                    continue
                elif (self.board.is_valid() and self.previous_board is None):
                    print("self.previous_board does not exist, trying to move")
                    if (recheck == 0):
                        recheck += 1
                    self.update_board()
                    recheck = 0
                    count = 0
                elif (self.previous_board is not None and self.is_valid_next_board(self.previous_board, self.board)):
                    if (recheck == 0):
                        recheck += 1
                        continue
                    print("self.previous_board exist, trying to move")
                    self.update_board()
                    recheck = 0
                    count = 0
                elif (self.previous_board is not None and self.previous_board.fen().split()[0] == self.board.fen().split()[0]):
                    print("previous board == current board")
                    continue
                else:
                    count += 1
                    print("invalid board")
                    if count == 30:
                        root = tk.Tk()
                        root.title("Can't validate the board")

                        label = tk.Label(root, text="Quit or change to new board?", font=("Arial", 12))
                        label.pack(pady=10)

                        quit_selected = False
                        change_selected = False

                        def quit_action():
                            nonlocal quit_selected
                            quit_selected = True
                            root.destroy()

                        def change_action():
                            nonlocal change_selected
                            change_selected = True
                            root.destroy()

                        quit_button = tk.Button(root, text="Quit", command=quit_action)
                        quit_button.pack(side=tk.LEFT, padx=10, pady=10)

                        new_board_button = tk.Button(root, text="Refresh", command=change_action)
                        new_board_button.pack(side=tk.RIGHT, padx=10, pady=10)

                        root.mainloop()

                        if quit_selected:
                            # exit()
                            break
                        elif change_selected:
                            self.previous_board = None
                            self.move_side = None
                            self.required_move_side = None
                            self.flip = None
                # clear_output(wait=True)
                # # display(self.previous_board)
                # display(self.board)
                # display(self.square_coords)
                # display(self.piece_coords)
                # display(self.Piece_Notation)

        self.engine.quit()
        cv2.destroyAllWindows() 
        return self.square_coords, self.piece_coords, self.board

if __name__ == "__main__":
    square_coords, piece_coords, board = ObjectDetection(0)()
                