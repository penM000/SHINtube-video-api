import sqlite3

dbname = "video.db"
dbengine = "sqlite"


def get_connection() -> sqlite3.Connection:
    if dbengine == "sqlite":
        conn = sqlite3.connect(dbname)
    return conn


def check_existence_table(table_name):
    conn = get_connection()
    cur = conn.cursor()
    if dbengine == "sqlite":
        sql = "SELECT name from sqlite_master where type= 'table'"
    elif dbengine == "mysql":
        sql = f"SHOW TABLES LIKE \'{table_name}\';"
    result = cur.execute(sql).fetchall()
    cur.close()
    conn.close()
    for name in result:
        if name[0] == table_name:
            return True
    return False


def create_table():
    # create_input_video_table()
    create_stream_video_table()


def create_input_video_table():
    if check_existence_table("input_video"):
        return
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        'CREATE TABLE input_video(  id INTEGER PRIMARY KEY AUTOINCREMENT,\
                                            video_name STRING,\
                                            file_name STRING,\
                                            class_code STRING)')
    conn.commit()
    conn.close()


def create_stream_video_table():
    if check_existence_table("stream_video"):
        return
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        'CREATE TABLE stream_video(  id INTEGER PRIMARY KEY AUTOINCREMENT,\
                                            video_name STRING,\
                                            class_code STRING,\
                                            input_video_file_name STRING,\
                                            stream_file_name STRING,\
                                            encode_status STRING,\
                                            resolution INT)')
    conn.commit()
    conn.close()


def add_stream_video(
        video_name,
        class_code,
        input_video_file_name,
        stream_file_name,
        encode_status,
        resolution):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "insert into stream_video values (?,?,?,?,?,?)",
        (
            video_name,
            class_code,
            input_video_file_name,
            stream_file_name,
            encode_status,
            resolution
        )
    )
    conn.commit()
    conn.close()


def update_status_stream_video(status):
    conn = get_connection()
    cur = conn.cursor()

    # personsというtableを作成してみる
    # 大文字部はSQL文。小文字でも問題ない。
    cur.execute('CREATE TABLE persons(id INTEGER PRIMARY KEY AUTOINCREMENT,\
                                      name STRING)')

    # データベースへコミット。これで変更が反映される。
    conn.commit()
    conn.close()


def delete_video_status():
    dbname = 'TEST.db'
    conn = sqlite3.connect(dbname)
    # sqliteを操作するカーソルオブジェクトを作成
    cur = conn.cursor()

    # personsというtableを作成してみる
    # 大文字部はSQL文。小文字でも問題ない。
    cur.execute('CREATE TABLE persons(id INTEGER PRIMARY KEY AUTOINCREMENT,\
                                      name STRING)')

    # データベースへコミット。これで変更が反映される。
    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_table()
