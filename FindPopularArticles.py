#!/usr/bin/env python
"""
FindPopularArticles.py

Usage:
    ./FindPopularArticles.py [-h] [-n NUM_TRIALS] [-l LANGUAGE] [-t TOPN]

Options:
    -h --help                       Show this screen
    -n --num-trials NUM_TRIALS      Number of random trials to perform [default: 100]
    -l --language LANGUAGE          A two-letter language code such as "en" (English), "de"
                                    (German), etc.  See
                                    https://en.wikipedia.org/wiki/List_of_Wikipedias#Detailed_list
                                    for more details. [default: en]
    -t --top-n TOPN                 Filter the "top n" outputs. If 0, don't filter [default: 5]

This script runs through NUM_TRIALS random wiki pages for a random starting article and tries to
identify which articles are the most popular when traversing the first link of each article.

Copyright (c) 2016 Frederic Spieler
"""

from WikiCrawler import WikiCrawler
import operator
try:
  from docopt import docopt
except e:
  print "Missing dependency: docopt. If pip available, try `# pip install docopt`."
  exit(1)

def percent(num, denom):
  return str(100 * num/denom) + "%"

if __name__ == "__main__":
  import sys
  arguments = docopt(__doc__, version = "FindPopularArticles.py 0.1")
  num = int(arguments["--num-trials"])
  lang = arguments["--language"]
  topn = int(arguments["--top-n"])
  counts = {}
  for i in xrange(num):
    crawler = WikiCrawler(language=lang, target="--garbage--") #unfindable
    start = crawler.getRandomArticle()
    crawler.crawlFrom(start)
    for k in crawler.cache.iterkeys():
      if k in counts:
        counts[k] += 1
      else:
        counts[k] = 1
  counts = sorted(counts.items(),key=operator.itemgetter(1),reverse=True)
  if topn == 0:
    topn = len(counts)
  elif topn > len(counts):
    topn = len(counts)
  for i in xrange(topn):
    print percent(counts[i][1], num), counts[i][0],
    if "en" != lang:
      import sys
      sys.stdout.flush()
      print WikiCrawler.getTranslatedArticle(counts[i][0],lang,"en")
    else: print #newline

