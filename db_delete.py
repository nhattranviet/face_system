import sqlite3
from config.config import MILVUS_HOST, MILVUS_PORT
from milvus import Milvus
import sys

def delete_in_milvus(collection_name, ids):
    milvus = Milvus(host=MILVUS_HOST, port=MILVUS_PORT)
    status, ok = milvus.has_collection(collection_name)
    if not ok:
        print("No collection with name", collection_name)
        return False
    milvus.delete_entity_by_id(collection_name=collection_name, id_array = ids)
    milvus.flush(collection_name_array=[collection_name])
    milvus.close()
    return True

## delete person in sql lite database by file_path or ids or person_name ---> ids for delete at milvus
def delete_by_file_paths(sql_db, table_name, collection_name, file_paths):
    success = False
    conn = sqlite3.connect(sql_db)
    ids = []
    for file_path in file_paths:
        cursor = conn.execute("select id from {0} where file_path='{1}'".format(table_name, file_path))
        for row in cursor:
            ids.append(row[0])
        query = "delete from {0} where file_path='{1}'".format(table_name, file_path)
        conn.execute(query)
        
    if delete_in_milvus(collection_name, ids):
        conn.commit()
        success = True
    conn.close()
    return success

## delete by person name
def delete_by_person_name(sql_db, table_name, collection_name, person_name):
    success = False
    conn = sqlite3.connect(sql_db)
    ids = []
    cursor = conn.execute("select id from {0} where name='{1}'".format(table_name, person_name))
    for row in cursor:
        ids.append(row[0])
    query = "delete from {0} where name='{1}'".format(table_name, person_name)
    conn.execute(query)
    if delete_in_milvus(collection_name, ids):
        conn.commit()
        success = True
    conn.close()
    return success

## delete by person ids
def delete_by_ids(sql_db, table_name, collection_name, ids):
    success = False
    conn = sqlite3.connect(sql_db)
    for id in ids:
        query = "delete from {0} where id={1}".format(table_name, id)
    conn.execute(query)
    if delete_in_milvus(collection_name, ids):
        conn.commit()
        success = True
    conn.close()
    return success

## delete all record
def clear_all(sql_db, table_name, collection_name):
    success = False
    conn = sqlite3.connect(sql_db)
    query = "delete from {0}".format(table_name)
    conn.execute(query)
    milvus = Milvus(host=MILVUS_HOST, port=MILVUS_PORT)
    milvus.drop_collection(collection_name)
    status, ok = milvus.has_collection(collection_name)
    if not ok:
        conn.commit()
        success = True
    conn.close()
    milvus.close()
    return success


if __name__=="__main__":
    person_name = sys.argv[1]
    # sql database path --> which use for manager id, person, file_path
    sql_db = "./static/database/face_db_manager.db"
    # sql table name in database
    table_name = "person"
    ## table name in vectors database
    collection_name = 'face_db'
    # status = delete_by_person_name(sql_db, table_name, collection_name , person_name)
    status  = clear_all(sql_db, table_name, collection_name)
    if status:
        print("delete success")
    else:
        print("delete failure")