import cv2
import chess
import math
class ChessBoardGeneration:  
    def generate_notations_position(self, frame, x_coords, y_coords):
        square_coords = {}
        flip = False
        x_min, x_max = int(min(x_coords)), int(max(x_coords))
        y_min, y_max = int(min(y_coords)), int(max(y_coords))
        square_width = (x_max - x_min) / 8
        square_height = (y_max - y_min) / 8
        # Look for the "a1" notation    
        x1 = int(x_min + square_width)
        y1 = int(y_max - square_height)

        # Crop to the a1 square to see whether it is a1 or h8 (the board is flipped)
        frame1 = frame[y1:y_max, x_min:x1]

        if frame1 is None or frame1.size == 0:
            return None, flip  # Ensure flip has a default value
        else:  
            grayframe = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            resized_grayframe = cv2.resize(grayframe, (640, 640))
            resized_grayframe = cv2.merge([resized_grayframe, resized_grayframe, resized_grayframe])
            predicted_results = self.predict_board(resized_grayframe)
            files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
            ranks = ['8', '7', '6', '5', '4', '3', '2', '1']

            if len(predicted_results[0].boxes.cls.cpu().numpy()) != 0:
                predicted_notation = int(predicted_results[0].boxes.cls.cpu().numpy()[0])
                if predicted_notation == 1:
                    ranks = ranks[::-1]
                    files = files[::-1]
                    flip = True  # Flip is now explicitly set

            # Draw square notations
            for file_idx, file in enumerate(files):
                for rank_idx, rank in enumerate(ranks):
                    # Calculate square corners
                    x1 = int(x_min + file_idx * square_width)
                    y1 = int(y_min + rank_idx * square_height)
                    x2 = int(x1 + square_width)
                    y2 = int(y1 + square_height)

                    # Calculate center of square for text
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2

                    notation = file + rank
                    # cv2.putText(
                    #     frame,
                    #     notation,
                    #     (center_x, center_y),
                    #     cv2.FONT_HERSHEY_SIMPLEX,
                    #     0.4,
                    #     (0, 255, 0),
                    #     1
                    # )
                    square_coords[notation] = (center_x, center_y)

            return square_coords, flip

    
    def center_piece_coords(self, piece_coords):
        for name in piece_coords:
            for idx, piece in enumerate(piece_coords[name]):
                x_min, y_min, x_max, y_max = piece 
                x_middle = (x_min + x_max) / 2
                y_middle = (y_min + y_max) / 2
                piece_coords[name][idx] = int(x_middle), int(y_middle)
        return piece_coords
    def place_piece_notation(self, square_coords, piece_coords):
        Piece_notation = {}
        for notation, n_coord in square_coords.items():
            for piece, p_coord in piece_coords.items():
                for coord in p_coord: 
                    if abs(n_coord[0] - coord[0]) < 15 and abs(n_coord[1] - coord[1]) < 15:
                        if piece == 'w_pawn':
                            Piece_notation[notation] = 'P'
                        elif piece == 'w_king':
                            Piece_notation[notation] = 'K'
                        elif piece == 'w_queen':
                            Piece_notation[notation] = 'Q'
                        elif piece == 'b_pawn':
                            Piece_notation[notation] = 'p'
                        elif piece == 'b_king':
                            Piece_notation[notation] = 'k'
                        elif piece == 'b_queen':
                            Piece_notation[notation] = 'q'
                        elif piece == 'w_rook':
                            Piece_notation[notation] = 'R'
                        elif piece == 'b_rook':
                            Piece_notation[notation] = 'r'
                        elif piece == 'w_knight':
                            Piece_notation[notation] = 'N'
                        elif piece == 'b_knight':
                           Piece_notation[notation] = 'n'
                        elif piece == 'w_bishop':
                            Piece_notation[notation] = 'B'
                        elif piece == 'b_bishop':
                            Piece_notation[notation] = 'b'
                        break
            if notation not in Piece_notation:
                Piece_notation[notation] = 'nan'
        return Piece_notation
    def generate_fen_key(self, Piece_Notation, flip, required_move_side, move_side, previous_board):
        fen_key = ''
        if flip:
            for i in range(8, 0, -1):  # Iterate through ranks (rows) from 8 to 1
                empty_consec_counts = 0
                line = ''
                for notation in reversed(Piece_Notation.keys()):
                    if notation in [letter + str(i) for letter in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']]:
                        if Piece_Notation[notation] == 'nan':
                            empty_consec_counts += 1
                        else:
                            if empty_consec_counts != 0:
                                line += str(empty_consec_counts)
                                empty_consec_counts = 0
                            line += Piece_Notation[notation]
                if empty_consec_counts == 8:
                    line += '8'
                elif empty_consec_counts > 0:
                    line += str(empty_consec_counts)
                if i != 1:
                    fen_key += line + '/'
                else:
                    fen_key += line
        else:
            for i in range(8, 0, -1):  # Iterate through ranks (rows) from 8 to 1
                empty_consec_counts = 0
                line = ''
                for notation in Piece_Notation.keys():
                    if notation in [letter + str(i) for letter in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']]:
                        if Piece_Notation[notation] == 'nan':
                            empty_consec_counts += 1
                        else:
                            if empty_consec_counts != 0:
                                line += str(empty_consec_counts)
                                empty_consec_counts = 0
                            line += Piece_Notation[notation]
                if empty_consec_counts == 8:
                    line += '8'
                elif empty_consec_counts > 0:
                    line += str(empty_consec_counts)
                if i != 1:
                    fen_key += line + '/'
                else:
                    fen_key += line
        if required_move_side is None:
            if (move_side is None):
                fen_key += " w"
            elif (move_side):
                fen_key += " b"
            else:
                fen_key += " w"
        else:
            if (required_move_side):
                fen_key += " b"
            else:
                fen_key += " w"
        
        current_board = chess.Board(fen_key)
        # Add castling rights (evaluate for the current board)
        castling_rights = self.get_castling_rights(current_board)
        fen_key += ' ' + castling_rights

        # Add en passant target
        en_passant_target = self.get_en_passant_target(previous_board, current_board)
        fen_key += ' ' + en_passant_target
        return fen_key

    def get_castling_rights(self, current_board):
        """
        Determine castling rights by checking if the king or rooks have moved.
        """
        castling_rights = ''
        if (current_board is None):
            castling_rights += "KQkq"
            return castling_rights
        # Check white castling rights
        if current_board.piece_at(chess.E1) == chess.Piece.from_symbol('K'):
            if current_board.piece_at(chess.H1) == chess.Piece.from_symbol('R'):
                castling_rights += 'K'
            if current_board.piece_at(chess.A1) == chess.Piece.from_symbol('R'):
                castling_rights += 'Q'
        # Check black castling rights
        if current_board.piece_at(chess.E8) == chess.Piece.from_symbol('k'):
            if current_board.piece_at(chess.H8) == chess.Piece.from_symbol('r'):
                castling_rights += 'k'
            if current_board.piece_at(chess.A8) == chess.Piece.from_symbol('r'):
                castling_rights += 'q'
        # If no castling rights, use '-'
        if not castling_rights:
            castling_rights = '-'
        return castling_rights

    def get_en_passant_target(self, previous_board, current_board):
        """
        Determine the en passant target by checking if a pawn has moved two squares.
        """
        if not previous_board:
            return '-'  # No previous board, no en passant target

        # Find the move that was made
        move = self.find_move(previous_board, current_board)
        if move:
            piece = self.board.piece_at(move.to_square)
            if piece and piece.piece_type == chess.PAWN:
                if (chess.square_file(move.from_square) == chess.square_file(move.to_square) and
                    abs(move.to_square - move.from_square) == 16):
                    if piece.color == chess.WHITE:
                        return chess.square_name(move.to_square - 8)
                    else:
                        return chess.square_name(move.to_square + 8)
        return '-'
    def find_move(self, previous_board, current_board):
        """
        Find the move that was made between the previous and current board states
        """
        for move in previous_board.legal_moves:
            if previous_board.is_legal(move):
                temp_board = previous_board.copy()
                temp_board.push(move)
                if temp_board == current_board:
                    return move
        return None
    
    def generate_notation_piece(self, frame, x_coords, y_coords):
        frame, cropped_x_coords, cropped_y_coords = self.crop_frame(frame, x_coords, y_coords, 416)
        if (any(v is None for v in [frame, cropped_x_coords, cropped_y_coords])):
                    return None, None
        self.square_coords, self.flip = self.generate_notations_position(frame, cropped_x_coords, cropped_y_coords)
        if (any(v is None for v in [self.square_coords])):
                    return None, None
        results = self.predict(frame)
        predicted_img, self.piece_coords = self.map_piece_coords(results)
        piece_notation = self.place_piece_notation(self.square_coords, self.piece_coords)
        
        return piece_notation, predicted_img
