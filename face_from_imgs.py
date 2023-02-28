import argparse
import os
import glob
import cv2
import imutils
from utils_face_detection.utils import check_legal_face
from utils_facial_landmark_detection import load_model as load_facial_lanmark_model
from utils_face_detection.faceboxes import load_model as load_face_detection_model
from config.config import IMG_HEIGHT, FD_THRESH
from utils import *

# Load face detection model
face_model = load_face_detection_model.face_boxes_model()
face_model.load_face_model()
# Load facial landmark detection model
landmark_model, out_size = load_facial_lanmark_model.load_model()


def create_face_img(face_model, landmark_model, out_size, sub_dir_path, save_dir, person_name):
    save_path = os.path.join(save_dir, person_name)
    if os.path.exists(save_path):
        print("Person", person_name, "existed --> Skipped")
        return
    os.mkdir(save_path)
    img_paths = glob.glob(os.path.join(sub_dir_path, "*.jpg"))
    for index, img_path in enumerate(img_paths):
        frame = cv2.imread(img_path)
        frame_rs = imutils.resize(frame, height=IMG_HEIGHT)
        faces = faceboxes_detect(frame_rs, face_model)
        rects = []
        for _, face in enumerate(faces):
            if face[4] < FD_THRESH:  # remove low confidence detection
                continue
            # resize to original bouding box
            face = resize_bbox(frame, frame_rs, face)
            if not check_legal_face(face, None):
                continue
            rects.append(face)
        if len(rects) == 0:
            print("No face detected at", img_path)
            continue
        cropped, new_bbox = crop_face(frame, rects[0])
        warped_face = aligned_face_img(
            frame, cropped, new_bbox, landmark_model, out_size)
        save_img_path = os.path.join(save_path, str(index) + ".jpg")
        cv2.imwrite(save_img_path, warped_face)
        print("Saved img", save_img_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', default='./static/database/raw_images')
    parser.add_argument('--save_dir', default='./static/database/images')
    args = parser.parse_args()
    input_dir = args.input_dir
    save_dir = args.save_dir
    sub_dirs = os.listdir(input_dir)
    for sub_dir in sub_dirs:
        sub_dir_path = os.path.join(input_dir, sub_dir)
        if os.path.isdir(sub_dir_path):
            person_name = sub_dir
            create_face_img(face_model, landmark_model, out_size, sub_dir_path, save_dir, person_name)
