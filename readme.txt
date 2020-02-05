
Semester project at EPFL - Fall 2019

This project aims at discovering correlated activity on the french twitter. We use the DeBot method as a baseline. Some new features have been added. The most important are : 

 - Choose at runtime whether or not to use hashing to filter out users. From experiments, if the user count in a window of 2 hours is lower than around 150, it is faster and more accurate to compute the warped correlation between all authors in the time window.
 
 - Timeline alignment : the allowable gap does not allow for shift beyond its value. Here we can specify if we want to find the best timeline alignment prior to computing the warped correlation. For now, it is implemented in cpp, like DTW, but it could more efficient to use numpy parallelization to compute the best alignment. 

About the code : 

The two main files are hash_user.py and corr_user.py. The first one corresponds to step 2 of DeBot, which is the indexer. The second one corresponds roughly to step 4, which is the computation of DTW. Unlike DeBot, we use mostly pre-made datasets in this project. 

A simple example in given in Test.ipynb, it requires to download the Ecuador dataset from April 2019 (or any other dataset actually) from Twitter : 
https://transparency.twitter.com/en/information-operations.html

The ‘correlation’ directorty contains a python wrapper to run cpp files. It is used to compute DTW from a python script. Awarp is also available. It’s an approximation of DTW, which is much faster for sparse time series. However, it’s currently implemented only for non normalized time series, so it’s not used in this project. If we want to analyse time series with longer time window, we may want to adapt awarp for z-normalized time series and use it instead of DTW to speed up the computation. 

The ‘others’ directory contains some notebooks that have been used to explore data and for different experiments. 

