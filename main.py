from bs4 import BeautifulSoup
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import urllib.request
from pathlib import Path
import numpy as np


def transfers_html(year):
    transfers_url = f'https://www.transfermarkt.us/premier-league/transfers/wettbewerb/GB1/plus/?saison_id={year}&s_w=&leihe=0&intern=0&intern=1'
    local_html_str = f'data/epl_transfers/{year}_epl_transfers.html'
    page_html = ''
    if not Path(local_html_str).is_file():
        print(f'pulling and opening html for year {year}')
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:63.0) Gecko/20100101 Firefox/63.0'}
        req = urllib.request.Request(url=transfers_url, headers=headers) # this request object will integrate your URL and the headers defined above
        with urllib.request.urlopen(req) as response:
            page_html = response.read()
        f = open(local_html_str, 'wb')
        f.write(page_html)
        f.close()
    return open(local_html_str)

def players_html(year):
    # Specific to website for years 2018-2000
    years = np.arange(2018, 1999, -1)
    year_codes = ['210', '79', '54', '42', '27']
    for i in range(22, 8, -1):
        year_codes.append(str(i))
    years_dict = dict(zip(year_codes, years))


     
    print(years_dict)
    
    print()

    
def scrape_market(year, func):
    html_file = func(year)

    # soup = BeautifulSoup(html_file, 'html.parser')    
    '''
    boxes Structure
    0: League Info
    3: League Transfer Stats
    4-23: Team Tables
    '''
    # boxes = soup.select('.box')
    
    '''

    '''
    # print(boxes[4].select('.responsive-table')[0].find_all('tr')[1].select('.zentriert.alter-transfer-cell')[0].get_text()) # This gets all the ages in 
    # html_file.close()


if __name__ == "__main__":
    year = 2000
    # for year in range(2000, 2019):
    #     print(f'Scraping {year}')
    #     scrape_market(year)
    
    scrape_market(year, players_html)