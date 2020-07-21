from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import urllib.request
import time
import unicodedata

class PlayerScrapper:
    def __init__(self):
        self.year = 2000
        self.players_url = []
        self.year_dict = self._make_years_dict()
        self.str_dict = {'url list': '', 'local list': '', 'local player': ''}
        self._update_str_dict()

    def _update_str_dict(self):
        self.str_dict['url list'] = f'https://www.premierleague.com/players?se={self.year_dict[self.year]}'
        self.str_dict['local list'] = f'data/epl/epl_players/{self.year}/{self.year}_epl_players.html'
        self.str_dict['local player'] = f'data/epl/epl_players/{self.year}/players/'

    def _make_years_dict(self):
        # Initializating map specific to players website for years 2018-2000
        years = np.arange(2018, 1999, -1)
        year_codes = ['210', '79', '54', '42', '27'] + [x for x in range(22, 8, -1)]
        return dict(zip(years, year_codes))

    def _write_list_html_from_url(self):
        url = self.str_dict['url list']
        print(f'pulling and opening players list html from url:\n{url}')
        browser = webdriver.Chrome(executable_path='/home/seanwieser/sel_drivers/chromedriver')
        browser.get(url)
        time.sleep(5)
        elem = browser.find_element_by_tag_name("body")
        no_of_pagedowns = 60
        for cur_num in range(no_of_pagedowns, 0, -1):
            if not cur_num%20:
                print(f'Page Down: {cur_num}')
            elem.send_keys(Keys.PAGE_DOWN)
            time.sleep(1)
        f = open(self.str_dict['local list'], 'w')
        f.write(browser.page_source)
        f.close()
        browser.close()

    def _write_player_html_from_url(self, player_str):
        url = self.players_url[player_str]
        print(f'pulling and opening player stats html for:\n{player_str}\t\t{url}')
        browser = webdriver.Chrome(executable_path='/home/seanwieser/sel_drivers/chromedriver')
        browser.get(url)
        time.sleep(4)
        f = open(''.join([self.str_dict['local player'], player_str.replace(' ', '_')]), 'w')
        f.write(browser.page_source)
        f.close()
        browser.close()
    
    '''
    def _write_player_html_from_url(self, player_str):
        url = self.players_url[player_str]
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:63.0) Gecko/20100101 Firefox/63.0'}
        req = urllib.request.Request(url=url, headers=headers) # self request object will integrate your URL and the headers defined above
        page_html = ''
        with urllib.request.urlopen(req) as response:
            page_html = response.read()
        f = open(''.join([self.str_dict['local player'], player_str.replace(' ', '_')]), 'wb')
        f.write(page_html)
        f.close()
    '''

    def write_player_html(self):
        self._update_str_dict()
        for player_str in self.players_url.keys():
            if not Path(''.join([self.str_dict['local player'], player_str.replace(' ', '_')])).is_file() or player_str not in 'data/epl/ignored.html':
                self._write_player_html_from_url(player_str)

    def get_player_html(self, player_str):
        return open(''.join([self.str_dict['local player'], player_str]))

    def write_list_html(self):
        self._update_str_dict()
        if not Path(self.str_dict['local list']).is_file():
            self._write_list_html_from_url()

    def get_list_html(self):
        return open(self.str_dict['local list'])

    def get_ascii(self, s):
        if all(ord(c) < 128 for c in s):
            return s
        else:
            return unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode('utf-8')

    def parse_list_html(self, html):
        with open(self.str_dict['local list']) as fp:
            soup = BeautifulSoup(fp, 'html.parser')
        info = [[],[],[], {}]
        rows = soup.findAll('tr')
        for idx in range(1, len(rows)):
            contents = rows[idx].findAll('td')
            if len(contents[0])<1 or len(contents[1])<1 or len(contents[2])<1:
                print(f'Ignoring {idx} in year {self.year}')
                f = open('data/epl/ignored.html', 'w')
                f.write(str(contents))
                f.close()
                continue
            name = contents[0].findAll(text=True)[0].replace('.', '')
            position = contents[1].findAll(text=True)[0]
            nation = contents[2].findAll(text=True)
            player_url = ''.join([rows[idx].find('a')['href'][:38], rows[idx].find('a')['href'][38:].replace('.', '')])
            while ' ' in nation:
                nation.remove(' ')
            if len(nation)==0:
                nation = ''
            elif len(nation)==1:
                nation = nation[0]
            info[0].append(name.replace('.', ''))
            info[1].append(position)
            info[2].append(nation)
            info[3][self.get_ascii(name)] = ''.join(['https:', self.get_ascii(player_url), self.year_dict[self.year]]).replace('overview', 'stats?co=1&se=')
        list_df = pd.DataFrame(np.array(info[:3])).transpose().rename(columns={0: 'Name', 1: 'Position', 2: 'Nationality'})
        self.players_url = info[3]
        return list_df


    def execute(self, year):
        self.year = year
        self.write_list_html()
        players_df = self.parse_list_html(self.get_list_html())
        self.write_player_html()

'''   

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
        '''