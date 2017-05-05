import pymysql
import dbconfig
connection = pymysql.connect(host='localhost',
                             user=dbconfig.db_user,
                             passwd=dbconfig.db_password)


try:
    with connection.cursor() as cursor:
        sql = "CREATE DATABASE IF NOT EXISTS news"
        cursor.execute(sql)
        sql = """CREATE TABLE IF NOT EXISTS news.feed_stories (
        id int NOT NULL AUTO_INCREMENT,
        title VARCHAR(150),
        description VARCHAR(1000),
        date DATETIME,
        bias VARCHAR(20),
        PRIMARY KEY (id) """
        cursor.execute(sql)
        connection.commit()
finally:
    connection.close()