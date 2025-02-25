import cv2
import pyautogui
import numpy as np
from fen_chess_utils.utils import find_max_contour_area, find_outer_corners
from screeninfo import get_monitors
class ChessBoardScanner:
    def detect_corners(self,frame):
        #convert to grayscale for some reason
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        thresh  = cv2.adaptiveThreshold(
            src = gray,
            maxValue = 255, 
            adaptiveMethod = cv2.ADAPTIVE_THRESH_MEAN_C,
            thresholdType = cv2.THRESH_BINARY_INV,
            blockSize = 9,
            C = 3
        )
        # Find contours detect boundaries of objects, the curve joining along a boundary of an object that have the same color
        contours, _  = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Find the largest contour, the chessboard
        contours = find_max_contour_area(contours)
        if not contours:
            return None
        #Find corners from the contours
        c = contours[0]
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        corners = find_outer_corners(frame, approx)
        return corners
    def map_piece_coords(self, results):
        top_left_bottom_right_coords = []
        piece_coords = {}
        has_white = False
        has_black = False
        max_white_confidence = 0.0
        max_black_confidence = 0.0
        for result in results:
            box = result.boxes.cpu().numpy()
            top_left_bottom_right_coords.append(box.xyxy)
            if len(box.cls) != 0:
                for index, cls_id in enumerate(box.cls):
                    class_name = self.model.names[int(cls_id)]
                    confidence = box.conf[index]
                    if class_name not in piece_coords:
                        piece_coords[class_name] = [box.xyxy[index]]
                    else:
                        piece_coords[class_name].append(box.xyxy[index]) ## holy shit, now I know, the append is for pieces like pawns and knight when they have more than two pieces
                    if class_name == "white":
                        has_white = True
                        max_white_confidence = max(max_white_confidence, confidence)
                    elif class_name == "black":
                        has_black = True
                        max_black_confidence = max(max_black_confidence, confidence)
            if has_white and has_black:
                if (max_black_confidence > max_white_confidence):
                    self.move_side = False
                    print("has black")
                elif (max_black_confidence < max_white_confidence):
                    self.move_side = True
                    print("has white")
                else:
                    print("has none")
                    self.move_side = None
            elif has_white:
                self.move_side = True
                print("has white")
            elif has_black:
                print("has black")
                self.move_side = False
            else: 
                print("has none")
                self.move_side = None
        piece_coords = self.center_piece_coords(piece_coords)
        return results[0].plot(), piece_coords
    def crop_frame(self, frame, x_coords, y_coords, target_size):  
        # Get x_min, x_max, y_min, and y_max to determine the bounding box of the chessboard
        x_min, x_max = int(min(x_coords)), int(max(x_coords))
        y_min, y_max = int(min(y_coords)), int(max(y_coords))
        
        # Crop the frame to the detected chessboard region
        cropped_frame = frame[y_min:y_max, x_min:x_max]
        
        # Get original cropped size
        original_h, original_w = cropped_frame.shape[:2]

        # Resize to target size (416x416)
        resized_frame = cv2.resize(cropped_frame, (target_size, target_size))

        # Scale coordinates to match the resized frame
        scale_x = target_size / original_w
        scale_y = target_size / original_h
        resized_x_coords = [int((x - x_min) * scale_x) for x in x_coords]
        resized_y_coords = [int((y - y_min) * scale_y) for y in y_coords]

        return resized_frame, resized_x_coords, resized_y_coords

 
     
    def screenshot(self, screen_index):
        monitors = get_monitors()
        if screen_index > len(monitors):
            raise ValueError(f"Screen index {screen_index} is out of range. Only {len(monitors)} monitors detected")
        monitor = monitors[screen_index]
        region = [monitor.x, monitor.y, monitor.width, monitor.height]
        screenshot = pyautogui.screenshot(region = region)
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return frame