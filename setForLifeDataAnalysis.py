import pandas as pd
import colours as colour

def last_10_set(results_df, type='main'):
    
    print(f"{colour.YELLOW}Analysing data...{colour.GREEN}")

    #get a set of the last 10 results and then pass it to the ai asking it to pick 3 from this set
    last_10 = results_df.head(10)
    #print(f"{colour.CYAN}Last 10 results are:{last_10}")

    #get the numbers out and put them in a set. first declare the set
    last_10_set = set()
    if type == 'life':
        for index, row in last_10.iterrows():
            last_10_set.add(row['limitedNum'])
    else:
        for index, row in last_10.iterrows():
            last_10_set.update({row['Num1'], row['Num2'], row['Num3'], row['Num4'], row['Num5']})

    print(f"{colour.CYAN}Last 10 set of numbers is: \n{last_10_set}{colour.GREEN}")

    return last_10_set
