import torch
from easydict import EasyDict as edict
import numpy as np
from pathlib import Path
from torchvision import transforms as trans

# DEVICE SETTING
CUDNN = False
DEVICE_IDX = 0  # -1 for cpu


# FACE DETECTION PARAMETERS
# FaceBoxes
IMG_HEIGHT = 800
IMG_HEIGHT_TRT = 1024
FD_THRESH = 0.85
FB_WEIGHTS = "weights/face_detection/faceboxes/FaceBoxes.pth"
FB_WEIGHTS_TRT = "weights/face_detection/faceboxes/FaceBoxes_trt.pth"
MIN_HEIGHT = 30
MIN_WIDTH = 30
confidence_threshold = 0.05
nms_threshold = 0.3
cpu = False
DEVICE = 'cuda:0'
top_k = 1000
keep_top_k = 200

# FACIAL LANDMARK PARAMETERS
LandmarkBackbone = 'MobileFaceNet'
CR_WEIGHTS = "weights/facial_landmark_detection/mobilefacenet_model_best.pth.tar"
CR_WEIGHTS_TRT = "weights/facial_landmark_detection/mobilefacenet_model_best_trt.pth"

# LandmarkBackbone = 'MobileNet'
# CR_WEIGHTS = "weights/facial_landmark_detection/mobilenet_224_model_best_gdconv_external.pth.tar"

# LandmarkBackbone = 'PFLD'
# CR_WEIGHTS = "weights/facial_landmark_detection/pfld_model_best.pth.tar"
MobileNetMean = np.asarray([0.485, 0.456, 0.406])
MobileNetStd = np.asarray([0.229, 0.224, 0.225])
CROP_SIZE = 112
SCALE = CROP_SIZE / 112.

# FACE FEATURE EXTRACTION


def get_config():
    conf = edict()
    # conf.model_path = "weights/face_feature_extraction/model_mobilefacenet.pth"
    conf.model_path = "weights/face_feature_extraction/model_ir_se50.pth"
    conf.model_path_trt = "weights/face_feature_extraction/model_ir_se50_trt.pth"
    conf.input_size = [112, 112]
    conf.embedding_size = 512
    # conf.use_mobilfacenet = True
    conf.use_mobilfacenet = False
    conf.net_depth = 50
    conf.drop_ratio = 0.6
    conf.net_mode = 'ir_se'  # or 'ir'
    if torch.cuda.is_available() and DEVICE_IDX != -1:
        conf.device = "cuda:{0}".format(str(DEVICE_IDX))
    else:
        conf.device = "cpu"
    conf.test_transform = trans.Compose([
        trans.ToTensor(),
        trans.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
    ])
    conf.threshold = 1.5
    return conf


# FACE MATCHING PARAMETERS
MAX_SAVE_FACES = 20
MIN_SIM_TO_SAVE = 0.3
MILVUS_HOST = "127.0.0.1"
# MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"
TOP_K = 10
MAX_SIM_DISTANCE = 0.9
MIN_PERCENT = 0.3

# PUT TEXT OPTION
TEXT_SIZE = 1.
THICK_NESS = 2

# -- Tracking parameters --
MAX_DISSAPPEARED = 5
MAX_TRIAL_TIMES = 100
SKIP_FRAME = 4
IOU_NMS = 0.85
MIN_DISTANCE_RATIO = 2
MAX_KEEP_TIME = 20

# -----Motion detection parameters----
FRAMES_TO_PERSIST = 10
MIN_DIFF_FOR_MOVEMENT = 1
MOVEMENT_DETECTED_PERSISTENCE = 11

# -----ROI of cam parameters---
CAM_PARAM = {
    "0": [[
        [
          11.754098360655737,
          9.770491803278688
          ],
        [
            1269.1311475409836,
            712.2295081967213
        ]
    ], [
        [
            111.75409836065575,
            101.57377049180329
        ],
        [
            1168.311475409836,
            106.49180327868852
        ],
        [
            1170.7704918032787,
            608.1311475409836
        ],
        [
            104.37704918032787,
            608.1311475409836
        ]
    ]],
    "rtsp://admin:Admin@123@192.168.10.64:554/Streaming/Channels/101/":
    # "rtsp://admin:Admin@123@117.4.240.104:8084/Streaming/Channels/101/":
    [
        [
            [
                25.688524590163937,
                47.47540983606557
            ],
            [
                1232.2459016393443,
                704.032786885246
            ]
        ], [
            [
                88.80327868852459,
                71.24590163934427
            ],
            [
                1197.0,
                67.14754098360656
            ],
            [
                1157.655737704918,
                367.9672131147541
            ],
            [
                862.5737704918033,
                653.2131147540983
            ],
            [
                82.24590163934427,
                641.7377049180328
            ]
        ]
    ],
    "rtsp://camera:123qweQWE@113.176.61.64:554": [
        [
            [
                95.08510638297872,
                142.5531914893617
            ],
            [
                2499.3404255319147,
                1846.8085106382978
            ]
        ], [
            [
                322.7446808510638,
                208.51063829787233
            ],
            [
                2444.0212765957444,
                493.6170212765957
            ],
            [
                2401.4680851063827,
                1170.2127659574467
            ],
            [
                282.3191489361702,
                576.595744680851
            ]
        ]
    ],
    "./test.avi": [
        [
            [
                4.46448087431694,
                4.66120218579235
            ],
            [
                844.3551912568306,
                470.23497267759564
            ]
        ], [
            [
                73.86338797814207,
                50.56284153005464
            ],
            [
                750.3661202185792,
                54.3879781420765
            ],
            [
                749.2732240437158,
                417.775956284153
            ],
            [
                65.12021857923497,
                424.3333333333333
            ]
        ]
    ]
}
