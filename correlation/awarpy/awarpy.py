import numpy as np
from math import sqrt

# Run awarp directly in python
# This is about 4x slower than the cpp version

def UBCases(a, b, c):
    v = 0
    if a > 0 and b > 0:
        v = (a-b)**2
    elif a > 0 and b < 0:
        if c == 'l':
            v = a*a
        else:
            v = (-b)*a*a
    elif a < 0 and b > 0:
        if c == 't':
            v = b*b
        else:
            v = (-a)*b*b
    else:
        v = 0
    return v

def awarpy(s, t):
    '''
    Compute awarp distance between two time series
    Takes two time series (list) already encoded for awarp (replacing runs of
    zeroes by minus something). It should have been previously z-normalized.
    Return the awarp distance between the two time series.
    '''
    d = 0
    D = np.zeros((len(s)+1, len(t)+1))

    for i in range(len(s)+1):
        D[i][0] = np.inf
    for i in range(len(t)+1):
        D[0][i] = np.inf
    D[0][0] = 0

    for i in range(len(s)):
        for j in range(len(t)):
            a1 = D[i][j] + (s[i]-t[j]) * (s[i]-t[j])
            if i > 0 and j > 0:
                a1 = D[i][j] + UBCases(s[i], t[j], 'd')
            a2 = D[i+1][j] + UBCases(s[i], t[j], 't')
            a3 = D[i][j+1] + UBCases(s[i], t[j], 'l')

            D[i+1][j+1] = min(a3, min(a1, a2))

    d = sqrt(D[len(s)][len(t)])

    return d
