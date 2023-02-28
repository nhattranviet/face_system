class Face:
    def __init__(self):
        self.is_processed = False
        self.face_name = "guest"
        self.bbox = None
        self.best_img = None
        self.feature = None
        self.keep_times = 0
        self.save_times = 1
        self.change = False
        self.img_from_db = None