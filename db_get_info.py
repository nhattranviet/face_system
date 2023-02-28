import sqlite3

def get_info(sql_db, table_name):
    conn = sqlite3.connect(sql_db)
    infos = []
    cursor = conn.execute("select name, id, file_path from {0}".format(table_name))
    for row in cursor:
        # name, id, file_path
        infos.append([row[0], row[1], row[2]])
    conn.close()
    return infos

if __name__=="__main__":
    # sql database path --> which use for manager id, person, file_path
    sql_db = "./static/database/face_db_manager.db"
    # sql table name in database
    table_name = "person"
    # infos fields: name, id, file_path
    infos  = get_info(sql_db, table_name)
    for info in infos:
        print(info)