from bs4 import BeautifulSoup
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
from WebScrapper import *

# parameter year represents year of season start must be in the range 2000-2018
def scrape_market(year, func):
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
    p_scrapper = PlayerScrapper()
    for year in range(2017, 2016, -1):
        print(f'Scraping {year}')
        p_scrapper.execute_year(year)