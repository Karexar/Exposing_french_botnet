CPP wrapper for python to compute awarp distance.

Setup on OSX to create awarp.o and libawarp.so:
clang++ -std=c++11 -stdlib=libc++ -c -fPIC awarp.cpp -o awarp.o
clang++ -std=c++11 -stdlib=libc++ -shared -W1, -install_name,libawarp.so -o libawarp.so awarp.o
