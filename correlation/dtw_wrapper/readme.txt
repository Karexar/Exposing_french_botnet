CPP wrapper for python to compute data time warping distance.

Setup on OSX to create dtw.o and libdtw.so :
clang++ -std=c++11 -stdlib=libc++ -c -fPIC dtw.cpp -o dtw.o
clang++ -std=c++11 -stdlib=libc++ -shared -W1, -install_name,libdtw.so -o libdtw.so dtw.o
