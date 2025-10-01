from openai import OpenAI
import pandas as pd
import collections
import numpy
import urllib.request
import json
import datetime

NC='\033[0m'       # No Color / reset

# Regular Colors
BLACK='\033[0;30m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
PINK='\033[38;5;205m'
SOFT_PINK='\033[38;5;219m'

LSOFT_PINK='\033[1;38;5;219m'
LBLACK='\033[1;30m'
LRED='\033[1;31m'
LGREEN='\033[1;32m'
LYELLOW='\033[1;33m'
LBLUE='\033[1;34m'
LPURPLE='\033[1;35m'
LCYAN='\033[1;36m'
LWHITE='\033[1;37m'
LPINK='\033[1;38;5;205m'

def main():

    results_df = get_results()
    if results_df is False:
        print(f"{LRED}Failed to get results, exiting")
        return
    
    data = results_df.to_dict(orient='records')

    message = create_message(data, first=True)

    returned_numbers = get_ai_prediction(message)
    print(f"{GREEN}Returned numbers are: {returned_numbers}")

    message = create_message(returned_numbers, first=False)

    final_numbers = get_ai_prediction(message)
    print(f"{GREEN}Final predicted numbers are: {final_numbers}")
    



def get_results():

    #pull new results from national lottery website and store locally
    try:
        url = 'https://www.national-lottery.co.uk/results/set-for-life/draw-history/csv'
        filename = './setForLife_new.csv'
        urllib.request.urlretrieve(url, filename)
        print(f"{GREEN}New results retrieved successfully")

    except Exception as error:
        print(f"{LRED}Error retrieving new results: {error}")
        return False
    
    new_df = pd.read_csv('./setForLife_new.csv')

    print(f"Length of new_df is: {len(new_df)}")
    print(new_df.head())

    #pull old results from local file
    main_df = pd.read_csv('./setForLife.csv')

    main_df["DrawDate"] = pd.to_datetime(main_df["DrawDate"])
    new_df["DrawDate"] = pd.to_datetime(new_df["DrawDate"])

    #set the date as the index
    main_df.set_index('DrawDate',inplace=True)
    new_df.set_index('DrawDate',inplace=True)

    #create output_df, merged the two csvs
    output_df = pd.concat([main_df, new_df], axis=0, join = 'outer')
    output_df.index.name='Date'
    output_df.drop_duplicates(keep='first', inplace=True, ignore_index=False)
    output_df.sort_index(inplace = True, ascending = False)

    # update setForLife.csv with new results
    output_df.to_csv('../setForLife.csv', index=True)
    print(f"Length of output_df is: {len(output_df)}")
    print(output_df.head())

    ####################testing only, remove when live#########################
    #output_df = main_df.copy()                                                #
    ###########################################################################

    all_df = output_df.drop(columns = ["Ball Set", "Machine", "DrawNumber"])
    all_df.columns = ["DrawDate", "Num1", "Num2", "Num3", "Num4", "Num5", "limitedNum"]


    print(f"{CYAN}Main results dataframe, length is: {len(all_df)}:")
    print(all_df.head())
    print(all_df.tail())

    return all_df



def create_message(data, first=True):

    if first:
        message = [
            {"role": "system", "content": "You are a data analyst that explains results clearly."},
            {"role": "user", "content": f"Here is some JSON data:\n{data}\n\nPlease predict the next set of numbers for today's date. return in json format same as presented. Please return 10 sets of possibilities"}
        ]
    else:
        message = [
            {"role": "system", "content": "You are a data analyst that explains results clearly."},
            {"role": "user", "content": f"Here is some JSON data:\n{data}\n\nThese are predictions for a number set. Please run a regression analysis on the data and predict the most likely predicted set."}
        ]

    return message




def get_ai_prediction(message):

    client = OpenAI()

    print(f"{YELLOW}Getting AI prediction...")

    response = client.chat.completions.create(
        model="gpt-5",
        messages=message,
    )

    returned_numbers = response.choices[0].message.content

    return returned_numbers



if __name__ == "__main__":

    print(f"{YELLOW}Starting setForLife uber AI lottery ball picker")

    timeStart = datetime.datetime.now()

    main()

    timeEnd = datetime.datetime.now()
    
    print(f"{YELLOW}Total time taken: {timeEnd - timeStart}")
    print(f"{YELLOW}Ending setForLife uber AI lottery ball picker")
