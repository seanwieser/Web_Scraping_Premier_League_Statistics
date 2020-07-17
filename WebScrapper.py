from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import numpy as np
import urllib.request
import time

class PlayerScrapper:
    def __init__(self):
        self.year = 2000
        self.year_dict = self._make_years_dict()
        self.str_dict = {'url': '', 'local path': ''}
        self._update_str_dict()

    def _update_str_dict(self):
        self.str_dict['url'] = f'https://www.premierleague.com/players?se={self.year_dict[self.year]}'
        self.str_dict['local path'] = f'data/epl/epl_players/{self.year}_epl_players.html'

    def _make_years_dict(self):
        # Initializating map specific to players website for years 2018-2000
        years = np.arange(2018, 1999, -1)
        year_codes = ['210', '79', '54', '42', '27'] + [x for x in range(22, 8, -1)]
        return dict(zip(years, year_codes))

    def _write_html_from_url(self):
        url = self.str_dict['url']
        print(f'pulling and opening players html from url:\n{url}')
        browser = webdriver.Chrome(executable_path='/home/seanwieser/sel_drivers/chromedriver')
        browser.get(self.str_dict['url'])
        time.sleep(5)
        elem = browser.find_element_by_tag_name("body")
        no_of_pagedowns = 60
        for cur_num in range(no_of_pagedowns, 0, -1):
            if not cur_num%20:
                print(f'Page Down: {cur_num}')
            elem.send_keys(Keys.PAGE_DOWN)
            time.sleep(1)
        f = open(self.str_dict['local path'], 'w')
        f.write(browser.page_source)
        f.close()
        browser.close()

    def html(self, year):
        self.year = year
        self._update_str_dict()
        if not Path(self.str_dict['local path']).is_file():
            self._write_html_from_url()
        return open(self.str_dict['local path'])

    

class TransferScrapper:
    def __init__(self):
        self.year = 2000
        self.str_dict = {'url': '', 'local path': ''}
        self._update_str_dict()

    def _update_str_dict(self):
        self.str_dict['url'] = f'https://www.transfermarkt.us/premier-league/transfers/wettbewerb/GB1/plus/?saison_id={self.year}&s_w=&leihe=0&intern=0&intern=1'
        self.str_dict['local path']= f'data/epl/epl_transfers/{self.year}_epl_transfers.html'

    def _write_html_from_url(self):
        url = self.str_dict['url']
        print(f'pulling and opening transfers html from url:\n{url}')
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:63.0) Gecko/20100101 Firefox/63.0'}
        req = urllib.request.Request(url=self.str_dict['url'], headers=headers) # self request object will integrate your URL and the headers defined above
        page_html = ''
        with urllib.request.urlopen(req) as response:
            page_html = response.read()
        f = open(self.str_dict['local path'], 'wb')
        f.write(page_html)
        f.close()

    def change_year(self, new_year):
        self.year = new_year
        self._update_str_dict()

    def html(self, year):
        self.year = year
        self._update_str_dict()
        if not Path(self.str_dict['local path']).is_file():
            self._write_html_from_url()
        return open(self.str_dict['local path'])