from bs4 import BeautifulSoup
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import numpy as np
import urllib.request
import time

def write_html_from_url_req(url, local_html_str):
    print(f'pulling and opening html from url:\n{url}')
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:63.0) Gecko/20100101 Firefox/63.0'}
    req = urllib.request.Request(url=url, headers=headers) # this request object will integrate your URL and the headers defined above
    page_html = ''
    with urllib.request.urlopen(req) as response:
        page_html = response.read()
    f = open(local_html_str, 'wb')
    f.write(page_html)
    f.close()

def write_html_from_url_sel(url, local_html_str):
    print(f'pulling and opening html from url:\n{url}')
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

    f = open(local_html_str, 'w')
    f.write(browser.page_source)
    f.close()
    browser.close()


def transfers_html(year):
    transfers_url = f'https://www.transfermarkt.us/premier-league/transfers/wettbewerb/GB1/plus/?saison_id={year}&s_w=&leihe=0&intern=0&intern=1'
    local_html_str = f'data/epl/epl_transfers/{year}_epl_transfers.html'
    if not Path(local_html_str).is_file():
        write_html_from_url_req(transfers_url, local_html_str)
    return open(local_html_str)


# parameter year represents year of season start must be in the range 2000-2018
def players_html(year):
    # Initializating map specific to players website for years 2018-2000
    years = np.arange(2018, 1999, -1)
    year_codes = ['210', '79', '54', '42', '27']
    for i in range(22, 8, -1):
        year_codes.append(str(i))
    years_dict = dict(zip(years, year_codes))

    players_url = f'https://www.premierleague.com/players?se={years_dict[year]}'
    local_html_str = f'data/epl/epl_players/{year}_epl_players.html'
    if not Path(local_html_str).is_file():
        write_html_from_url_sel(players_url, local_html_str)
    return open(local_html_str)


def scrape_market(year, func):
    html_file = func(year)

    # soup = BeautifulSoup(html_file, 'html.parser') 
    # print(soup)

    # .dataContainer.indexSection class only exists one time 
    # players = soup.select('.dataContainer.indexSection')
    # print(type(players))

    '''
    boxes Structure
    0: League Info
    3: League Transfer Stats
    4-23: Team Tables
    '''
    # boxes = soup.select('.box')
 
    # print(boxes[4].select('.responsive-table')[0].find_all('tr')[1].select('.zentriert.alter-transfer-cell')[0].get_text()) # This gets all the ages in 
    html_file.close()


if __name__ == "__main__":
    
    for year in range(2000, 2019):
        print(f'Scraping {year}')
        scrape_market(year, transfers_html)
        scrape_market(year, players_html)