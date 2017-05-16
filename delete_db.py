"""
If needed, this can be used to delete the database.
"""
import pymysql
import dbconfig


def delete_feed_stories(connection):
    try:
        with connection.cursor() as cursor:
            sql = "DROP TABLE news.feed_stories"
            cursor.execute(sql)
            connection.commit()
    finally:
        connection.close()


if __name__ == '__main__':
    connection = pymysql.connect(host='localhost',
                                 user=dbconfig.db_user,
                                 passwd=dbconfig.db_password)
    delete_feed_stories(connection)
