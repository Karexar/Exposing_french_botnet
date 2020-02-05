import os
import pandas as pd
import time
from datetime import datetime, timedelta
import time_series
from concat_csv import *
from correlation.dtw_wrapper.dtw_wrapper import *

def find_correlated_activity(df,
                             in_path,
                             out_dir,
                             window_size=2*3600,
                             interval=1,
                             allowable_lag=20,
                             activity_th_for_dtw=10,
                             report_threshold=0.995,
                             use_shift=False,
                             fetch_timelines=False,
                             since_id=None,
                             max_id=None):
    '''
    Iterate over all time window and compute dtw between authors
    in each time window. Each author must have a minimum amount at least
    of tweets during the time window to compute the DTW.
    Report the account whose warped correlation is over report_threshold
    and store it in a csv file containing 3 columns :
     - author_id_x
     - author_id_y
     - warp_corr : warped correlation between the two authors
     - window : start of time window
    No duplicates. If author_id_x = X and author_id_y = Y in a row, there
    will not be author_id_x = Y and author_id_y = X in some other row.
    Parameters :
     - df : a dataframe containing 2 columns :
         - author_id : the id of the author of the tweet
         - created : time of creation of the tweet (datetime.datetime)
       with as index the sorted created_at column
       The dataframe should contain the complete timeline for all users.
     - in_path : the path to the csv file containing the suspicious user.
       The csv is created by the find_suspicious_user function.
       If None, then the warped correlation will be computed between each
       author for each time window
     - out_dir : the path to the output directory
     - window_size : the window size (in seconds) we use to compare authors
       between them. According to DeBot, the default value is 2 hours.
     - interval : the interval (in seconds) between two values in the time
       series.
     - allowable_lag : the maximum shift (in seconds) allowed to match two
       tweets from two different authors.
     - activity_th_for_dtw : the minimum amount of tweet a user must have
       to be candidate for dtw computation. We use 10 by default, as DeBot.
     - use_shift : when computing DTW, if set to true, we will shift one
       time series such that it matches better the other time series. If
       this is set to True, we should use a lower allowable lag, otherwise
       we may have false positives.
    '''
    # Create the correlation dataframe
    df_corr = pd.DataFrame(columns=['author_id_x', 'author_id_y', 'warp_corr', 'window'])
    # will be use to save the results on disk regularly
    base_time = time.time()
    # the first date
    start_date = df.iloc[0].created_at
    # the last date
    end_date = df.iloc[-1].created_at
    # the start date of the current window
    start_window = start_date
    # wrapper to compute time series
    TS = time_series.TimeSeries(interval=interval)
    # current index of the partial results to save on disk
    idx_out = 0
    # create the suspicious user dataframe
    df_suspicious = None
    if in_path is not None:
        df_suspicious = pd.read_csv(in_path,
                                    encoding='utf-8',
                                    engine='python',
                                    index_col="time_window")

    last_time = start_window - timedelta(days=31)

    # Iterate over all windows
    while start_window + timedelta(seconds=window_size) <= end_date:
        # Print the start window every month to give the progress
        if start_window > last_time + timedelta(days=30):
            print(start_window)
            last_time = start_window
        end_window = start_window + timedelta(seconds=window_size)


        # Keep only tweets in the current time window
        df_window = df.loc[start_window:end_window]

        # Filter out authors that are not suspicious
        if df_suspicious is not None and start_window in df_suspicious.index:
            susp_authors = df_suspicious.loc[start_window]["suspicious_authors"]
            df_window = df_window[df_window.author_id.isin(susp_authors)]

        if df_suspicious is None or start_window in df_suspicious.index:
            # Group tweets by authors
            df_grouped = (df_window.groupby('author_id')['created_at']
                                  .apply(list)
                                  .reset_index(name='activity'))

            # Keep only authors who have enough tweets during this time window
            df_grouped["count"] = df_grouped.activity.apply(len)
            df_filtered = df_grouped[df_grouped["count"] >= activity_th_for_dtw].copy()
            authors_kept = set(df_filtered["author_id"])

            # If there is at least two authors remaining, compute DTW between
            # all of them
            if df_filtered.shape[0] > 1:
                # Compute the z-normalized time series
                df_filtered["ts"] = df_filtered["activity"].apply(lambda x:
                                        TS.znorm(TS.ts_from_datetime(x,
                                                                     start_window,
                                                                     end_window)))

                # Compute DTW between each authors
                out = compute_dtw(df_filtered, allowable_lag, use_shift)
                #print("max corr = " + str(out.warp_corr.max()) + "   at " + str(start_window))

                out["window"] = start_window

                corr = out[out["warp_corr"] >= report_threshold].copy()
                df_corr = pd.concat([df_corr, corr])
                if time.time() > base_time + 300:
                    if df_corr.shape[0] > 0:
                        df_corr.to_csv(os.path.join(out_dir, "out_corr_" + str(idx_out) + ".csv"),
                                      index=False,
                                      encoding='utf-8')
                        print("saved until " + str(start_window))
                        df_corr = pd.DataFrame(columns=['author_id_x',
                                                        'author_id_y',
                                                        'warp_corr',
                                                        'window'])
                        idx_out += 1
                    base_time = time.time()

        # Update start_window
        start_window = end_window
    df_corr.to_csv(os.path.join(out_dir, "out_corr_" + str(idx_out) + ".csv"),
                   index=False,
                   encoding='utf-8')

    # Concatenate the partial results
    concat_csv(out_dir, "out_corr_", os.path.join(out_dir, "out_corr.csv"))
