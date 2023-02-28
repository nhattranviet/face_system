import cv2
import os,stat,shutil
from face_from_imgs_app import create_face_img
from db_build import *
from config.config_app import *
from milvus import Milvus, MetricType
from demo_image import *
from gen import frame2base64
lst_Detect_Recog=[]
DATABASE_DIR="./static/database"
INPUT_DIR="./static/database/raw_images"
SAVE_DIR="./static/database/images"
CROP_PARA=None
ROI_PARA_LS=None
VIDEO_PATH=None
list_RF={
    "24 0A B2 24":"Binh53",
    "53 04 5E 1D":"Quoc Khanh",
    "0A BC 62 1A":"A Dan 52",
    "87 BF A8 4B":"Tri53"
}
# # Load face detection model
# face_model = load_face_detection_model.face_boxes_model()
# face_model.load_face_model()
# # Load facial landmark detection model
# landmark_model, out_size = load_facial_lanmark_model.load_model()
def registerUser():
    sub_dirs = os.listdir(INPUT_DIR)
    for sub_dir in sub_dirs:
        sub_dir_path = os.path.join(INPUT_DIR, sub_dir)
        if os.path.isdir(sub_dir_path):
            person_name = sub_dir
            create_face_img(face_model, landmark_model, out_size, sub_dir_path, SAVE_DIR, person_name)

def saveToDatabase():
    #init param
    root = './static/database/images'

    #task to save to database
    database_existed = False
    # check if databse existed
    if os.path.isfile(sql_db):
        database_existed = True
    # Connect database
    sql_conn = sqlite3.connect(sql_db)
    
    if not database_existed:
        create_sql_table(sql_conn, table_name)

    milvus_conn = Milvus(host=MILVUS_HOST, port=MILVUS_PORT)
    create_collection(milvus_conn, collection_name, cfg.embedding_size)

    sub_dirs = os.listdir(root)
    for person_name in sub_dirs:
        sub_dir_path = os.path.join(root, person_name)
        if os.path.isdir(sub_dir_path):
            if insert_images_person_to_db(extract_model, person_name, sub_dir_path, sql_conn, table_name, milvus_conn, collection_name):
                print("insert {0} succesfully".format(person_name))
            else:
                print("insert {0} failure".format(person_name))

    # Close database
    sql_conn.close()
    milvus_conn.close()

def saveToDatabase2():
    #init param
    root = './static/database/images'

    #task to save to database
    database_existed = False
    # check if databse existed
    if os.path.isfile(sql_db):
        database_existed = True
    # Connect database
    sql_conn = sqlite3.connect(sql_db)
    
    if not database_existed:
        create_sql_table(sql_conn, table_name)

    milvus_conn = Milvus(host=MILVUS_HOST, port=MILVUS_PORT)
    create_collection(milvus_conn, collection_name, cfg.embedding_size)

    sub_dirs = os.listdir(root)
    for person_name in sub_dirs:
        sub_dir_path = os.path.join(root, person_name)
        if os.path.isdir(sub_dir_path):
            if insert_images_person_to_db2(extract_model, person_name, sub_dir_path, sql_conn, table_name, milvus_conn, collection_name):
                print("insert {0} succesfully".format(person_name))
            else:
                print("insert {0} failure".format(person_name))

    # Close database
    sql_conn.close()
    milvus_conn.close()

def getFirstFrame(video_path):
    camera = cv2.VideoCapture(video_path)
    if not (camera.isOpened()):
        print('cannot open')
    success, frame = camera.read()  # read the camera frame
    print(frame)
    # if not success:
    #     return None
    # else:
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

def get_first_image_by_id(RFid):
    # conn = sqlite3.connect(sql_db)
    # cursor = conn.execute("select file_path from {0} where name='{1}' limit 1".format(table_name,name))
    # face_img_path=""
    # for row in cursor:
    #     face_img_path=row[0]
    # face_img = cv2.cvtColor(cv2.imread(face_img_path), cv2.COLOR_BGR2RGB)
    # conn.close()
    lst_RF={
        "24 0A B2 24":"static/image/Binh53.jpg",
        "53 04 5E 1D":"static/image/Quoc Khanh.jpg",
        "0A BC 62 1A":"static/image/Dan52.jpg",
        "87 BF A8 4B":"static/image/Tri53.jpg",
    }
    for id, path in lst_RF.items(): 
        if id == RFid:
            face_img = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB)
            return face_img
    return ""
def create_sql_table_RTSP(sql_conn, table_name):
    query = "CREATE TABLE '{0}' ( `id`INTEGER PRIMARY KEY AUTOINCREMENT,`RTSP_Name` TEXT NOT NULL, `crop_para` TEXT NOT NULL, `roi_para_ls` TEXT NOT NULL )".format(table_name)
    sql_conn.execute(query)
    sql_conn.commit()

def authorizeImageRFID(frame):
    sql_conn, milvus_conn = connect_database(sql_db, collection_name)
    res=image_process(frame,sql_conn,milvus_conn,collection_name,table_name)
    return res

def findRFIDbyName(name):
    for id, user in list_RF.items(): 
        if user == name:
            print("=>>>.....=>"+id)
            return id
    return 0

def findNameFromRFid(RFid):
    for id, user in list_RF.items(): 
        if RFid == id:
            return user
    return ""

def deleteFolderByName(foldName):
    try:
        shutil.rmtree(INPUT_DIR+'/'+foldName)
        shutil.rmtree(SAVE_DIR+'/'+foldName)
    except OSError as e:
        print("Error: %s" % ( e.strerror))

def deleteFolderAll():
    try:
        shutil.rmtree(DATABASE_DIR)
    except OSError as e:
        print("Error: %s" % ( e.strerror))

def getFaceRecog(ct):
    lst_Reg=[]
    faces_items = ct.faces.items()
    for (objectID, face) in faces_items:
        if ct.faces[objectID].is_processed:
            info_reg={}
            if ct.faces[objectID].face_name == 'guest':
                continue
            info_reg['name']=ct.faces[objectID].face_name
            info_reg['image_from_db']=frame2base64(ct.faces[objectID].img_from_db).decode('utf-8')
            info_reg['image_capture']=frame2base64(cv2.cvtColor(ct.faces[objectID].best_img, cv2.COLOR_BGR2RGB)).decode('utf-8')
            lst_Reg.append(info_reg)
    return lst_Reg