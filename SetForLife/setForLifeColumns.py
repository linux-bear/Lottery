from openai import OpenAI
import pandas as pd
import datetime


import colours as colour

def main():

    dataframe_csv = pull_numbers_from_csv('./setForLife_dataForAI.csv')

    one_list_to_rule_them_all = create_lists(dataframe_csv)

    print(f"length of one_list_to_rule_them_all is: {len(one_list_to_rule_them_all)}")

    returned_numlist = []
    for numList in one_list_to_rule_them_all:
        last_10_set = create_last_10_set(numList)
        message = create_message(numList, last_10_set)
        #print(message)
        returned_number = get_ai_prediction(message)
        print(f"{colour.GREEN}Returned number is: \n{returned_number}")
        returned_numlist.append(returned_number)

    print(f"{colour.GREEN}All returned numbers are: \n{returned_numlist}")


def pull_numbers_from_csv(filename):
    df = pd.read_csv(filename)
    print(f"{colour.CYAN}Data from {filename}:\n{df.head()}{colour.GREEN}")
    return df


def create_lists(dataframe_csv):
    list1 = dataframe_csv['num1'].tolist()
    list2 = dataframe_csv['num2'].tolist()
    list3 = dataframe_csv['num3'].tolist()
    list4 = dataframe_csv['num4'].tolist()
    list5 = dataframe_csv['num5'].tolist()
    lifeList = dataframe_csv['life'].tolist()

    one_list_to_rule_them_all = [list1, list2 ,list3, list4, list5, lifeList]
    
    return one_list_to_rule_them_all


def create_last_10_set(numlist):
    last_10_set = set()
    last_10 = numlist[:10]
    last_10_set.update(last_10)
    #print(f"{colour.CYAN}Last 10 set of numbers is: \n{last_10_set}{colour.GREEN}")
    return last_10_set


def create_message(data, last_10_set):
    print(f"{colour.YELLOW}Creating message for AI...{colour.GREEN}")

    content = f"""
We are doing a purely hypothetical, just-for-fun analysis of lottery draws.
Do NOT use any kind of "historical_frequency_mode" or any strategy based purely on overall frequency.

You are given the historical values for a single lottery position as a list.
Assume the list is ordered from most recent draw to oldest:

History (most recent first):
{data}

Also given is the set of values that appeared in the last 10 draws:
{last_10_set}

Follow these rules:

1. Treat this as a random game. Do not claim that this method truly predicts the future.

2. For each distinct number in the history:
   - Think about how many draws ago it last appeared (a recency / "overdue" measure).
   - Consider numbers that have not appeared for the longest time as more "overdue".

3. Use a combination of:
   - Overdue behaviour (numbers that have not appeared recently).
   - Clustering in randomness:
     - Prefer numbers that are close in value to several numbers in the recent set {last_10_set},
       for example within ±2 or ±3 of them.

4. Choose exactly ONE number for a hypothetical next draw that:
   - Is reasonably overdue (has not appeared in many draws), and
   - Also fits into a local cluster around the recent numbers where possible.

5. Output format:
   - Return ONLY the chosen number as a bare integer (e.g. 23).
   - Do NOT include any explanation, JSON, text, quotes, or extra characters.
"""

    returned = [
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

    return returned


# def create_message(data, last_10_set):
#     print(f"{colour.YELLOW}Creating message for AI...{colour.GREEN}")
#     returned = []


#     content = f"Here is a list of data:\n{data}\n\nPlease predict the next number. Just return only the number as an int and no other text."
#     returned = [
#         {"role": "system", "content": "You are a data analyst that explains results clearly."},
#         {"role": "user", "content": content}
#     ]

#     return returned




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