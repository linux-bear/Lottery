from openai import OpenAI
import pandas as pd
import urllib.request
import datetime
import colours as colour


def main():

    results_df = get_results()
    if results_df is False:
        print(f"{colour.LRED}Failed to get results, exiting")
        return
    
    print(results_df.head())

    results_df.columns = ["num1", "num2",  "num3",  "num4",  "num5", "xnum1",  "xnum2", "DrawNumber"]
    
    #get main only guess
    main_only = results_df.drop(columns = ["DrawNumber", "xnum1", "xnum2"])
    data_main = main_only.to_dict(orient='records')
    last_10_set_main = last_10_set(main_only)
    message = create_message(data_main, last_10_set_main, first=True)
    returned_numbers = get_ai_prediction(message)
    print(f"{colour.GREEN}Returned numbers are: \n{returned_numbers}")

    #get life only guess
    star_only = results_df.drop(columns = ["num1", "num2",  "num3",  "num4",  "num5", "DrawNumber"])
    last_10_set_star = last_10_set(star_only, type='star')
    data_star = star_only.to_dict(orient='records')
    message = create_message(data_star, last_10_set_star, first=False)
    star_returned_numbers = get_ai_prediction(message)
    print(f"{colour.GREEN}star returned numbers are: \n{star_returned_numbers}")
    print(f"{colour.GREEN}Main balls are: \n{returned_numbers}")




def get_results():

    output_df = None

    # columns_old = ["DrawDate", "Ball 1", "Ball 2",  "Ball 3",  "Ball 4",  "Ball 5",  "Lucky Star 1",  "Lucky Star 2", "DrawNumber"]
    # columns_new = ["DrawDate", "Ball 1", "Ball 2",  "Ball 3",  "Ball 4",  "Ball 5",  "Lucky Star 1",  "Lucky Star 2", "UK Millionaire Maker","DrawNumber"]
    
    ####pull old results from local file
    main_df = pd.read_csv('./euromillions.csv')

    #print(main_df.head())

    #rename Date column to DrawDate
    #main_df.rename(columns={"Date": "DrawDate"}, inplace=True)

        #set the date as the index
    main_df.set_index('Date',inplace=True)


    ##pull new results from national lottery website and store locally
    try:
        url = 'https://www.national-lottery.co.uk/results/euromillions/draw-history/csv'
        filename = './euromillions_new.csv'
        urllib.request.urlretrieve(url, filename)
        print(f"{colour.GREEN}New results retrieved successfully")

    except Exception as error:
        print(f"{colour.LRED}Error retrieving new results: {error}")
        return False
    
    new_df = pd.read_csv('./euromillions_new.csv')

    print(f"Length of new_df is: {len(new_df)}")
    #print(new_df.head())

    new_df.rename(columns={"DrawDate": "Date"}, inplace=True)

    new_df.set_index('Date',inplace=True)

    new_df.drop(columns = ["UK Millionaire Maker"], inplace=True)

        #create output_df, merged the two csvs
    output_df = pd.concat([main_df, new_df], axis=0, join = 'outer')
    output_df.index.name='Date'
    output_df.drop_duplicates(keep='first', inplace=True, ignore_index=False)
    output_df.sort_index(inplace = True, ascending = False)

    # update euromillions.csv with new results
    output_df.to_csv('./euromillions.csv', index=True)
    print(f"Updated euromillions.csv with latest results")

    # ####################testing only, remove when live#########################
    # #only for testing, comment out when live
    # output_df = main_df.copy()

    print(f"{colour.CYAN}{output_df.head(5)}")
    print(f"{colour.CYAN}{output_df.tail(5)}")

    print(f"{colour.GREEN}Populated results_df with {len(output_df)} results")

    return output_df



def last_10_set(results_df, type='main'):
    
    print(f"{colour.YELLOW}Analysing data...{colour.GREEN}")

    #get a set of the last 10 results and then pass it to the ai asking it to pick x many from that set
    last_10 = results_df.head(10)

    #get the numbers out and put them in a set. first declare the set
    last_10_set = set()
    if type == 'star':
        for index, row in last_10.iterrows():
            last_10_set.update({row['xnum1'], row['xnum2']})
    else:
        for index, row in last_10.iterrows():
            last_10_set.update({row['num1'], row['num2'], row['num3'], row['num4'], row['num5']})

    print(f"{colour.CYAN}Last 10 set of numbers is: \n{last_10_set}{colour.GREEN}")

    return last_10_set



def create_message(data, last_10_set, first=True):
    print(f"{colour.YELLOW}Creating message for AI...{colour.GREEN}")

    if first:
        content = f"Here is some JSON data:\n{data}\n\nPlease predict the next set of numbers. \
            However, you must include 3 of these numbers in your prediction: {last_10_set}. Two of them must be even. \
                return in json format same as presented."
        message = [
            {"role": "system", "content": "You are a data analyst that explains results clearly."},
            {"role": "user", "content": content}
        ]
    else:
        content = f"Here is some JSON data:\n{data}\n\nPlease predict the next set of numbers. \
            However, you must include one of these numbers in your prediction: {last_10_set}.  \
                return in json format same as presented"
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




