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
    #print(f"{colour.GREEN}Returned numbers are: \n{returned_numbers}")

    #get life only guess
    life_only = results_df.drop(columns = ["Num1", "Num2", "Num3", "Num4", "Num5"])
    last_10_set_life = setForLifeDataAnalysis.last_10_set(life_only, type='life')
    data_life = life_only.to_dict(orient='records')
    message = create_message(data_life, last_10_set_life, first=False)
    life_returned_numbers = get_ai_prediction(message)

    #output results
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
    #new_df["DrawDate"] = pd.to_datetime(new_df["DrawDate"])

    #set the date as the index
    main_df.set_index('DrawDate',inplace=True)
    new_df.set_index('DrawDate',inplace=True)

    #### create output_df, merged the two csvs
    output_df = pd.concat([main_df, new_df], axis=0, join = 'outer')
    output_df.index.name='Date'
    output_df.drop_duplicates(keep='first', inplace=True, ignore_index=False)
    output_df.sort_index(inplace = True, ascending = False)

    # update setForLife.csv with new results
    output_df.to_csv('./setForLife.csv', index=True)
    print(f"Length of output_df is: {len(output_df)}")
    print(output_df.head())

    ####################testing only, remove when live#########################
    # output_df = main_df.copy()                                                #
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
        # MAIN BALLS
        content = content = f"""
We are doing a purely hypothetical, just-for-fun analysis of lottery draws.

Bucket definitions (inclusive ranges):
- bucket 1: numbers 0-9
- bucket 2: numbers 10-19
- bucket 3: numbers 20-29
- bucket 4: numbers 30-39
- bucket 5: numbers 40-47

You must obey **all** of the following:

1. Choose 5 distinct main numbers between 0 and 47 inclusive.
2. Each number must be assigned to **exactly one** bucket according to these ranges.
   - Example: 17 is in bucket 2 because 10 ≤ 17 ≤ 19.
   - Example: 25 is in bucket 3 because 20 ≤ 25 ≤ 29.
3. The final bucket counts must be [2,1,1,1,0] in some order:
   - Exactly one bucket has 2 numbers.
   - Exactly three buckets have 1 number each.
   - Exactly one bucket has 0 numbers.
4. Before you answer, mentally check each number against its bucket range.
   Do NOT say a number is in a bucket if its value is outside that bucket's range.

Return **only** a JSON object:

{{
  "main_numbers": [n1, n2, n3, n4, n5],
  "buckets": {{"n1": b1, "n2": b2, "n3": b3, "n4": b4, "n5": b5}},
  "reasoning": "very short explanation"
}}

Here is the JSON data with past draws:
{data}
"""
        message = [
            {
                "role": "system",
                "content": (
                    "You are a careful data analyst. "
                    "You must strictly follow the user's instructions and must not use "
                    "historical_frequency_mode or any frequency-only strategy."
                ),
            },
            {"role": "user", "content": content},
        ]

    else:
        # LIFE BALL
        content = f"""
We are doing a purely hypothetical, just-for-fun analysis of lottery draws.
Do NOT use any kind of "historical_frequency_mode" or simple frequency-based picking strategy.

This JSON data contains only the limited (life) numbers from past draws.

1. Treat this as a random game. Do not claim that the method actually predicts the future.
2. For each possible limited (life) number:
   - Compute how many draws ago it last appeared (recency / "overdue" measure).
   - Focus on numbers that have not appeared for the longest time ("overdue" numbers).
3. Choose ONE limited (life) number for a hypothetical next draw:
   - It should be chosen from among the most overdue numbers if there is one number that is significantly more overdue than the others
   - else it should be chosen from {last_10_set}, and choose the most likely to come up by patterns not by overdue numbers
4. Return ONLY a JSON object with this structure and nothing else:

{{
  "life_number": n,
  "reasoning": "short explanation of how the overdue rule was applied"
}}

Here is the JSON data with past draws:
{data}
"""
        message = [
            {
                "role": "system",
                "content": (
                    "You are a careful data analyst. "
                    "You must strictly follow the user's instructions and must not use "
                    "historical_frequency_mode or any frequency-only strategy."
                ),
            },
            {"role": "user", "content": content},
        ]

    return message


# def create_message(data, last_10_set, first=True):
#     print(f"{colour.YELLOW}Creating message for AI...{colour.GREEN}")

#     if first:
#         content = f"Here is some JSON data:\n{data}\n\nPlease predict the next set of numbers for tomorrow's date. \
#             However, you must include 3 of these numbers in your prediction: {last_10_set}. Two of them must be even. \
#                 return in json format same as presented."
#         message = [
#             {"role": "system", "content": "You are a data analyst that explains results clearly."},
#             {"role": "user", "content": content}
#         ]
#     else:
#         content = f"Here is some JSON data:\n{data}\n\nPlease predict the next limited number for tomorrow's date. \
#             However, you must include one of these numbers in your prediction: {last_10_set}.  \
#                 return in json format"
#         message = [
#             {"role": "system", "content": "You are a data analyst that explains results clearly."},
#             {"role": "user", "content": content}
#         ]
#     return message




def get_ai_prediction(message):

    client = OpenAI()

    print(f"{colour.YELLOW}Getting AI prediction...")

    response = client.chat.completions.create(
        model="gpt-5.2",
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
