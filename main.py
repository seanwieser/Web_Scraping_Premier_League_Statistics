from WebScrapper import *

if __name__ == "__main__":
    analyzer = DataAnalyzer(2006, 2018) #inclusive on both boundaries
    # analyzer.plot_multi_scatter(['Forward', 'Midfielder'], 'Goals', 'Assists')
    # analyzer.plot_multi_scatter(['Forward', 'Midfielder'], 'Passes per Game', 'Assists')

    # analyzer.print_df()
    analyzer.diversity(kind='both')
    # analyzer.goal_t_test() 