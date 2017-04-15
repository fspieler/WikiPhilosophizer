#!/usr/bin/env python
"""
WikiCrawler

Usage:
    ./WikiCrawler.py [-h] [-n NUM_RANDOM_TRIALS |-s STARTING_ARTICLE] [-l LANGUAGE] [-t TARGET]

Options:
    -h --help                       Show this screen
    -n --num-trials NUM_TRIALS      Number of random trials to perform [default: 1]
    -s --starting STARTING          The relative URL of an article to start crawling from, of
                                    the format "/wiki/Relative_url"
    -l --language LANGUAGE          A two-letter language code such as "en" (English), "de"
                                    (German), etc.  See
                                    https://en.wikipedia.org/wiki/List_of_Wikipedias#Detailed_list
                                    for more details. [default: en]
    -t --target TARGET              The relative URL of the destination article, of the format
                                    "/wiki/Relative_url". While this is assumed to be /wiki/Philosophy,
                                    if you choose another language and don't provide a target,
                                    the crawler will attempt to find that language's philosophy page.

If neither a number of trials nor a starting article URL are provided, by default the wiki crawler
will do a single trial from a ramdom starting article.

Copyright (c) 2016 Frederic Spieler
"""
from lxml import html
from lxml import etree
import re
import requests
import sys

try:
    from docopt import docopt
except e:
    print "Missing dependency: docopt. If pip available, try `# pip install docopt`."
    exit(1)

node_hook = None
links_hook = None

class WikiCrawler(object):
    #class constants
    RETRIES_COUNT=5
    RANDOM_PATH="/wiki/Special:Random"
    def __init__(self,target=None,language="en",enableCache=True):
        self.language = language
        if target is None:
            if "en" == language:
                self.target = "/wiki/Philosophy"
            else: # not English, find that language's Philosophy article
                self.target = self.getTranslatedPhilosophy()
                if self.target is None:
                    self.target = "/wiki/Philosophy" #we tried :(
        else:
            self.target = target
        self.prefix = "https://"+language+".wikipedia.org"
        self.count = 0
        self.enableCache = enableCache
        '''this "garbage" is useful because one might try to find the entire
        link chain without ending at a specific article. In this case we don't
        want to actually get the final page.
        '''
        if "--garbage--" == target:
            self.target_title = "--garbage"
        else:
            target_page = self.getPage(self.target)
            self.target_title = target_page[0]
        '''
        cache whether this relative link was already found
        to reach target or not
        '''
        self.cache = {}

    @classmethod
    def getTranslatedArticle(clazz, article, from_lang, to_lang):
        original_url = "https://"+from_lang+".wikipedia.org"+article
        page = clazz.downloadHTML(original_url)
        tree = html.fromstring(page)
        expression = ("//div[@id='p-lang']//a[@lang='"+to_lang+"']/@href")
        lang_url = tree.xpath(expression)
        if lang_url is None or 0 == len(lang_url):
            return "<no translation found>"
        return "/"+"/".join(lang_url[0].split("/")[3:])

    def getTranslatedPhilosophy(self):
        return self.getTranslatedArticle("/wiki/Philosophy","en",self.language)

    def getFullPath(self,path):
        return self.prefix + path

    @classmethod
    def downloadHTML(clazz,fullPath):
        tries = WikiCrawler.RETRIES_COUNT + 1
        while True:
            response = requests.get(fullPath)
            tries -= 1
            if 200 == response.status_code:
                break
            if 404 == response.status_code:
                print "probable dead link: " + fullPath
                break
            if tries == 0:
                raise Exception("Failed to download wiki page at "+fullPath+", latest status: " + str(response.status_code))
        return response.content

    @classmethod
    def find_first_link(clazz, paragraphs):
        """
        Find first non-parenthesized link

        This loop iterates through each HTML "node" (it was designed for <p></p> tags but
        works for other HTML nodes such as <h1> and <table).

        For each node, it finds the locations of all possible wiki links; then it iterates
        through the text of each "paragraph" keeping track of how many parens there are. 

        When it finds a link that is not enclosed by parens, it double checks that the link is
        not a .ogg file (which is usually a pronunciation link) or a help page; these *should*
        be parenthesized but that in practice that doesn't always happen.

        Once the first link is found, this function can return.
        """
        for p in paragraphs:
            parens_count = 0
            flat = etree.tostring(p)
            current_link = 0
            link_indices = \
                [(m.start(), m.end()) for m in re.finditer(r'/wiki/[^\'"]+',flat)]
            if 0 == len(link_indices): 
                continue
            for idx, c in enumerate(flat):
                if idx == link_indices[current_link][0]:
                    link = flat[link_indices[current_link][0]:link_indices[current_link][1]]
                    if parens_count == 0:
                        if link[-4:] == ".ogg":
                            current_link += 1
                            continue
                        elif link[:11] == "/wiki/Help:":
                            current_link += 1
                            continue
                        return link
                    else:
                        current_link += 1
                        if current_link >= len(link_indices):
                            break #go to next paragraph
                if c == "(":
                    parens_count += 1
                elif c == ")":
                    parens_count -= 1
        return None #none found!


    @classmethod
    def clearXPath(clazz,doctree,xpath):
        '''
        There are a lot of tags that may contain links within the "main" content <div>
        but that should not be considered. Easiest thing is to get rid of them to make
        sure they're not considered.
        '''
        for node in doctree.xpath(xpath):
            for subelement in node:
                subelement.clear()

    @classmethod
    def parseHTML(clazz,page):
        doctree = html.fromstring(page)
        title = doctree.xpath("//title/text()")[0].split(" - ")[0].encode("utf-8")
        clazz.clearXPath(doctree,"//i") #clear italics
        clazz.clearXPath(doctree,"//sup") #clear superscripts
        clazz.clearXPath(doctree,"//span[@id='coordinates']") #clear coordinates from geographic articles
        '''this xpath expression will return a list of all <p>, <h1-3>, <ul>, and
        <table class="wikitable"> elements found in a page.
        '''
        expression = "//div[@id='mw-content-text']/"
        expression += "*[self::p or self::h1 or self::h2 or self::h3 or self::ul or self::table[@class='wikitable']]"
        paragraphs = doctree.xpath(expression)
        first_link = clazz.find_first_link(paragraphs)
        return (title, first_link)

    def getPage(self,path):
        '''
        this method retries a title and the first link of a relative wiki link
        '''
        self.count += 1
        page = self.downloadHTML(self.getFullPath(path))
        return self.parseHTML(page)

    def getRandomArticle(self):
        '''
        this method retries a title and the first link of a random wiki article for the
        current language
        '''
        return self.getPage(WikiCrawler.RANDOM_PATH)

    def appendToCache(self, newLinks, success):
        for link in newLinks:
            self.cache[link] = success

    def crawlFrom(self,start):
        '''
        This method is the complicated bit...
        '''

        if type(start) is str: # convert relative link to (title, first_link)
            start = self.getPage(start)

        '''
        pathPages is the set of all pages visited during this crawl

        We will use it to calculate whether there is a cycle on the current crawl.

        If caching is enabled, we will also put these pages to cache once we know whether
        they connect to target.
        '''
        pathPages = set() 
        title, first_link = start
        print "Starting page: " + title
        success = None
        while True: 
            sys.stdout.flush()
            if first_link is None:
                success = False
                print "No links found!"
                break
            if first_link in pathPages:
                success = False
                print "Cycle found (already visited " + first_link+")"
                break
            pathPages.add(first_link)
            if first_link == self.target:
                success = True
                break
            if self.enableCache and first_link in self.cache:
                success = self.cache[first_link]
                print "Found " + str(first_link) + " in cache!"
                break
            title, first_link = self.getPage(first_link)
            print "Next page:", title
        print ("Reached " if success else "Failed to reach " ) + "target "+self.target_title
        if self.enableCache:
            self.appendToCache(pathPages, success)
        return success

    def crawlFromNew(self,start):
        '''
        This method is the complicated bit...
        '''

        if type(start) is str: # convert relative link to (title, first_link)
            start = self.getPage(start)

        '''
        pathPages is the set of all pages visited during this crawl

        We will use it to calculate whether there is a cycle on the current crawl.

        If caching is enabled, we will also put these pages to cache once we know whether
        they connect to target.
        '''
        pathPages = set() 
        title, first_link = start
        print "Starting page: " + title
        success = None
        while True: 
            sys.stdout.flush()
            if first_link is None:
                success = False
                print "No links found!"
                break
            if first_link in pathPages:
                success = False
                print "Cycle found (already visited " + first_link+")"
                break
            pathPages.add(first_link)
            if first_link == self.target:
                success = True
                break
            if self.enableCache and first_link in self.cache:
                success = self.cache[first_link]
                print "Found " + str(first_link) + " in cache!"
                break
            title, first_link = self.getPage(first_link)
            print "Next page:", title
        print ("Reached " if success else "Failed to reach " ) + "target "+self.target_title
        if self.enableCache:
            self.appendToCache(pathPages, success)
        return success

if __name__ == "__main__":
    arguments = docopt(__doc__, version="wikiCrawler 0.1")
    crawler = WikiCrawler(
        target = arguments["--target"],
        language = arguments["--language"].strip('"')
    )
    if arguments["--starting"] is None:
        numTrials = int(arguments["--num-trials"])
        successes = 0
        failures = 0
        for i in xrange(numTrials):
            start = crawler.getRandomArticle()
            success = crawler.crawlFrom(start)
            sys.stdout.flush()
            if success: successes += 1
            else: failures += 1
        if numTrials > 1:
            print successes, "successes"
            print failures, "failures"
    else:
        print "Success" if crawler.crawlFrom(arguments["--starting"].strip('"')) else "Failure"
    print crawler.count, "pages downloaded"
    sys.stdout.flush()
