from bs4 import BeautifulSoup
import dbconfig
import feedparser
import pymysql
import pandas as pd
import re

biased_feeds = {
    'conservative': {
        "gatewaypundit": "http://www.thegatewaypundit.com/feed/",
        "dailycaller": "http://feeds.feedburner.com/dailycaller?format=xml",
        'westernjournalism': "http://www.westernjournalism.com/feed/",
        'breitbart': "http://feeds.feedburner.com/breitbart?format=xml",
        'wnd': "http://www.wnd.com/feed/",
        'ijr': "http://ijr.com/feed/",
        'nr1': "http://www.nationalreview.com/author/1211296/feed",
        'nr2': "http://www.nationalreview.com/author/900001/feed",
        'nr3': "http://www.nationalreview.com/author/903009/feed",
        'nr4': "http://www.nationalreview.com/author/1048/feed",
        'nr5': "http://www.nationalreview.com/author/901117/feed",
        'washingtontimes': "http://www.washingtontimes.com/rss/headlines/news/politics/",
        'th': "https://townhall.com/api/openaccess/columnists/anncoulter/",
        'th2': "https://townhall.com/api/openaccess/news/politics-elections/"
    },
    'liberal': {
        'dk1': "http://www.dailykos.com/user/Hunter/rss.xml",
        'dk2': "http://www.dailykos.com/user/Doctor%20RJ/rss.xml",
        'dk3': "http://www.dailykos.com/user/Jeff%20Singer/rss.xml",
        'cal': "http://feeds.crooksandliars.com/crooksandliars/YaCP?format=xml",
        'dailybeast': "http://feeds.feedburner.com/thedailybeast/articles?format=xml",
        'tpm': "https://talkingpointsmemo.com/feed/all",
        'motherjones': "http://feeds.feedburner.com/motherjones/BlogsAndArticles?format=xml",
        'alternet': 'http://feeds.feedblitz.com/alternet',
        'rawstory': "http://www.rawstory.com/feed/"
    }
}


class DBHelper(object):
    """
    A class that helps create database stuff. Will be renamed, this is just a placeholder.
    """
    def __init__(self, database="news"):
        self.connection = None
        self.open_connection()
        self.old_df = None

    def _insert_values(self, title, description, bias):
        """
        Parameters:
            title: str, Name of the article
            description: str, more detailed description
            bias: str, 'conservative' or 'liberal'

        return: None
        """
        try:
            with self.connection.cursor() as cursor:
                query = 'INSERT INTO feed_stories(title, description, bias) VALUES (\'{title}\', \'{description}\', ' \
                        '\'{bias}\')'.format(title=title, description=description, bias=bias)
                cursor.execute(query)
                self.connection.commit()

        except Exception as e:
            self.connection.rollback()

    def _clean_text(self, text):
        """
        Takes feed strings and removes unneeded information, such as html content and extra 
        characters.

        Parameters:
            text: str, text to be cleaned

        Returns:
            str: lower-cased version of the feed
            """
        soup = BeautifulSoup(text, 'lxml')
        text_only = soup.text
        text_spacey = re.sub('[^\w|^ ]', ' ', text_only)
        text_less_space = re.sub('\ {1,}', ' ', text_spacey)
        text_clean = ''.join([c for c in text_less_space if 0 < ord(c) < 127])
        return text_clean

    def _get_feeds(self, bias, articles_parsed=None):
        """
        Goes through the given feed (bias) and searches for new content
        Parameters:
            bias: str, 'conservative' or 'liberal'
            articles_parsed: dictionary with the articles that are in
                             the db
        Returns:
            dict: includes information about the feeds obtained
        """
        feeds_urls = biased_feeds[bias]
        feeds_parsed = {page: feedparser.parse(feed) for page, feed in feeds_urls.items()}
        new_articles = {"title": [], "description": [], "bias": []}
        if not articles_parsed:
            articles_parsed = new_articles
        for _, page_content in feeds_parsed.items():
            for article in page_content['entries']:
                title = self._clean_text(article["title"])
                if title not in articles_parsed['title']:
                    description = self._clean_text(article["description"])
                    if len(description) > 1000:
                        description = description[:999]
                    new_articles["title"].append(title)
                    new_articles["description"].append(description)
                    new_articles["bias"].append(bias)
        return new_articles

    def update_sql(self, article_dict):
        """
        Parameters:
            article_dict: a dictionary
        Returns:
            None
        """
        for i in range(len(article_dict['title'])):
            title = article_dict["title"][i]
            description = article_dict['description'][i]
            bias = article_dict['bias'][i]
            self._insert_values(title, description, bias)

    def close_connection(self):
        self.connection.close()

    def open_connection(self):
        self.connection = pymysql.connect(host='localhost',
                                          user=dbconfig.db_user,
                                          passwd=dbconfig.db_password,
                                          db="news")

    def get_old_df(self):
        self.old_df = pd.read_sql_query('SELECT * FROM feed_stories', self.connection)
        return self.old_df

    def get_connection(self):
        return self.connection

    def update_feed(self):
        """
        Takes from dictionary of feeds and updates the sql database.
        """
        try:
            self.get_old_df()
            old_dict = self.old_df.to_dict('list')
            new_articles = self._get_feeds('conservative', old_dict)
            self.update_sql(new_articles)
            new_articles = self._get_feeds('liberal', old_dict)
            self.update_sql(new_articles)

        finally:
            self.connection.close()


if __name__ == '__main__':
    db = DBHelper()
    db.update_feed()
