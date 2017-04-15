#!/usr/bin/env python
import unittest

from WikiCrawler import WikiCrawler

class WikiCrawlerTester(unittest.TestCase):
  '''
  These are various 'hard cases' that came up during testing
  '''
  def test_hard_cases(self):
    crawler = WikiCrawler(target="/wiki/Philosophy")
    cases=["Deity","Colombia","Mexico","West_Bank","Irish_people","John_L._Brunner","Embryophyte","Vegetation","Provinces_of_Turkey","London"]
    for case in cases:
      self.assertTrue(crawler.crawlFrom("/wiki/"+case))

  def test_de_deutschland(self):
    # this didn't work because the first link is a .ogg file
    crawler = WikiCrawler(language="de")
    self.assertTrue(crawler.crawlFrom("/wiki/Deutschland"))

  def test_london(self):
    crawler = WikiCrawler()
    self.assertEqual("/wiki/Capital_city",crawler.getPage("/wiki/London")[1])
  
  def test_poland(self):
    crawler = WikiCrawler()
    self.assertEqual("/wiki/Central_Europe",crawler.getPage("/wiki/Poland")[1])

  def test_cache_doesnt_affect_results_but_lowers_total_pages_hits(self):
    cache = WikiCrawler(target="/wiki/Philosophy")
    nocache = WikiCrawler(target="/wiki/Philosophy",enableCache=False)
    cases=["Deity","Colombia","Mexico","West_Bank","Irish_people","John_L._Brunner","Embryophyte","Vegetation","Provinces_of_Turkey","London","Canada"]
    for case in cases:
        case = "/wiki/" + case
        self.assertEqual(nocache.crawlFrom(case), cache.crawlFrom(case))
    self.assertLess(cache.count, nocache.count)

  def test_disambiguation_page_new(self):
    crawler = WikiCrawler(target="/wiki/Philosophy")
    self.assertTrue(crawler.crawlFrom("/wiki/New"))

  def test_tabular_page(self):
    crawler = WikiCrawler(target="/wiki/Philosophy")
    self.assertTrue(crawler.crawlFrom("/wiki/Cross-America_flight_air_speed_record"))

  def test_computer_science(self):
    crawler = WikiCrawler()
    self.assertTrue(crawler.crawlFrom("/wiki/Computer_science"))

  def test_telecommunication(self):
    crawler = WikiCrawler()
    self.assertTrue(crawler.crawlFrom("/wiki/Telecommunication"))

if __name__ == '__main__':
  unittest.main()
