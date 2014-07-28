#  Scraper for Florida 2nd District Court of Appeal
# CourtID: flaapp2
# Court Short Name: flaapp2
# Author: Andrei Chelaru
# Reviewer:
# Date created: 21 July 2014


from datetime import date
import time
import requests
from lxml import html

from juriscraper.OpinionSite import OpinionSite
from juriscraper.opinions.united_states.state import fla


class Site(fla.Site):
    def __init__(self):
        super(Site, self).__init__()
        self.court_id = self.__module__
        d = date.today()
        self.url = 'http://www.2dca.org/opinions/Opinions_Yearly_Links/{year}/{month_yr}.shtml'.format(
            year=d.year,
            month_yr=d.strftime("%B_%y")
        )

    def _download(self, request_dict={}):
        html_l = OpinionSite._download(self)
        s = requests.session()
        html_trees = []
        for url in html_l.xpath("//*[@class='cen']/a/@href"):
            r = s.get(url,
                      headers={'User-Agent': 'Juriscraper'},
                      **request_dict)
            r.raise_for_status()

            # If the encoding is iso-8859-1, switch it to cp1252 (a superset)
            if r.encoding == 'ISO-8859-1':
                r.encoding = 'cp1252'

            # Grab the content
            text = self._clean_text(r.text)
            html_tree = html.fromstring(text)
            html_tree.make_links_absolute(url)

            remove_anchors = lambda url: url.split('#')[0]
            html_tree.rewrite_links(remove_anchors)
            html_trees.append(html_tree)
        return html_trees

    def _get_case_names(self):
        case_names = []
        for html_tree in self.html:
            case_names.extend(self._return_case_names(html_tree))
        return case_names

    @staticmethod
    def _return_case_names(html_tree):
        path = "//th//a[contains(., '/')]/text()"
        return list(html_tree.xpath(path))

    def _get_download_urls(self):
        download_urls = []
        for html_tree in self.html:
            download_urls.extend(self._return_download_urls(html_tree))
        return download_urls

    @staticmethod
    def _return_download_urls(html_tree):
        path = "//th//a[contains(., '/')]/@href"
        return list(html_tree.xpath(path))

    def _get_case_dates(self):
        case_dates = []
        for html_tree in self.html:
            case_dates.extend(self._return_dates(html_tree))
        return case_dates

    @staticmethod
    def _return_dates(html_tree):
        path = "//h1/text()"
        dates = []
        text = html_tree.xpath(path)[0]
        case_date = date.fromtimestamp(time.mktime(time.strptime(text.strip(), '%B %d, %Y')))
        dates.extend([case_date] * int(html_tree.xpath("count(//th//a[contains(., '/')])")))
        return dates

    def _get_precedential_statuses(self):
        return ['Published'] * len(self.case_dates)

    def _get_docket_numbers(self):
        docket_numbers = []
        for html_tree in self.html:
            docket_numbers.extend(self._return_docket_numbers(html_tree))
        return docket_numbers

    @staticmethod
    def _return_docket_numbers(html_tree):
        path = "//th//a[contains(., '-')]/*/text()"
        return list(html_tree.xpath(path))