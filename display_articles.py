"""
Just a simple test to make sure that this is working. Later on this might take a different role.
Perhaps even be renamed
"""
import dbconfig
import pandas as pd
import pymysql


def get_data():
    try:
        connection = pymysql.connect(host='localhost',
                                     user=dbconfig.db_user,
                                     passwd=dbconfig.db_password,
                                     db='news')
        articles = pd.read_sql_query('SELECT * FROM feed_stories', connection)
        print(articles.head())
    finally:
        connection.close()


if __name__ == '__main__':
    get_data()
