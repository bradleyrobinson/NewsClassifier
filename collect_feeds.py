import dbconfig
import pymysql
import pandas as pd
import feedparser
import re
from bs4 import BeautifulSoup

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
    def __init__(self, database="news"):
        self.connection = pymysql.connect(host='localhost',
                               user=dbconfig.db_user,
                               passwd=dbconfig.db_password,
                               db=database)

    def _insert_values(self, title, description, date, bias):
        """
        
        :param title: 
        :param description: 
        :param date: 
        :param bias: 
        :return: 
        """
        try:
            with self.connection.cursor() as cursor:
                query = 'INSERT INTO feed_stories(title, description, bias) VALUES ({title}, {description}, ' \
                        '{bias})'.format(title=title, description=description, date=date, bias=bias)
                cursor.execute(query)
                self.connection.commit()
        except:
            self.connection.rollback()

    def _clean_text(self, text):
        """
            Takes feed strings and removes unneeded information, such as html content and extra characters

            Parameters:
                text:

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
            bias: 
            articles_parsed: 
        
        Returns: 
        """
        feeds_urls = biased_feeds[bias]
        feeds_parsed = {page: feedparser.parse(feed) for page, feed in feeds_urls.items()}
        if not articles_parsed:
            articles_parsed = {"title": [], "description": [], "page": [], "bias": []}
        for key, page_content in feeds_parsed.items():
            for article in page_content['entries']:
                title = self._clean_text(article["title"])
                if title not in articles_parsed['title']:
                    description = self._clean_text(article["description"])
                    articles_parsed["title"].append(title)
                    articles_parsed["description"].append(description)
                    articles_parsed["page"].append(key)
                    articles_parsed["bias"].append(bias)
        return articles_parsed

    def update_sql(self, article_dict):
        """
        
        Parameters:
            article_dict: 
        Returns:
            None
        """
        for i in range(len(article_dict['title'])):
            title = article_dict["title"][i]
            description = article_dict['description'][i]
            bias = article_dict['bias'][i]
            self._insert_values(title, description, bias)
        pass

    def update_feed(self):
        try:
            with self.connection.cursor() as cursor:
                df = pd.read_sql_query('SELECT * FROM feed_stories', cursor)
                new_articles = self._get_feeds('conservative', df.to_dict('list'))
                new_articles = self._get_feeds('liberal', new_articles)
                self.update_sql(new_articles)

        finally:
            self.connection.close()
        pass


if __name__ == '__main__':
    DBHelper()
    DBHelper.update_feed()
