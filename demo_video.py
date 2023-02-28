import cv2
import argparse
import imutils
from torch.backends import cudnn
from utils_face_detection.faceboxes import load_model as load_face_detection_model
from utils_face_detection.utils import check_legal_face
from utils_facial_landmark_detection import load_model as load_facial_lanmark_model
from utils_face_feature_extraction.arcface import load_model
from utils_face_tracking.center_track.tracking import CentroidTracker
from milvus import Milvus
import sqlite3
from config.config import *
from helper_func import *
from utils import *
# Set environment
if CUDNN:
    cudnn.benchmark = True
torch.set_grad_enabled(False)

# Load face detection model
face_model = load_face_detection_model.face_boxes_model()
face_model.load_face_model()
# Load facial landmark detection model
landmark_model, out_size = load_facial_lanmark_model.load_model()
# Load face feature extraction model
cfg = get_config()
extract_model = load_model.face_learner(cfg)
extract_model.load_state()


def connect_database(sql_db=None, collection_name=None):
    milvus_conn = None
    sql_conn = None
    try:
        # Connect face vector database
        milvus_conn = Milvus(host=MILVUS_HOST, port=MILVUS_PORT)
        # connect to sql face db manager
        sql_conn = sqlite3.connect(sql_db)
    except Exception as e:
        close_connection(sql_conn, milvus_conn)
        print("[WARNING]: Connection error")
        return None, None
    status, search_face = milvus_conn.has_collection(collection_name)
    if not search_face:
        close_connection(sql_conn, milvus_conn)
        print("[WARNING]: Collection", collection_name, "is not existed")
        return None, None
    return sql_conn, milvus_conn


def close_connection(sql_conn, milvus_conn):
    sql_conn.close()
    milvus_conn.close()


def video_process(video_path, sql_conn, milvus_conn, collection_name=None, table_name=None, draw_id=True):
    # _INIT_ camera consts
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    ori_frame = frame
    crop_para, roi_para_ls = load_camera_parameter(str(video_path), frame)
    frame, cut_top, cut_bottom, cut_left, cut_right, roi_para = crop_roi(
        frame, crop_para, roi_para_ls)
    height, width = frame.shape[:2]

    # _INIT_ motion detection consts
    previous_frame = None
    delay_counter = FRAMES_TO_PERSIST
    movement_persistent_counter = 0

    # _INIT_ tracking consts
    ct = CentroidTracker(landmark_model, extract_model, out_size)
    ct.width = width
    ct.height = height
    ct.roi_para = roi_para

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = frame[cut_top:cut_bottom, cut_left:cut_right]
        ct.frame = frame
        frame_rs = imutils.resize(frame, height=IMG_HEIGHT)
        # is_motion, previous_frame, delay_counter, movement_persistent_counter = motion_detect(frame.copy(), previous_frame, delay_counter, movement_persistent_counter)
        # if is_motion:
        faces = faceboxes_detect(frame_rs, face_model)
        rects = []
        for _, face in enumerate(faces):
            if face[4] < FD_THRESH:  # remove low confidence detection
                continue
            # resize to original bouding box
            face = resize_bbox(frame, frame_rs, face)
            if not check_legal_face(face, roi_para):
                continue
            rects.append(face)
        # update tracking
        objects = ct.update(rects)
        # search name of face object in the database
        search(ct, milvus_conn, sql_conn, collection_name, table_name)
        # face_objs = ct.faces.items()
        # for (objectID, face_obj) in face_objs:
        draw_process_roi(frame, process_roi=roi_para_ls)
        cvDrawBoxes(rects, frame)
        visualize_result(frame, ct, objects, draw_id=draw_id)
        cv2.imshow("ok", frame)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--video_path', default=0, help='video path')
    parser.add_argument(
        '--sql_db', default="./static/database/face_db_manager.db", help='sql databse path')
    parser.add_argument('--table_name', default='person',
                        help='table name in sql databse')
    parser.add_argument('--collection_name', default='face_db',
                        help='collection name (table name) in vectors database (milvus)')
    args = parser.parse_args()
    # Connect database
    sql_conn, milvus_conn = connect_database(args.sql_db, args.collection_name)
    if sql_conn is not None:
        video_process(args.video_path, sql_conn, milvus_conn, args.collection_name, args.table_name, draw_id=False)
    # Close database
    close_connection(sql_conn, milvus_conn)
