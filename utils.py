from pickle import TRUE
from torch import le
from config.config import *
import numpy as np
import cv2
import os
import operator
from utils_facial_landmark_detection.common.utils import BBox
from utils_facial_landmark_detection.utils.align_trans import get_reference_facial_points, warp_and_crop_face
from utils_facial_landmark_detection.common.utils import drawLandmark_multiple
reference = get_reference_facial_points(default_square=True) * SCALE

def aligned_face_img(frame, cropped, new_bbox, landmark_model, out_size):
    cropped_face = cv2.resize(cropped, (out_size, out_size))
    new_bbox, landmark = landmark_detect(
        cropped_face, landmark_model, new_bbox)
    facial5points = get_facial_five_points(landmark)
    warped_face = warp_and_crop_face(
        frame, facial5points, reference, crop_size=(CROP_SIZE, CROP_SIZE))
    return warped_face

def feature_extraction(frame, cropped, new_bbox, landmark_model, extract_model, out_size):
    warped_face = aligned_face_img(frame, cropped, new_bbox, landmark_model, out_size)
    face_feature = extract_model.extract_feature([warped_face])
    face_feature = face_feature.detach().to('cpu').numpy()
    # print(face_feature.shape)
    # drawLandmark_multiple(frame, new_bbox, landmark)
    # cv2.imshow("w_f", warped_face)
    return warped_face, face_feature


def faceboxes_detect(image, face_model):
    bboxs = face_model.detect_faces(np.float32(image.copy()))
    if bboxs is None:
        bboxs = []
    return bboxs


def resize_bbox(origin_img, image_rs, face=None):
    rs_h, rs_w = image_rs.shape[:2]
    ori_h, ori_w = origin_img.shape[:2]
    x1 = face[0]*ori_w/rs_w
    y1 = face[1]*ori_h/rs_h
    x2 = face[2]*ori_w/rs_w
    y2 = face[3]*ori_h/rs_h
    w = x2 - x1 + 1
    h = y2 - y1 + 1
    size = int(min([w, h])*1.2)
    cx = x1 + w//2
    cy = y1 + h//2
    x1 = cx - size//2
    x2 = x1 + size
    y1 = cy - size//2
    y2 = y1 + size

    # dx = max(0, -x1)
    # dy = max(0, -y1)
    x1 = max(0, x1)
    y1 = max(0, y1)

    # edx = max(0, x2 - ori_w)
    # edy = max(0, y2 - ori_h)
    x2 = min(ori_w, x2)
    y2 = min(ori_h, y2)
    new_bbox = list(map(int, [x1, y1, x2, y2]))
    return new_bbox


def crop_face(origin_img, new_bbox):
    new_bbox = BBox(new_bbox)
    cropped = origin_img[new_bbox.y1:new_bbox.y2,
                         new_bbox.x1:new_bbox.x2]
    # if (new_bbox.dx > 0 or new_bbox.dy > 0 or new_bbox.edx > 0 or new_bbox.edy > 0):
    #     cropped = cv2.copyMakeBorder(cropped, int(new_bbox.dy), int(
    #         new_bbox.edy), int(new_bbox.dx), int(new_bbox.edx), cv2.BORDER_CONSTANT, 0)
    return cropped, new_bbox


def landmark_detect(cropped_face, model, new_bbox):
    test_face = cropped_face.copy()
    test_face = test_face/255.0
    if LandmarkBackbone == 'MobileNet':
        test_face = (test_face-MobileNetMean)/MobileNetStd
    test_face = test_face.transpose((2, 0, 1))
    test_face = test_face.reshape((1,) + test_face.shape)
    input = torch.from_numpy(test_face).float()
    # input = torch.autograd.Variable(input)
    if torch.cuda.is_available() and DEVICE_IDX != -1:
        input = input.to(device='cuda:{0}'.format(DEVICE_IDX))
    if LandmarkBackbone == 'MobileFaceNet':
        landmark = model(input)[0].detach().cpu().data.numpy()
    else:
        landmark = model(input).detach().cpu().data.numpy()
    landmark = landmark.reshape(-1, 2)
    landmark = new_bbox.reprojectLandmark(landmark)
    return new_bbox, landmark


def get_facial_five_points(landmark):
    # crop and aligned the face
    lefteye_x = 0
    lefteye_y = 0
    for i in range(36, 42):
        lefteye_x += landmark[i][0]
        lefteye_y += landmark[i][1]
    lefteye_x = lefteye_x/6
    lefteye_y = lefteye_y/6
    lefteye = [lefteye_x, lefteye_y]

    righteye_x = 0
    righteye_y = 0
    for i in range(42, 48):
        righteye_x += landmark[i][0]
        righteye_y += landmark[i][1]
    righteye_x = righteye_x/6
    righteye_y = righteye_y/6
    righteye = [righteye_x, righteye_y]

    nose = landmark[33]
    leftmouth = landmark[48]
    rightmouth = landmark[54]
    facial5points = [righteye, lefteye, nose, rightmouth, leftmouth]
    return facial5points


def motion_detect(frame, previous_frame, delay_counter, movement_persistent_counter):
    frame = cv2.resize(frame, (250, 250))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (11, 11), 0)
    delay_counter += 1
    curr_frame = gray
    if delay_counter > FRAMES_TO_PERSIST:
        delay_counter = 0
        previous_frame = curr_frame
    frame_delta = cv2.absdiff(previous_frame, curr_frame)
    diff_value = np.mean(frame_delta)
    if diff_value > MIN_DIFF_FOR_MOVEMENT:
        # movement_persistent_flag = True
        movement_persistent_counter = MOVEMENT_DETECTED_PERSISTENCE

    if movement_persistent_counter > 0:
        movement_persistent_counter -= 1
        return True, previous_frame, delay_counter, movement_persistent_counter
    return False, previous_frame, delay_counter, movement_persistent_counter

def find_most_name(names):
    name_dict = {}
    for name in names:
        if name not in name_dict.keys():
            name_dict[name] = 0
        name_dict[name] += 1
    # print(name_dict)
    marklist= sorted(name_dict.items(), key=operator.itemgetter(1), reverse=True)
    sortdict=dict(marklist)
    percent = list(sortdict.values())[0]/len(names)
    if percent < MIN_PERCENT:
        return "guest"
    return list(sortdict.keys())[0]

def search_one_face(face_feature, milvus, conn, collection_name, table_name):
    param = {
            'collection_name': collection_name,
            'query_records': face_feature,
            'top_k': TOP_K,
            'params': {},
        }
    status, results = milvus.search(**param)
    if status.OK():
        names = []
        file_paths = []
        file_path = ""
        for result in results[0]:
            if result.distance >= MAX_SIM_DISTANCE:
                continue
            cursor = conn.execute("SELECT name, file_path from {0} where id={1}".format(table_name, result.id))
            for record in cursor:
                names.append(record[0])
                file_paths.append(record[1])
        if len(names) == 0:
            return False, None, None
        person_name = find_most_name(names)
        for index, name in enumerate(names):
            if name == person_name:
                file_path = file_paths[index]
                break
        return True, person_name, file_path
    else:
        print("Search failed")
        return False, None, None

def search(ct, milvus, conn, collection_name, table_name):
    faces_items = ct.faces.items()
    for (objectID, face) in faces_items:
        if face.is_processed == True:
            if face.keep_times <= MAX_KEEP_TIME:
                face.keep_times += 1
            else:
                face.is_processed = False
                face.keep_times = 0
            continue
        param = {
            'collection_name': collection_name,
            'query_records': face.feature,
            'top_k': TOP_K,
            'params': {},
        }
        status, results = milvus.search(**param)
        if status.OK():
            ct.faces[objectID].is_processed = True
            names = []
            for result in results[0]:
                if result.distance >= MAX_SIM_DISTANCE:
                    continue
                cursor = conn.execute("SELECT name from {0} where id={1}".format(table_name, result.id))
                for record in cursor:
                    names.append(record[0])
            if len(names) == 0:
                ct.faces[objectID].face_name = "guest"
                continue
            ct.faces[objectID].face_name = find_most_name(names)
        else:
            print("Search failed")


def save_face(best_img, save_dir="./static/database/images", save_times=1):
    if save_times > MAX_SAVE_FACES:
        return
    cv2.imwrite(os.path.join(save_dir, str(save_times) + ".jpg"), best_img)
