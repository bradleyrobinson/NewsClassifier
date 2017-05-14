"""
If needed, this can be used to delete the database.
"""
import pymysql
import dbconfig
connection = pymysql.connect(host='localhost',
                             user=dbconfig.db_user,
                             passwd=dbconfig.db_password)


try:
    with connection.cursor() as cursor:
        sql = "DROP TABLE news.feed_stories"
        cursor.execute(sql)
        connection.commit()
finally:
    connection.close()
