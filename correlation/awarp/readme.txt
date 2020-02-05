Here we can call the awarp algorithm with the shell directly.

To run awarp.cpp, we need a ts.csv file which contains all time series to compare, comma-separated, and encoded for awarp. It should also be z-normalized.

The programm output an out.txt file, containing on each line :
- the first index of time series
- the second index of time series (strictly superior to first index)
- the awarp distance between the two time series
All space-separated

On OSX :
clang++ -std=c++11 -stdlib=libc++ awarp.cpp;chmod 777 a.out;./a.out
