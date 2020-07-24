# **Capstone 1**
Analysis of Footballers

Capstone 1 Project for Galvanize Data Science Immersive

## **Topics**:
Various visualizations and analyses of English Premier League players from 2000-2018

## **Data Source**
I created the data set I used entirely by webscrapping. I encapsulated all methods and properties in the PlayerScrapper class.

The pipeline occurs in the following fashion:
### 1. **Club List**
    * This step provided the list of names and URLs to all the clubs competing in the EPL for that particular year
   
        1. Get HTML
            * Used Selenium with Chromedriver because the dropdown bar would not update with specific URL. 
            * Saved HTML to "data/epl/epl_clubs/year/year_epl_clubs.html"
            * Example of webpage: [Club List](https://www.premierleague.com/clubs?se=210)
        2. Parse Club List HTML
            * Used BeautifulSoup to extract club/url key/value pairs from local HTML file
            * Saved this information as a dictionary in a class variable to be accessed later
            
### 1. ***Club***
    * This step provided a player list for a club with Name, Position, and Nationality along with URLs to player page
    
    1. Get Club HTMLs
        * Used Selenium with Chromedriver because the dropdown bar would not update with specific URL.
        * Saved HTML to "data/epl/epl_clubs/year/clubs/club
        Example of webpage: [Club](https://www.premierleague.com/clubs/10/Liverpool/squad?se=210)
    1. Parse Club List HTML
        * Used BeautifulSoup 
1. Parse Club HTMLs

1. Write Player HTMLs

1. Parse Player HTMLs

1. Merge Dataframes

1. Iterate Pipeline over Year Range
## Data Description
1. Transfers: 20 teams over 19 years with 10+ transfers per team per year \n
1. Players: ~400 players per year over 19 years with 20+ metrics per player \n
1. Fixture results: All fixutre results over 19 years with matchday, date, home team, score, away team, notes
