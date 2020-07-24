from WebScrapper import *

if __name__ == "__main__":
    analyzer = DataAnalyzer(2006, 2018)
    # analyzer.diversity(kind='both')
    analyzer.goal_t_test() #inclusive on both boundaries