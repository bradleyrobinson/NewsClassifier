"""
Code to clean out duplicate stories in the database
"""
import collect_feeds
import delete_db
import setup_db
import pandas as pd


def main():
    """
    Used to clean feeds
    """
    dbhelper = collect_feeds.DBHelper()
    old_df = dbhelper.get_old_df() # Keep the data
    old_df = old_df.drop_duplicates()
    delete_db.delete_feed_stories(dbhelper.get_connection())
    dbhelper.open_connection()
    setup_db.setup_db(dbhelper.get_connection())
    dbhelper.open_connection()
    dbhelper.update_sql(old_df.to_dict('list'))
    dbhelper.close_connection()


if __name__ == "__main__":
    main()