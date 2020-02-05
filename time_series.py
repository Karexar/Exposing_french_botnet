from datetime import datetime, timedelta
import numpy as np
import math

# Create time series from created_at (str)
# Since we use dynamic time warping, the length doesn't need to be the same
# for all time series. We simply start from the first tweet and end for the last tweet.

class TimeSeries:
    def __init__(self,
                 interval=1):
        self.interval = interval
        #self.base_time = base_time
        #self.end_time = end_time
        #self.ts_size = int((self.end_time - self.base_time).total_seconds()//self.win_size+1)

    def znorm(self, x):
        '''
        Z-normalization of a list of integer
        '''
        x = np.array(x)
        return (x - x.mean()) / x.std()

    def ts_from_datetime(self, user_ts, start, end):
        '''
            Takes a list of datetime.datetime and convert it into a time series
            between 'start' and 'end' datetime.
        '''
        column_idx = 0
        # +2 stands for the zero we add at the beginning and end of the time
        # series. This is a simple way to solve the problem of two time series
        # being not correlated if one of them starts or ends with a non zero
        # value but not the other, even if the other is in the allowable gap.
        # for example, if author 1 tweet at 0:0:0 and author 2 at 0:0:1, then
        # the max correlation will be around 0.95, independantly to the rest.
        length = int((end - start).total_seconds() / self.interval + 1 + 2)
        activity = np.zeros((length), dtype=np.int64)
        for i in range(len(user_ts)):
            time_stamp =  user_ts[i]
            delta = (time_stamp - start).total_seconds()
            column_idx = math.floor(delta/self.interval)+1
            activity[column_idx] = activity[column_idx] + 1
        return activity

    # def get_ts_from_datetime(self, user_ts):
    #     '''
    #         Takes a list of datetime.datetime and convert it into a z-normalized
    #         time series. It starts from the min datetime and ends at the max
    #         datetime from the user_ts list.
    #
    #     '''
    #     first = min(user_ts)
    #     last = max(user_ts)
    #     length = int(((last - first).total_seconds() + 1) / self.interval)
    #     activity = np.zeros((length))
    #     for i in range(len(user_ts)):
    #         time_stamp =  user_ts[i]
    #         delta = (time_stamp - first).total_seconds()
    #         column_temp = int(delta/self.interval)
    #         activity[column_temp] = activity[column_temp] + 1
    #
    #     return self.znorm(activity)

    # def get_ts_from_datetime(self, user_ts):
    #     '''
    #         Takes a list of datetime.datetime and convert it into a time series
    #     '''
    #     check_list = []
    #     column_temp = 0
    #
    #     activity = np.zeros((self.ts_size))
    #     for i in range(len(user_ts)):
    #         time_stamp =  user_ts[i]
    #         delta = (time_stamp - self.base_time).total_seconds()
    #         column_temp = int(delta/self.win_size)
    #         try:
    #             activity[column_temp] = activity[column_temp] + 1
    #         except:
    #             #print(str(self.base_time) + "  " + str(time_stamp) + "   " +  str(delta) + "   "+ str(column_temp) + "   " +str(self.ts_size))
    #             pass
    #
    #     return self.znorm(activity)

    def encode_ts(self, ts):
        '''
            WARNING : time-consuming version, please use get_encoded_ts instead.
            Take a time serie (list of integers) and convert it to be usable
            by the awarp algorithm. It replaces sequences of zeroes by a
            negative number whose value represents the count of zeroes (e.g.
            [1, 0, 0, 0, 1] -> [1, -3, 1]). Note that if the first or the last
            observation is zero, then it must be -1 (i.e. we can group zeroes
            only for those who are not in first or last position). Example :
            [0, 1, 0, 0, 0] => [-1, 1, -2, -1]
        '''
        res = [ts[0]] if ts[0] != 0 else [-1]
        zeros = 0
        for x in ts[1:]:
            if x == 0:
                zeros+=1
            else:
                if zeros > 0:
                    res.append(-zeros)
                    zeros=0
                res.append(x)
        if zeros > 0:
            if zeros > 1:
                res.append(-(zeros-1))
            res.append(-1)

        return res

    def get_encoded_ts(self, activity):
        '''
            Takes a list of datetime and convert it into an encoded time serie
            usable by the awarp algorithm. Instead of writing long sequences of
            zeros, it will replace them by a negative number whose value represents
            the count of zeroes (e.g. [1, 0, 0, 0, 1] -> [1, -3, 1]).
            Note that if the first or the last observation is zero, then it must
            be -1 (i.e. we can group zeroes only for those who are not in first
            or last position). Example : [0, 1, 0, 0, 0] => [-1, 1, -2, -1]
        '''
        # Filter out all activity outside the period of interest
        activity = [x for x in activity if x >= self.base_time and x <= self.end_time]

        if len(activity) == 0:
            return [-1, -(int((self.end_time-self.base_time).total_seconds() - 1)), -1]

        activity.sort()

        res = []
        last_timestamp = self.base_time - timedelta(seconds=1)

        # Iterate over all timestamps and add the correct number of preceding zeroes
        i = 0
        while i < len(activity):
            # Count how much zeros before
            zeros = int((activity[i] - last_timestamp).total_seconds() - 1)
            if zeros > 0:
                res.append(-zeros)
            # Count how many tweets in the same second
            count = 1
            last_timestamp = activity[i]
            while i+1 < len(activity) and activity[i+1] == last_timestamp:
                i+=1
                count+=1
            res.append(count)
            last_timestamp = activity[i]
            i+=1

        final_zeroes = int((self.end_time - last_timestamp).total_seconds())
        if final_zeroes > 0:
            res.append(-final_zeroes)

        # if the first element is a run of zeros, replace it by an observation
        # e.g. ([-4, ...] => [-1, -4, ...])
        if res[0] < -1:
            res = [-1] + [res[0]+1] + res[1:]
        # same for the last element
        if res[-1] < -1:
            res = res[:-1] + [res[-1]+1] + [-1]

        return res
