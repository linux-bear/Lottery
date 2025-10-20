from openai import OpenAI
import pandas as pd
import urllib.request
import datetime
import setForLifeDataAnalysis

import colours as colour

def main():

    results_df = get_results()
    if results_df is False:
        print(f"{colour.LRED}Failed to get results, exiting")
        return
    
    #get main only guess
    main_only = results_df.drop(columns = ["limitedNum"])
    data_main = main_only.to_dict(orient='records')
    last_10_set_main = setForLifeDataAnalysis.last_10_set(main_only)
    message = create_message(data_main, last_10_set_main, first=True)
    returned_numbers = get_ai_prediction(message)
    print(f"{colour.GREEN}Returned numbers are: \n{returned_numbers}")

    #get life only guess
    life_only = results_df.drop(columns = ["Num1", "Num2", "Num3", "Num4", "Num5"])
    last_10_set_life = setForLifeDataAnalysis.last_10_set(life_only, type='life')
    data_life = life_only.to_dict(orient='records')
    message = create_message(data_life, last_10_set_life, first=False)
    life_returned_numbers = get_ai_prediction(message)
    print(f"{colour.GREEN}Life returned numbers are: \n{life_returned_numbers}")
    print(f"{colour.GREEN}Main balls are: \n{returned_numbers}")





def get_results():

    ###pull new results from national lottery website and store locally
    try:
        url = 'https://www.national-lottery.co.uk/results/set-for-life/draw-history/csv'
        filename = './setForLife_new.csv'
        urllib.request.urlretrieve(url, filename)
        print(f"{colour.GREEN}New results retrieved successfully")

    except Exception as error:
        print(f"{colour.LRED}Error retrieving new results: {error}")
        return False
    
    new_df = pd.read_csv('./setForLife_new.csv')

    print(f"Length of new_df is: {len(new_df)}")
    print(new_df.head())

    ####pull old results from local file
    main_df = pd.read_csv('./setForLife.csv')

    #rename column "Date" to "DrawDate" in main_df
    main_df.rename(columns={"Date": "DrawDate"}, inplace=True)

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
    output_df.to_csv('./setForLife.csv', index=True)
    print(f"Length of output_df is: {len(output_df)}")
    print(output_df.head())

    ####################testing only, remove when live#########################
    output_df = main_df.copy()                                                #
    ###########################################################################

    all_df = output_df.drop(columns = ["Ball Set", "Machine", "DrawNumber"])
    #print(f"{colour.GREEN}{all_df.head()}")

    print(all_df)
    all_df.columns = ["Num1", "Num2", "Num3", "Num4", "Num5", "limitedNum"]
    #print(f"{colour.CYAN}All columns renamed to standard format")


    print(f"{colour.CYAN}Main results dataframe, length is: {len(all_df)}:")
    # print(all_df.head())
    # print(all_df.tail())

    return all_df




def create_message(data, last_10_set, first=True):
    print(f"{colour.YELLOW}Creating message for AI...{colour.GREEN}")

    if first:
        content = f"Here is some JSON data:\n{data}\n\nPlease predict the next set of numbers for tomorrow's date. \
            However, you must include 3 of these numbers in your prediction: {last_10_set}. Two of them must be even. \
                return in json format same as presented."
        message = [
            {"role": "system", "content": "You are a data analyst that explains results clearly."},
            {"role": "user", "content": content}
        ]
    else:
        content = f"Here is some JSON data:\n{data}\n\nPlease predict the next limited number for tomorrow's date. \
            However, you must include one of these numbers in your prediction: {last_10_set}.  \
                return in json format"
        message = [
            {"role": "system", "content": "You are a data analyst that explains results clearly."},
            {"role": "user", "content": content}
        ]
    return message




def get_ai_prediction(message):

    client = OpenAI()

    print(f"{colour.YELLOW}Getting AI prediction...")

    response = client.chat.completions.create(
        model="gpt-5",
        messages=message,
    )

    returned_numbers = response.choices[0].message.content

    return returned_numbers



if __name__ == "__main__":

    print(f"{colour.YELLOW}Starting setForLife uber AI lottery ball picker")

    timeStart = datetime.datetime.now()

    main()

    timeEnd = datetime.datetime.now()
    
    print(f"{colour.YELLOW}Total time taken: {timeEnd - timeStart}")
    print(f"{colour.YELLOW}Ending setForLife uber AI lottery ball picker")
