from config.config import MIN_HEIGHT, MIN_WIDTH
from shapely.geometry import Point

def is_detections_in_roi(detection, roi_para):
    if roi_para is None:
        return True
    x, y, a, b = detection
    x, y = (x + a)//2, (y + b)//2
    return roi_para.contains(Point(x,y))

def check_legal_face(face, roi_para):
    x1,y1,x2,y2 = face
    if y2-y1 < MIN_HEIGHT or x2-x1 < MIN_WIDTH:
        return False
    return is_detections_in_roi(face, roi_para)