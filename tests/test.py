# -*- coding: utf-8 -*-
"""
Unit tests of the classes in the Markivet module.
"""
import datetime
import unittest
import os, sys

# Make sure relative import of modules work...
testdir = os.path.dirname(__file__)
srcdir = "../"
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))

# ...so that we can import this
from markivet import Markivet


class MarkivetTests(unittest.TestCase):

    def setUp(self):
        self.markivet = Markivet("testfile1.txt", verbose=False)

    def test_import_file_works(self):
        news = self.markivet.articles
        self.assertEqual(len(self.markivet.files), 1)
        self.assertEqual(len(news), 14)
        self.assertEqual(news[4].title, "Reinfeldt vinner väljare från alla övriga partier")
        self.assertEqual(news[13].title, "De onda, de goda och de fula")

    def test_first_news_article_contain_values(self):
        news = self.markivet.articles[0]
        self.assertEqual(news.title, "Tro och vetande")
        self.assertEqual(news.date_raw, "2004-12-29 09:31")
        self.assertEqual(news.date, datetime.datetime(2004, 12, 29, 9, 31, 0))
        self.assertEqual(news.newspaper, "Hagens Knuheter")
        self.assertEqual(news.edition, "Publicerat på webb.")
        self.assertEqual(news.lead, "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse pulvinar purus...")
        self.assertEqual(news.body[:37], "©Sonnier<br>Alla artiklar är skyddade")
        self.assertEqual(news.url, "http://ret.nu/7Ml1g0k")

    def test_generator_works(self):
        for i, news in enumerate(self.markivet):
            self.assertIsNotNone(news.title)
        self.assertEqual(i, 13)

    def test_remove_duplicates_works(self):
        ma1 = Markivet("testfile1.txt", verbose=False)
        ma2 = Markivet("testfile2.txt", verbose=False)
        ma3 = ma2
        markivet = ma1 + ma2 + ma3
        self.assertEqual(len(markivet), 42)
        markivet.remove_duplicates()
        self.assertEqual(len(markivet), 14)
        markivet.remove_duplicates()
        self.assertEqual(len(markivet), 14)

    def test_import_folder_works(self):
        markivet = Markivet.from_folder("./testfile*.txt", verbose=False)
        self.assertEqual(len(markivet.files), 2)
        self.assertEqual(len(markivet), 28)
        markivet.remove_duplicates()
        self.assertEqual(len(markivet), 14)
        self.assertEqual(len(markivet.articles), 14)


if __name__ == '__main__':
    unittest.main()
