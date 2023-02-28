import os
import glob
import cv2
import numpy as np
from milvus import Milvus, MetricType
import sqlite3
import argparse
from utils_face_feature_extraction.arcface import load_model
from config.config import *
# root/
# ----kelly/
# -----------img1.jpg
# -----------img2.jpg
# ----jonh/
# -----------img1.jpg
# -----------img2.jpg

def get_person_name(sql_conn, db_manager_name):
    cursor = sql_conn.execute("select name from {0}".format(db_manager_name))
    names = set()
    for row in cursor:
        names.add(row[0])
    return list(names)


def create_collection(milvus_conn, collection_name, vector_dimension):
    status, ok = milvus_conn.has_collection(collection_name)
    if not ok:
        param = {'collection_name': collection_name, 'dimension': vector_dimension,
                 'index_file_size': 1024, 'metric_type': MetricType.L2}
        milvus_conn.create_collection(param)
    else:
        print("Collection existed")

## insert person and feature from image directory to db
def insert_images_person_to_db(extract_model, person_name, sub_dir_path, sql_conn, table_name, milvus_conn, collection_name):
    stored_names = get_person_name(sql_conn, table_name)
    if person_name in stored_names:
        print("Person", person_name, "existed --> skip")
        return False
    face_features = []
    names = []
    face_img_paths = glob.glob(os.path.join(sub_dir_path, "*.jpg"))
    for face_img_path in face_img_paths:
        face_img = cv2.imread(face_img_path)
        face_feature = extract_model.extract_feature([face_img])
        face_feature = face_feature.detach().to('cpu').numpy()[0]
        face_features.append(face_feature)
        names.append(person_name)

    status, ids = milvus_conn.insert(collection_name, np.array(face_features))
    if status.code == 0:
        for name, id, face_img_path in zip(names, ids, face_img_paths):
            sql_conn.execute("insert into {0} (name, id, file_path) values ('{1}', {2}, '{3}')".format(
                table_name, name, id, face_img_path))
            sql_conn.commit()
        return True
    milvus_conn.flush([collection_name])
    return False

## insert person and feature from image directory to db
def insert_images_person_to_db2(extract_model, person_name, sub_dir_path, sql_conn, table_name, milvus_conn, collection_name):
    
    # stored_names = get_person_name(sql_conn, table_name)
    # if person_name in stored_names:
    #     print("Person", person_name, "existed --> skip")
    #     return False
    face_features = []
    names = []
    face_img_paths = glob.glob(os.path.join(sub_dir_path, "*.jpg"))
    for face_img_path in face_img_paths:
        face_img = cv2.imread(face_img_path)
        face_feature = extract_model.extract_feature([face_img])
        face_feature = face_feature.detach().to('cpu').numpy()[0]
        face_features.append(face_feature)
        names.append(person_name)

    status, ids = milvus_conn.insert(collection_name, np.array(face_features))
    if status.code == 0:
        for name, id, face_img_path in zip(names, ids, face_img_paths):
            sql_conn.execute("insert into {0} (name, id, file_path) values ('{1}', {2}, '{3}')".format(
                table_name, name, id, face_img_path))
            sql_conn.commit()
        return True
    milvus_conn.flush([collection_name])
    return False


def create_sql_table(sql_conn, table_name):
    query = "CREATE TABLE '{0}' ( `name` TEXT NOT NULL, `id` INTEGER NOT NULL, `file_path` TEXT NOT NULL, PRIMARY KEY(`id`) )".format(table_name)
    sql_conn.execute(query)
    sql_conn.commit()

# load model
cfg = get_config()
extract_model = load_model.face_learner(cfg)
extract_model.load_state()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='./static/database/images')
    parser.add_argument('--sql_db', default='./static/database/face_db_manager.db', help='database name of sqlite')
    parser.add_argument('--table_name', default='person', help='table name in sqlite')
    parser.add_argument('--collection_name', default='face_db',
                        help='collection name (table name) in vectors database (milvus)')
    args = parser.parse_args()
    root = args.root
    table_name = args.table_name
    collection_name = args.collection_name

    database_existed = False
    # check if databse existed
    if os.path.isfile(args.sql_db):
        database_existed = True
    # Connect database
    sql_conn = sqlite3.connect(args.sql_db)
    
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