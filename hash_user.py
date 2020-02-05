import os
import pandas as pd
import time
from hash_with_eqi_prob import hash_equi_prob
from datetime import datetime, timedelta
import time_series
from concat_csv import *

def sort_list_based_len(x):
    out = [[] for i in range(len(x))]
    s = [0 for i in range(len(x))]
    for i in range(len(x)):
        s[i] = len(x[i])
    ind = sorted(range(len(s)), key=lambda k: s[k])
    ind = list(reversed(ind))
    for i in (range(len(ind))):
        out[i] = x[ind[i]]
    return out

def get_num_good_usr(x,th):
    x2 = list(set(x))
    out = []
    for i in range (len(x2)):
        c = x.count(x2[i])
        if(c > th):
            out.append(x2[i])
    return out

def find_suspicious_user(df,
                         out_dir,
                         window_size=2*3600,
                         interval=1,
                         activity_th_for_hash=2,
                         shifting_times = 40,
                         modul = 5000,
                         sigma=0.024,
                         good_user_th=5,
                         good_bin_th=5):
    '''
    This corresponds to the indexer part of DeBot (step_2.py). The main
    difference is that random projection will be perform only if the
    author count exceeds 150. This threshold is given by experiment. This
    is because the hashing is time-consuming, and may take more time than
    computing DTW between all the authors without hashing them.
     - df : a dataframe containing 2 columns :
         - author_id : the id of the author of the tweet
         - created : time of creation of the tweet (datetime.datetime)
       with as index the sorted created_at column
     - out_dir : path of a directory where to store the suspicious users.
     - window_size : the window size (in seconds) we use to compare authors
       between them. According to DeBot, the default value is 2 hours.
     - interval : the interval (in seconds) between two values in the time
       series.
     - activity_th_for_hash : threshold of tweet count for a given author,
       under which we filter out the author. Note that the default value
       is low because we don't have the entire timeline of the users yet.
     - shifting times : Shows the number of copies we have from each users
       in our buckets (DeBot)
     - modul : number of buckets (DeBot)
     - sigma : standard deviation for equip_probable function (DeBot)
     - good_user_th : How many copies a user should have to be picked in a bin
       (default 5). Strict comparison (x > good_user_th) (DeBot)
     - good_bin_th : How many suspicious users a bin should have to be picked
       (default 5) strict comparison (x > good_bin_th) (DeBot)
    The suspicious users are reported as a list for each time window, in
    a dataframe with two columns
     - time_window : the start of the time window where the users are
       suspicious
     - suspicious_users : a list of suspicious users, according to random
       projection. They may not be bot, but were hashed into the same
       bucket and thus are suspicious.
    The dataframe is stored on disk in the given location. Intermediate
    csv files are also stored, such that if for some reason the computation
    stop, we can relaunch from the last date saved on disk.
    '''

    # the first date
    start_date = df.iloc[0].created_at
    # the last date
    final_date = df.iloc[-1].created_at
    # the start date of the current window
    start_window = start_date
    # will be used to save the results on disk regularly
    base_time = time.time()
    # will be used to print the progress
    last_time = start_window - timedelta(days=31)
    # current index of the partial results to save on disk
    idx_out = 0
    # wrapper to compute time series
    TS = time_series.TimeSeries(interval=interval)
    # rows that will contain the suspicious users
    rows = []

    # Iterate over all windows
    while start_window + timedelta(seconds=window_size) <= final_date:
        if start_window > last_time + timedelta(days=30):
            print(start_window)
            last_time = start_window

        end_window = start_window + timedelta(seconds=window_size)

        # Keep the tweets corresponding to the window
        df_window = df.loc[start_window:end_window]

        # For each author_id, get the activity (list of datetime)
        df_window = (df_window.groupby('author_id')['created_at']
                                                    .apply(list)
                                                    .reset_index(name='activity'))
        # Compute how much tweet each author created
        df_window["count"] = df_window['activity'].apply(len)
        # Filter out all authors with low activity
        df_window = df_window[df_window["count"]>= activity_th_for_hash]
        # Convert each activity (list of datetime) into a non-normalized time series
        # (list of int)
        df_window["ts"] = df_window['activity'].apply(lambda x:
                                TS.ts_from_datetime(x, start_window, end_window))

        # Hash users into buckets using Debot hashing technique
        ts_list = list(df_window.ts)
        if len(ts_list) > 1:
            test_time = time.time()
            bucket_user = hash_equi_prob(ts_list, modul, shifting_times, sigma)

            author_id_list = list(df_window.author_id)

            to_report = set()
            # From experiment, it will be faster and more accurate
            # to compute the warped correlation for all authors in
            # the time window without doing the hashing part if
            # the count of author is less than 150
            if len(author_id_list) > 150:
                #Find the set of suspicious users in the bucket
                good_bin = 0
                bucket_user = sort_list_based_len(bucket_user)
                for i in range (len(bucket_user)):
                    cur_good_user = get_num_good_usr(bucket_user[i],good_user_th)
                    if (len(cur_good_user) > good_bin_th):
                        good_bin = good_bin + 1
                        for j in range (len(cur_good_user)):
                            cur_id = author_id_list[cur_good_user[j]]
                            to_report.add(cur_id)
            else:
                to_report = to_report.union(set(author_id_list))

            if len(to_report) > 1:
                rows.append([start_window, to_report])

            # Save the suspicious users
            if time.time() > base_time + 300:
                if len(rows) > 0:
                    df_suspicious = pd.DataFrame(rows, columns=['time_window', 'suspicious_users'])
                    df_suspicious.to_csv(os.path.join(out_dir, "out_hash_" + str(idx_out) + ".csv"),
                                  index=False,
                                  encoding='utf-8')
                    print("saved until " + str(start_window))
                    rows = []
                    idx_out += 1
                base_time = time.time()

        # Update start_window
        start_window = end_window

    # Save the remaining users
    df_suspicious = pd.DataFrame(rows, columns=['time_window', 'suspicious_users'])
    df_suspicious.to_csv(os.path.join(out_dir, "out_hash_" + str(idx_out) + ".csv"),
                  index=False,
                  encoding='utf-8')

    # Concatenate the partial results
    concat_csv(out_dir, "out_hash_", os.path.join(out_dir, "out_hash.csv"))
