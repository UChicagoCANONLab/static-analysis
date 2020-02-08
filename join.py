# Zack Crenshaw

# Used to join all csvs containing a key term


import sys
import pandas as pd
import os


# python3 join.py name_of_data_folder name_of_output_file


def join(input,output):
    df = None
    join_df = None
    for filename in os.listdir(input):
        path = input + filename
        if filename.endswith(".csv"):
            if df is None:
                df = pd.read_csv(path)
                x_suff = filename.split("_")[0]
            else:
                join_df = pd.read_csv(path)
                y_suff = filename.split("_")[0]
                df = df.merge(join_df,how='outer',on="Student ID",suffixes=("",y_suff))

    df.to_csv(output)







if __name__ == '__main__':
    join(sys.argv[1], sys.argv[2])