import pymysql
from pymysql.cursors import DictCursor

dbh = pymysql.connect(
    host='185.12.94.106',
    user='2p1s04',
    password='251-480-822',
    db='2p1s04',
    charset='utf8mb4',
    cursorclass=DictCursor,
    autocommit=True
)

def db_request(sql):
    try:
        with dbh.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            out_data = {
                'status': 'ok', 
                'data': rows
            }
    except Exception as e:
        out_data = {
            'status': 'error',
            'data': str(e)
        }

    return out_data