import pandas as pd
import numpy as np
from ctypes import cdll
lib = cdll.LoadLibrary('./correlation/dtw_wrapper/libdtw.so')

class DTW(object):
    def __init__(self):
        self.obj = lib.DTW_new()

    def run(self):
        lib.DTW_bar(self.obj)

def compute_dtw(df_author_ts, w, shift):
    '''
    Takes a dataframe with 'author_id' and 'ts' as columnn.
    'ts' should contain z-normalized time series.
    w is the maximum allowable lag in seconds.
    Write the time series on disk and call a python wrapper
    for cpp that will read the file and compute the distances.
    The wrapper will then write the result on disk. The function
    then read the file and returns a dataframe with 'author_id_x',
    'author_id_y' and 'd' representing the distance between two
    authors.
    '''

    # Write on disk
    if shift:
        shift = "1"
    else:
        shift = "0"
    to_write = str(w) + "\n" + shift + "\n"
    for x in df_author_ts.ts:
        for y in x:
            to_write += str(y) + ","
        to_write = to_write[:-1]
        to_write += "\n"
    with open("correlation/dtw_wrapper/ts.csv", "w") as f:
        f.write(to_write)

    # call the wrapper
    f = DTW()
    f.run()

    # read the output file
    df_out = pd.read_csv('correlation/dtw_wrapper/out.txt', sep=" ", header=None,
                     names = ["author_id_x","author_id_y","warp_corr"])

    # update the author columns with the right authors
    current_idx = 0
    author_list = list(df_author_ts.author_id)
    cur_count = df_author_ts.shape[0]-1
    count = int((df_author_ts.shape[0]*(df_author_ts.shape[0]-1))/2)
    author_left = []
    author_right = []
    for i in range(len(author_list)-1):
        author_left += [author_list[i]]*cur_count
        cur_count-=1
    cur_count = df_author_ts.shape[0]-1
    for i in range(len(author_list)-1):
        for j in range(i+1, len(author_list)):
            author_right.append(author_list[j])

    df_out["author_id_x"] = author_left
    df_out["author_id_y"] = author_right

    return df_out

def znorm(x):
    '''
    Z-normalization of a list of integer
    '''
    x = np.array(x)
    return (x - x.mean()) / x.std()

def compute_single_dtw(tss, w, shift):
    '''
    Takes a list of two time series and compute dtw distance.
    w is the maximum allowable lag in seconds.
    Z-normalize the time series if not already done.
    Write the time series on disk and call a python wrapper
    for cpp that will read the file and compute the distances.
    The wrapper will then write the result on disk. The function
    then read the file and print the distance.
    '''
    tss[0] = znorm(tss[0])
    tss[1] = znorm(tss[1])
    if shift:
        shift = "1"
    else:
        shift = "0"
    to_write = str(w) + "\n" + shift + "\n"
    for x in tss:
        for y in x:
            to_write += str(y) + ","
        to_write = to_write[:-1]
        to_write += "\n"

    with open("correlation/dtw_wrapper/ts.csv", "w") as f:
        f.write(to_write)

    # call the wrapper
    f = DTW()
    f.run()

    # read the output file
    df_out = pd.read_csv('correlation/dtw_wrapper/out.txt', sep=" ", header=None,
                     names = ["author_id_x","author_id_y","warp_corr"])

    print(df_out.iloc[0]["warp_corr"])
