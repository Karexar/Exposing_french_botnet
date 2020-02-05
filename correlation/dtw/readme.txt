Here we can call the DTW algorithm with the shell directly.

To run dtw.cpp, we need a ts.csv file which contains all time series to compare, as integers, comma-separated. It should also be z-normalized. The first line is not a time series and contains only the value of w (the maximum allowable lag in seconds). 

The programm output an out.txt file, containing on each line :
- the first index of time series
- the second index of time series (strictly superior to first index)
- the dtw distance between the two time series
All space-separated

On OSX :
clang++ -std=c++11 -stdlib=libc++ dtw.cpp;chmod 777 a.out;./a.out
