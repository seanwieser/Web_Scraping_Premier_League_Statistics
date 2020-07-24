# **Capstone 1**
Analysis of Footballers

Capstone 1 Project for Galvanize Data Science Immersive

## **Topics**:
Various visualizations and analyses of English Premier League players from 2000-2018
___
## **Data Collection and Organization**

I created the data set I used entirely by webscrapping. I encapsulated all methods and properties in the PlayerScrapper class.

The pipeline occurs in the following fashion:
### 1. Club List
* This step provided the list of names and URLs to all the clubs competing in the EPL for that particular year

    1. Get Club List HTML
        * Used Selenium with Chromedriver because the dropdown bar would not update with specific URL. 
        * Saved HTML to "data/epl/epl_clubs/year/year_epl_clubs.html"
        * Example of webpage: [Club List](https://www.premierleague.com/clubs?se=210)
    2. Parse Club List HTML
        * Used BeautifulSoup to extract club/url key/value pairs from local HTML file
        * Saved this information as a dictionary in a class variable to be accessed later
            
### 1. Club
* This step provided a player list and URLS for each of the twenty clubs competing in the EPL for that particular year
* Created a Pandas Dataframe with Name, Year, Position, and Nationality and wrote it to a CSV file
    
    1. Get Club HTMLs
        * Used Selenium with Chromedriver because the dropdown bar would not update with specific URL.
        * Saved HTMLs to "data/epl/epl_clubs/year/clubs/club"
        * Example of webpage: [Club](https://www.premierleague.com/clubs/10/Liverpool/squad?se=210)
    1. Parse Club HTMLs
        * Used BeautifulSoup to extract player/url key/value pairs from local HTML file
        * Saved this information as a dictionary in a class variable to be accessed later
        * Constructed Pandas Dataframe with information below and wrote it to a CSV file
            * Name, Year, Club, Position, Nationality
            
### 1. Player
* This step provided statistics about an individual player for a particular year
* Created a Pandas Dataframe with 58 columns and wrote it to a CSV file
    
    1. Get Player HTMLs
        * Used Selenium with Chromedriver because the dropdown bar would not update with specific URL.
        * Saved HTMLs to "data/epl/epl_players/year/players/player"
        * Example of player webpages: 
            * [Goalkeeper](https://www.premierleague.com/players/4664/Hugo-Lloris/stats?co=1&se=210)
            * [Defender](https://www.premierleague.com/players/5140/Virgil-van-Dijk/stats?co=1&se=210)
            * [Midfielder](https://www.premierleague.com/players/3920/Paul-Pogba/stats?co=1&se=210)
            * [Forward](https://www.premierleague.com/players/4328/Sergio-Ag%C3%BCero/stats?co=1&se=210)
    1. Parse Player HTMLs
        * Used BeautifulSoup to extract all appropriate statistics from local HTML file
        * Put this information into a Pandas Dataframe then wrote the dataframe to a CSV file

### 1. Merge Dataframes
* For a particular year, I now had two Pandas Dataframes that needed to be merged. 
    1. Club level dataframe with 4 columns
    2. Player level dataframe with 58 columns
        * Merged on Name, Year, Position, Nationality

### 1. Iterate Pipeline over Year Range
* Iterate Steps 1-4 from 2006 to 2018 concatenating each resulting dataframe
    * This is the annual range that had consistent statistics fields for players

## **Data Description**
* Resulting dataframe: 7473 rows x 59 columns
    * Using only a subset of the dataframe where player made an appearance that year: 4750 rows x 59 columns
    
* Columns:
    1.  Global:
        * 'Name', 'Year', 'Club', 'Position', 'Appearances', 'Wins', 'Losses', 'Nationality'
    1. Attack
        * 'Goals', 'Headed Goals', 'Right Footed Goals', 'Left Footed Goals', 'Hit Woodwork', 'Goals per Match', 'Penalties Scored', 'Freekicks Scored', 'Shots', 'Shots on Target', 'Shooting Accuracy', 'Big Chances Missed'
    1. Defence
        * 'Tackles', 'Blocked Shots', 'Interceptions', 'Clearances', 'Headed Clearances', 'Tackle Success', 'Recoveries', 'Duels Won', 'Duels Lost', 'Successful 50/50s', 'Aerials Battles Won', 'Aerial Battles Lost', 'Clean Sheets', 'Goals Conceded', 'Own Goals', 'Errors Lead to a Goal', 'Last Man Tackles', 'Clearances Off the Line'
    1. Team Play
        * 'Assists', 'Passes', 'Passes per Game', 'Big Chances', 'Crosses', 'Cross Accuracy', 'Through Balls', 'Accurate Long Balls'
    1. Discipline
        * 'Yellows', 'Reds', 'Fouls', 'Offsides'
    1. Goalkeeping
        * 'Goalie Goals', 'Saves', 'Penalties Saved', 'Punches', 'High claims', 'Catches', 'Sweeper Clearances', 'Throw Outs', 'Goal Kicks'
___

## **Data Visualization and Analyses**

### Diversity of Nationality in EPL
![alt text](https://github.com/seanwieser/capstone_1/blob/master/images/diversity_indiv.png "Individual Countries")
![alt text](https://github.com/seanwieser/capstone_1/blob/master/images/diversity_continent.png "Continents")
![alt text](https://github.com/seanwieser/capstone_1/blob/master/images/assist_goal_forward_mid_10.png)



