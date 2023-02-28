import cv2
from shapely.geometry.polygon import Polygon
from config.config import *

def visualize_result(frame, ct, objects, cut_top=0, cut_left=0, draw_id=False, thickness=2):
    for (objectID, centroid) in objects.items():
        # draw both the ID of the object and the centroid of the
        # object on the output frame
        color = (0, 0, 255)
        if ct.faces[objectID].is_processed is True:
            color = (255, 255, 255)
        text = ""
        if draw_id:
            text = "{0}-".format(objectID)
        # cv2.imshow(ct.faces[objectID].lp_text, ct.faces[objectID].best_img)
        cv2.putText(frame, text + ct.faces[objectID].face_name, (centroid[0] + cut_left-10, centroid[1] + cut_top),
                    cv2.FONT_HERSHEY_SIMPLEX, TEXT_SIZE, color, thickness)
        cv2.circle(frame, (centroid[0] + cut_left, centroid[1] + cut_top), 4, color, -1)

def draw_process_roi(frame, process_roi, cut_top=0, cut_left=0, thickness=2):
    for i in range(len(process_roi)-1):
        cv2.line(frame, (process_roi[i][0] + cut_left, process_roi[i][1] + cut_top),
                 (process_roi[i+1][0] + cut_left, process_roi[i+1][1] + cut_top), (0, 255, 0), thickness)
    max_index = len(process_roi) - 1
    cv2.line(frame, (process_roi[max_index][0] + cut_left, process_roi[max_index][1] + cut_top),
             (process_roi[0][0] + cut_left, process_roi[0][1] + cut_top), (0, 255, 0), thickness)

def crop_roi(frame, crop_para, roi_para):
    height, width = frame.shape[:2]
    xt, yt = crop_para[0]
    xbt, ybt = crop_para[1]

    cut_top = int(yt)
    cut_bottom = int(ybt)
    cut_left = int(xt)
    cut_right = int(xbt)

    for index, _ in enumerate(roi_para):
        roi_para[index][0] = int(roi_para[index][0] - cut_left)
        roi_para[index][1] = int(roi_para[index][1] - cut_top)

    frame = frame[cut_top:cut_bottom, cut_left:cut_right]
    return frame, cut_top, cut_bottom, cut_left, cut_right, Polygon(roi_para)

def load_camera_parameter(camera_rtsp, frame):
    # load camera parameters
    if camera_rtsp in CAM_PARAM.keys():
        crop_para, roi_para = CAM_PARAM[camera_rtsp]
    else:
        print("No ROI")
        h,w = frame.shape[:2]
        crop_para = [[0,0], [w, h]]
        roi_para = [[0,0], [w,0], [w, h], [0, h]]

    return crop_para, roi_para

def cvDrawBoxes(detections, img, cut_top=0, cut_left=0, debug=False, thickness=4):
    confs = []
    for detection in detections:
        x1, y1, x2, y2 = detection
        x1 = x1 + cut_left
        x2 = x2 + cut_left
        y1 = y1 + cut_top
        y2 = y2 + cut_top
        cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), thickness)