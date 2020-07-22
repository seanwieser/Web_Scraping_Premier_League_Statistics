from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import urllib.request
import time
import unicodedata
import os
import sys

def _update_progress(count, total, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush()  # As suggested by Rom Ruben

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

    def parse_list_html(self, html):
        with open(self.str_dict['local list']) as fp:
            soup = BeautifulSoup(fp, 'html.parser')
        info = [[],[],[], {}]
        rows = soup.findAll('tr')
        for idx in range(1, len(rows)):
            contents = rows[idx].findAll('td')
            if len(contents[0])<1 or len(contents[1])<1 or len(contents[2])<1:
                print(f'Ignoring {idx} in year {self.year}')
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
        for filename in os.listdir(self.str_dict['local player']):
            j += 1
            file_path = Path(''.join([self.str_dict['local player'], filename]))
            with open('data/epl/ignore/ignored.html') as ignore_file:
                if Path(''.join(['data/epl/ignore/', filename, '_', str(self.year)])).is_file():
                    print(f'$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\tIGNORED {filename}')
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
            name = soup.find_all('div', class_='playerDetails')[0].find_all('div', attrs={'class': 'name t-colour'})[0].getText()
            number = soup.find_all('div', class_='playerDetails')[0].find_all('div', attrs={'class': 'number t-colour'})
            if len(number) > 0:
                number = number[0].getText()
            else:
                number = None
            position = self.list_df.loc[name]['Position']
            # 'Top' stats for season
            topStats = soup.find_all('div', attrs={'class': 'topStatList'})[0].find_all('div', attrs={'class': 'topStat'})
            appearances = topStats[0].find_all('span', attrs={'class':'allStatContainer statappearances'})[0].getText()
            wins = topStats[2].find_all('span', attrs={'class':'allStatContainer statwins'})[0].getText()
            losses = topStats[3].find_all('span', attrs={'class':'allStatContainer statlosses'})[0].getText()
            goals = 0
            cleans = None
            if position == 'Goalkeeper':
                cleans = topStats[1].find_all('span', attrs={'class':'allStatContainer statclean_sheet'})[0].getText()
            else:
                goals = topStats[1].find_all('span', attrs={'class':'allStatContainer statgoals'})[0].getText()

            # Normal stats which are different for different positions
            normalStats = soup.find_all('ul', attrs={'class': 'normalStatList block-list-2 block-list-2-m block-list-padding'})[0] \
                              .find_all('li')
            player_row = []
            i, done = 0, False
            positions = ['Forward', 'Midfielder', 'Defender', 'Goalkeeper']
            _update_progress(j, 888)
            while not done:
                try:
                    player_row = self._get_stats(position, normalStats)
                    done = True
                except:
                    position = positions[i]
                    i+=1

                    f = open('data/epl/epl_players/2018/mismatch.txt', 'w')
                    f.write(f'{filename}\n')
                    f.close()    
            player_array.append(player_row)
            
        #.transpose().rename(columns={0: 'Name', 1: 'Position', 2: 'Nationality'})
        # player_array = np.array(player_array)
        player_array.pop(0)
        df = pd.DataFrame(np.array(player_array))\
            .rename(columns={0: 'Goals', 1: 'Headed Goals', 2:'Right Footed Goals', 3:'Left Footed Goals', 4:'Hit Woodwork', 
                            5: 'Goals per Game', 6: 'Penalties', 7: 'Freekicks', 8: 'Shots', 9: 'Shots on Target', 10: 'Shooting Accuracy',\
                            11: 'Big Chances Missed',\
                            12: 'Tackles', 13: 'Blocked Shots', 14: 'Interceptions', 15: 'Clearances', 16: 'Headed Clearances', 17: 'Tackle Success',\
                            18: 'Recoveries', 19: 'Duels Won', 20: 'Duels Lost', 21: 'Success 5050', 22: 'Aerials Won', 23: 'Aerial Lost',\
                            24: 'Clean Sheets', 25: 'Goals Conceded', 26: 'Own Goals', 27: 'Errors Lead to a Goal', 28: 'Last Man Tackles',\
                            29: 'Clearances Off the Line',\
                            30: 'Assists', 31: 'Passes', 32: 'Passes per Game',\
                            33: 'Big Chances', 34: 'Crosses', 35: 'Cross Accuracy', 36: 'Through Balls', 37: 'Accurate Long Balls',\
                            38: 'Yellows', 39: 'Reds', 40: 'Fouls', 41: 'Offsides',\
                            42: 'Goalie Goals', 43: 'Saves', 44: 'Penalties Saved', 45: 'Punches', 46: 'High claims', 47: 'Catches',\
                            48: 'Sweeper Clearances', 49: 'Throw Outs', 50: 'Goal Kicks'})
        print(df.head(100))

    def execute_year(self, year):
        self.year = year
        self.write_list_html()
        self.parse_list_html(self.get_list_html())
        self.write_player_html()
        players_df = self.parse_player_htmls()

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