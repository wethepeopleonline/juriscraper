#  Scraper for Georgia Appeals Court
# CourtID: gactapp
# Court Short Name: gactapp
# Author: Andrei Chelaru
# Reviewer:
# Date created: 25 July 2014


from datetime import date

from juriscraper.opinions.united_states.state import ga
from lib.string_utils import titlecase


class Site(ga.Site):
    def __init__(self):
        super(Site, self).__init__()
        self.court_id = self.__module__
        self.case_date = date.today()
        self.base_path = "id('art-main')//tr[position() > 1]"
        self.url = 'http://www.gaappeals.us/docketdate/results_all.php?searchterm={mn}%2F{day}%2F{year}&searchterm2={mn}%2F{day}%2F{year}&submit=Search'.format(
            mn=self.case_date.month,
            day=self.case_date.day,
            year=self.case_date.year
        )

    def _get_case_names(self):
        path = "{base}/td[2]/text()".format(base=self.base_path)
        return [titlecase(e) for e in self.html.xpath(path)]

    def _get_download_urls(self):
        path = "{base}/td[6]/a/@href".format(base=self.base_path)
        return list(self.html.xpath(path))

    def _get_case_dates(self):
        return [self.case_date] * int(self.html.xpath("count({base})".format(base=self.base_path)))

    def _get_precedential_statuses(self):
        return ['Published'] * len(self.case_names)

    def _get_docket_numbers(self):
        path = "{base}/td[1]/text()".format(base=self.base_path)
        return list(self.html.xpath(path))

    def _get_dispositions(self):
        path = "{base}/td[4]/text()".format(base=self.base_path)
        return [titlecase(e) for e in self.html.xpath(path)]