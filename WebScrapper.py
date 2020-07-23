from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from cycler import cycler
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib._color_data as mcd
import urllib.request
import time
import unicodedata
import os
import sys
import datapackage


def _update_progress(count, total, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = 'X' * filled_len + '_' * (bar_len - filled_len)

    sys.stdout.write('-------------------------------------------------------->\
        [%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush()

class PlayerScrapper:
    def __init__(self):
        self.year = 2000
        self.players_url = []
        self.list_df = None
        self.year_dict = self._make_years_dict()
        self.str_dict = {'url list': '', 'local list': '', 'local player': ''}
        self._update_str_dict()

    def _update_str_dict(self):
        self.str_dict['url list'] = f'https://www.premierleague.com/players?se={self.year_dict[self.year]}'
        self.str_dict['local list'] = f'data/epl/epl_players/{self.year}/{self.year}_epl_players.html'
        self.str_dict['local player'] = f'data/epl/epl_players/{self.year}/players/'
        self.str_dict['local year'] = f'data/epl/epl_players/{self.year}'

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
        no_of_pagedowns = 80
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
        browser.maximize_window()
        time.sleep(3)
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
            test = Path(''.join([self.str_dict['local player'], player_str.replace(' ', '_')])).is_file()
            if not test and player_str not in 'data/epl/ignore/ignored.html':
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

    def parse_list_html_to_pandas(self, html):
        with open(self.str_dict['local list']) as fp:
            soup = BeautifulSoup(fp, 'html.parser')
        info = [[],[],[], {}]
        rows = soup.findAll('tr')
        for idx in range(1, len(rows)):
            contents = rows[idx].findAll('td')
            if len(contents[0])<1 or len(contents[1])<1 or len(contents[2])<1:
                # print(f'Ignoring {idx} in year {self.year}')
                f = open('data/epl/ignore/ignored.html', 'w')
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
            info[3][self.get_ascii(name)] = ''.join(['https:', self.get_ascii(player_url), str(self.year_dict[self.year])]).replace('overview', 'stats?co=1&se=')
        df_list = pd.DataFrame(np.array(info[:3])).transpose().rename(columns={0: 'Name', 1: 'Position', 2: 'Nationality'})
        self.players_url = info[3]
        self.list_df = df_list.set_index('Name')
        

    def _get_attack_stats(self, position, li):
        goals_per, penalties, freekicks, shots, shots_on, shooting_acc, big_missed = [None]*7
        goals = int(li.find_all('span', attrs={'class':'allStatContainer statgoals'})[0].getText())
        headed_goals = int(li.find_all('span', attrs={'class':'allStatContainer statatt_hd_goal'})[0].getText())
        rf_goals = int(li.find_all('span', attrs={'class':'allStatContainer statatt_rf_goal'})[0].getText())
        lf_goals = int(li.find_all('span', attrs={'class':'allStatContainer statatt_lf_goal'})[0].getText())
        woodwork = int(li.find_all('span', attrs={'class':'allStatContainer stathit_woodwork'})[0].getText())
        if position != 'Defender':
            goals_per = float(li.find_all('span', attrs={'class':'allStatContainer statgoals_per_game'})[0].getText())
            penalties = int(li.find_all('span', attrs={'class':'allStatContainer statatt_pen_goal'})[0].getText())
            freekicks = int(li.find_all('span', attrs={'class':'allStatContainer statatt_freekick_goal'})[0].getText())
            shots = int(li.find_all('span', attrs={'class':'allStatContainer stattotal_scoring_att'})[0].getText())
            shots_on = int(li.find_all('span', attrs={'class':'allStatContainer statontarget_scoring_att'})[0].getText())
            shooting_acc = int(li.find_all('span', attrs={'class':'allStatContainer statshot_accuracy'})[0].getText().strip('%'))
            big_missed = int(li.find_all('span', attrs={'class':'allStatContainer statbig_chance_missed'})[0].getText())
        return [goals, headed_goals, rf_goals, lf_goals, woodwork, goals_per, penalties, freekicks, shots, shots_on, shooting_acc, big_missed]

    def _get_defence_stats(self, position, li):
        tackles, blocked_shots, interceptions, clearances, headed_clearances, \
            tackle_success, recoveries, duels_won, duels_lost, success_5050, aerial_won, aerial_lost, \
                cleans, goals_conceded, own_goals, \
                    errors_goal, \
                    last_man_tackles, clearances_off_line = [None]*18
        if position != 'Goalkeeper':
            tackles = int(li.find_all('span', attrs={'class':'allStatContainer stattotal_tackle'})[0].getText())
            blocked_shots = int(li.find_all('span', attrs={'class':'allStatContainer statblocked_scoring_att'})[0].getText())
            interceptions = int(li.find_all('span', attrs={'class':'allStatContainer statinterception'})[0].getText())
            clearances = int(li.find_all('span', attrs={'class':'allStatContainer stattotal_clearance'})[0].getText())
            headed_clearances = int(li.find_all('span', attrs={'class':'allStatContainer stateffective_head_clearance'})[0].getText())

        if position != 'Forward' and position != 'Goalkeeper':
            tackle_success = int(li.find_all('span', attrs={'class':'allStatContainer stattackle_success'})[0].getText().strip('%'))
            recoveries = int(li.find_all('span', attrs={'class':'allStatContainer statball_recovery'})[0].getText())
            duels_won = int(li.find_all('span', attrs={'class':'allStatContainer statduel_won'})[0].getText())
            duels_lost =int(li.find_all('span', attrs={'class':'allStatContainer statduel_lost'})[0].getText())
            success_5050 = int(li.find_all('span', attrs={'class':'allStatContainer statwon_contest'})[0].getText())
            aerial_won = int(li.find_all('span', attrs={'class':'allStatContainer stataerial_won'})[0].getText())
            aerial_lost = int(li.find_all('span', attrs={'class':'allStatContainer stataerial_lost'})[0].getText())

        if position != 'Forward' and position != 'Midfielder':
            cleans = int(li.find_all('span', attrs={'class':'allStatContainer statclean_sheet'})[0].getText())
            goals_conceded = int(li.find_all('span', attrs={'class':'allStatContainer statgoals_conceded'})[0].getText())
            own_goals = int(li.find_all('span', attrs={'class':'allStatContainer statown_goals'})[0].getText())

        if position != 'Forward':
            errors_goal = int(li.find_all('span', attrs={'class':'allStatContainer staterror_lead_to_goal'})[0].getText())
            
        if position == 'Defender':
            last_man_tackles = int(li.find_all('span', attrs={'class':'allStatContainer statlast_man_tackle'})[0].getText())
            clearances_off_line = int(li.find_all('span', attrs={'class':'allStatContainer statclearance_off_line'})[0].getText())

        return [tackles, blocked_shots, interceptions, clearances, headed_clearances, \
            tackle_success, recoveries, duels_won, duels_lost, success_5050, aerial_won, aerial_lost, \
                cleans, goals_conceded, own_goals, \
                    errors_goal, \
                    last_man_tackles, clearances_off_line]

    
    def _get_discipline_stats(self, position, li):
        yellows, reds, fouls, offsides = [None]*4

        yellows = int(li.find_all('span', attrs={'class':'allStatContainer statyellow_card'})[0].getText())
        reds = int(li.find_all('span', attrs={'class':'allStatContainer statred_card'})[0].getText())
        fouls = int(li.find_all('span', attrs={'class':'allStatContainer statfouls'})[0].getText())
        if position != 'Goalkeeper':
            offsides = int(li.find_all('span', attrs={'class':'allStatContainer stattotal_offside'})[0].getText())

        return [yellows, reds, fouls, offsides]
        
    def _get_teamplay_stats(self, position, li):
        assists, passes, passes_per, big_chances, crosses, cross_accuracy, through_balls, accurate_long_balls, goalie_goals = [None]*9

        assists = int(li.find_all('span', attrs={'class':'allStatContainer statgoal_assist'})[0].getText())
        passes = int(li.find_all('span', attrs={'class':'allStatContainer stattotal_pass'})[0].getText().replace(',', ''))
        passes_per = float(li.find_all('span', attrs={'class':'allStatContainer stattotal_pass_per_game'})[0].getText())

        if position == 'Goalkeeper':
            goalie_goals = int(li.find_all('span', attrs={'class':'allStatContainer statgoals'})[0].getText())
        else:
            big_chances = int(li.find_all('span', attrs={'class':'allStatContainer statbig_chance_created'})[0].getText())
            crosses = int(li.find_all('span', attrs={'class':'allStatContainer stattotal_cross'})[0].getText())

        if position != 'Forward' and position != 'Goalkeeper':
            cross_accuracy = int(li.find_all('span', attrs={'class':'allStatContainer statcross_accuracy'})[0].getText().strip('%'))
            through_balls = int(li.find_all('span', attrs={'class':'allStatContainer stattotal_through_ball'})[0].getText())

        if position != 'Forward':
            accurate_long_balls = int(li.find_all('span', attrs={'class':'allStatContainer stataccurate_long_balls'})[0].getText())

        return [assists, passes, passes_per, big_chances, crosses, cross_accuracy, through_balls, accurate_long_balls, goalie_goals]
        

    def _get_goalkeeping_stats(self, li):
        saves = int(li.find_all('span', attrs={'class':'allStatContainer statsaves'})[0].getText())
        penalties_saved = int(li.find_all('span', attrs={'class':'allStatContainer statpenalty_save'})[0].getText())
        punches = int(li.find_all('span', attrs={'class':'allStatContainer statpunches'})[0].getText())
        high_claims = int(li.find_all('span', attrs={'class':'allStatContainer statgood_high_claim'})[0].getText())
        catches = int(li.find_all('span', attrs={'class':'allStatContainer statcatches'})[0].getText())
        sweeper_clearances = int(li.find_all('span', attrs={'class':'allStatContainer stattotal_keeper_sweeper'})[0].getText())
        throw_outs = int(li.find_all('span', attrs={'class':'allStatContainer statkeeper_throws'})[0].getText())
        goal_kicks = int(li.find_all('span', attrs={'class':'allStatContainer statgoal_kicks'})[0].getText())
        return [saves, penalties_saved, punches, high_claims, catches, sweeper_clearances, throw_outs, goal_kicks]


    def _get_stats(self, position, normalStats):
        attack, defence, teamplay, discipline, goalkeeping = [[],[],[],[],[]]
        for li in normalStats:
            category = li.find_all('div', attrs={'class': 'headerStat'})[0].getText().strip('\n')
            if category == 'Attack':
                attack = self._get_attack_stats(position, li) # 12
            elif category == 'Team Play':
                teamplay = self._get_teamplay_stats(position, li) # 9
            elif category == 'Defence':
                defence = self._get_defence_stats(position, li) # 18
            elif category == 'Discipline':
                discipline = self._get_discipline_stats(position, li) # 4
            elif category == 'Goalkeeping':
                goalkeeping = self._get_goalkeeping_stats(li) # 8
        if len(attack) < 1:
            attack = [None]*12
        elif len(goalkeeping) < 1:
            goalkeeping = [None]*8
        
        return attack + defence + teamplay + discipline + goalkeeping 

    def parse_player_htmls(self):
        player_array = [[]]
        j = -1
        total = len(os.listdir(self.str_dict['local player']))
        for filename in os.listdir(self.str_dict['local player']):
            j += 1
            file_path = Path(''.join([self.str_dict['local player'], filename]))
            if Path(''.join(['data/epl/ignore/', filename, '_', str(self.year)])).is_file():
                print(f'\nIGNORED {filename}\n')
                continue
            with open(file_path) as fp:
                soup = BeautifulSoup(fp, 'html.parser')
            '''
            # Club info
            club1 = soup.find_all('div', attrs={'class': 'wrapper hasFixedSidebar'})[0]
            print(club1)
            club2 = club1.find_all('dic', attrs={'class': 'label'})

            raise
            '''
            # Top banner
            name, number = filename.replace('_', ' '), None
            try: 
                name = soup.find_all('div', class_='playerDetails')[0].find_all('div', attrs={'class': 'name t-colour'})[0].getText()
            except:
                pass
            try:
                number = soup.find_all('div', class_='playerDetails')[0].find_all('div', attrs={'class': 'number t-colour'})[0].getText()
            except:
                pass
            position = self.list_df.loc[name]['Position']
            # 'Top' stats for season
            topStats = soup.find_all('div', attrs={'class': 'topStatList'})[0].find_all('div', attrs={'class': 'topStat'})
            appearances = topStats[0].find_all('span', attrs={'class':'allStatContainer statappearances'})[0].getText()
            wins = topStats[2].find_all('span', attrs={'class':'allStatContainer statwins'})[0].getText()
            losses = topStats[3].find_all('span', attrs={'class':'allStatContainer statlosses'})[0].getText()
            # Normal stats which are different for different positions
            normalStats = soup.find_all('ul', attrs={'class': 'normalStatList block-list-2 block-list-2-m block-list-padding'})[0] \
                              .find_all('li')
            player_row = [name, self.year, position, appearances, wins, losses, self.list_df.loc[name]['Nationality']]
            i, done = 0, False
            positions = ['Forward', 'Midfielder', 'Defender', 'Goalkeeper']
            _update_progress(j, total, f'********{filename}***************')
            
            while not done:
                try:
                    player_row.extend(self._get_stats(position, normalStats))
                    done = True
                except:
                    position = positions[i]
                    i+=1

                    f = open('data/epl/epl_players/2018/mismatch.txt', 'w')
                    f.write(f'{filename}\n')
                    f.close()
            player_array.append(player_row)
            
        player_array.pop(0)
        df = pd.DataFrame(np.array(player_array))\
            .rename(columns={0: 'Name', 1: 'Year', 2: 'Position', 3: 'Appearances', 4: 'Wins', 5: 'Losses', 6: 'Nationality',\
                            7: 'Goals', 8: 'Headed Goals', 9:'Right Footed Goals', 10:'Left Footed Goals', 11:'Hit Woodwork',\
                            12: 'Goals per Match', 13: 'Penalties Scored', 14: 'Freekicks Scored', 15: 'Shots', 16: 'Shots on Target',\
                            17: 'Shooting Accuracy', 18: 'Big Chances Missed',\
                            19: 'Tackles', 20: 'Blocked Shots', 21: 'Interceptions', 22: 'Clearances', 23: 'Headed Clearances', 24: 'Tackle Success',\
                            25: 'Recoveries', 26: 'Duels Won', 27: 'Duels Lost', 28: 'Successful 50/50s', 29: 'Aerials Battles Won',\
                            30: 'Aerial Battles Lost', 31: 'Clean Sheets', 32: 'Goals Conceded', 33: 'Own Goals', 34: 'Errors Lead to a Goal',\
                            35: 'Last Man Tackles', 36: 'Clearances Off the Line',\
                            37: 'Assists', 38: 'Passes', 39: 'Passes per Game',\
                            40: 'Big Chances', 41: 'Crosses', 42: 'Cross Accuracy', 43: 'Through Balls', 44: 'Accurate Long Balls',\
                            45: 'Goalie Goals', 46: 'Yellows', 47: 'Reds', 48: 'Fouls', 49: 'Offsides',\
                            50: 'Saves', 51: 'Penalties Saved', 52: 'Punches', 53: 'High claims', 54: 'Catches',\
                            55: 'Sweeper Clearances', 56: 'Throw Outs', 57: 'Goal Kicks'})
        csv_file_path = ''.join([self.str_dict['local year'], f'/{self.year}_df.csv'])
        if Path(csv_file_path).is_file():
            f = open(csv_file_path, "w+").close()
        df.to_csv(csv_file_path)

    def get_df(self, overwrite=False):
        csv_file_path = ''.join([self.str_dict['local year'], f'/{self.year}_df.csv'])

        if not Path(csv_file_path).is_file() or overwrite:
            self.parse_player_htmls()
        return pd.read_csv(csv_file_path)
    
    def execute_year_to_pandas(self, year):
        self.year = year
        self.write_list_html()
        self.parse_list_html_to_pandas(self.get_list_html())
        self.write_player_html()
        return self.get_df()

    def collect_all_names(self, dfs):
        names = []
        for df in dfs.values():
            for name in df['Name']:
                names.append(name)
        return names

    def contruct_master_df(self, start_year, stop_year, filter=False):
        df_master = pd.DataFrame()
        for year in range(start_year, stop_year+1):
            print(f'Scraping {year}')
            df = self.execute_year_to_pandas(year)
            if filter:
                df = df[df['Appearances']!=0]
            df_master = pd.concat([df_master, df])

        return df_master


class DataAnalyzer:
    def __init__(self, start_year, stop_year):
        self.df_master = PlayerScrapper().contruct_master_df(start_year, stop_year, filter=True)
    
    def _diversity_indiv(self):
        df_diversity = self.df_master.groupby(by='Year').count()['Name'].reset_index()\
            .rename(columns={'Name': 'Total Count'}).sort_values(by='Year')
        
        countries = list(self.df_master.groupby(by='Nationality').count()['Name'].reset_index()['Nationality'].to_numpy())
        country_dfs = [self.df_master.groupby(by=['Year', 'Nationality']).count()['Name'].reset_index()\
                .rename(columns={'Name': 'Count'}).sort_values(by='Nationality').set_index(['Nationality', 'Year'])\
                    .loc[country, :].rename(columns={'Count': f'{country} Prop'}).sort_values(by='Year') for country in countries]

        for df in country_dfs:
            df_diversity = pd.merge(df_diversity, df, on='Year', how='outer')
        df_diversity.fillna(0, inplace=True)
        cols = [f'{country} Prop' for country in countries]
        df_diversity.loc[:, cols] = df_diversity.loc[:, cols].div(df_diversity['Total Count'], axis=0)

        plt.style.use('cap1')
        fig, ax = plt.subplots()
        running_bottom = 0
        colors = [(np.random.rand()*0.5+0.25, np.random.rand()*0.5+0.25, np.random.rand()*0.5+0.25) for i in range(200)]
        ax.set_prop_cycle(cycler('color', colors))
        selected_legend = ['England', 'United States']
        for country in countries:
            label = None
            if country in selected_legend:
                label = country
                color = 'b'
                if country == 'United States':
                    color = 'r'
                ax.bar(df_diversity['Year'], df_diversity[f'{country} Prop'], width=0.75, bottom=running_bottom, color=color, label=label)
            else:
                ax.bar(df_diversity['Year'], df_diversity[f'{country} Prop'], width=0.75, bottom=running_bottom, label=label)

            running_bottom += df_diversity[f'{country} Prop']
        ax.legend(bbox_to_anchor=(1, 1))
        ax.set_ylim(0, 1.0)
        ax.set_yticks(np.arange(0, 1, 0.05))
        ax.set_xticks(np.arange(2006, 2019, 1))
        ax.set_xlabel('Year')
        ax.set_ylabel('Proportion of EPL')
        ax.title.set_text('Proportions of Nationalities in EPL Between 2006 and 2018')
        fig.show()

    def _which_continent(self, row):
        eu_countries = pd.read_csv('data/bin/listofeucountries.csv')
        latin_countries = pd.read_csv('data/bin/list-latin-american-countries.csv')
        north_countries = pd.read_csv('data/bin/list-north-american-countries.csv')
        african_countries = pd.read_csv('data/bin/list-african-countries.csv')
        asian_countries = pd.read_csv('data/bin/list-countries-asia.csv')
        continent_dfs = [eu_countries, latin_countries, north_countries, african_countries, asian_countries]
        map_idx = {0: 'Europe', 1: 'South America', 2: 'North America', 3: 'Africa', 4: 'Asia', 5: 'Other'}
        if row['Nationality']=="Cote D'Ivoire":
            return map_idx[3]
        for idx, continent_df in enumerate(continent_dfs):
            if continent_df['x'].isin([row['Nationality']]).any():
                return map_idx[idx]
        return map_idx[5]


    def _diversity_continent(self):
        continent_values = self.df_master.groupby(by=['Nationality', 'Year']).count()['Name'].reset_index()\
                            .rename(columns={'Name': 'Count'}).sort_values(by='Nationality').reset_index()[['Nationality', 'Year', 'Count']]
        continent_values['Continent'] = continent_values.apply(self._which_continent, axis=1)
        continent_values = continent_values.groupby(by=['Continent', 'Year']).sum()['Count'].reset_index().set_index(['Continent', 'Year'])

        df_diversity = self.df_master.groupby(by='Year').count()['Name'].reset_index()\
            .rename(columns={'Name': 'Total Count'}).sort_values(by='Year')

        continents = ['Europe', 'South America', 'North America', 'Africa', 'Asia', 'Other']
        continent_dfs = [continent_values.groupby(by=['Continent', 'Year']).sum()['Count'].reset_index().set_index(['Continent', 'Year'])\
                    .loc[continent, :].rename(columns={'Count': f'{continent} Prop'}).sort_values(by='Year') for continent in continents]

        for df in continent_dfs:
            df_diversity = pd.merge(df_diversity, df, on='Year')
        cols = [f'{continent} Prop' for continent in continents]
        df_diversity.loc[:, cols] = df_diversity.loc[:, cols].div(df_diversity['Total Count'], axis=0)

        plt.style.use('cap1')
        fig, ax = plt.subplots()
        ax.set_prop_cycle(cycler('color', ['b', 'g', 'r', 'k', 'y', 'm']))
        running_bottom = 0
        width = 0.75
        for continent in continents:
            y = df_diversity[f'{continent} Prop']
            rects = ax.bar(df_diversity['Year'], y, width=width, label=continent, bottom=running_bottom)
            running_bottom += y
            if continent == 'Europe':
                for rect in rects:
                    ax.text(rect.get_x()+0.03, rect.get_height()*0.9, str(round(y[int(rect.get_x()-2005)], 2)), color='orange', fontweight='bold')
        ax.legend(framealpha=0.8)
        ax.set_ylim(0, 1.0)
        ax.set_yticks(np.arange(0, 1, 0.05))
        ax.set_xticks(np.arange(2006, 2019, 1))
        ax.set_xlabel('Year')
        ax.set_ylabel('Proportion of EPL')
        ax.title.set_text('Proportions of Continents Represented in EPL Between 2006 and 2018')
        fig.show()

    def diversity(self):
        self._diversity_indiv()
        self._diversity_continent()
        
        
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