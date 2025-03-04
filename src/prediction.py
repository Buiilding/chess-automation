from ultralytics import YOLO
class Predictor:
    def predict(self, frame):
        results = self.model(frame ,conf = 0.7, verbose = False)
        return results
    def predict_board(self, frame):
        results = self.board_model(frame, conf = 0.7, verbose = False)
        return results
    def load_model(self,filepath):
        model = YOLO(filepath)
        model.fuse()
        return model