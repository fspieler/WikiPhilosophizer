
# WikiPhilosophizer

> Clicking on the first link in the main text of a Wikipedia article, and then
> repeating the process for subsequent articles, usually eventually gets one to
> the Philosophy article (admittedly, this is somewhat arbitrary, as the same
> can be said of 'problem solving', the article the first link from 'philosophy'
> leads to).

- https://en.wikipedia.org/wiki/Wikipedia:Getting_to_Philosophy

WikiPhilosophizer is a project that explores this phenomenon.

The main scripts:

* WikiCrawler.py: Find if a path exists from a given, or if not provided, random starting page to a target wiki page, or, if not provided, /wiki/Philosophy. Optimized to cache web pages to avoid traversing previously traversed paths.

* FindPopularArticles.py: For a given language, start from various random starting points and see what pages are the most popular. Could be optimized to recognize previously traversed loops.

* multilang-\*: Generate results
