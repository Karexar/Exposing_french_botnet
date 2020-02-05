#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <iostream>
#include <vector>
#include <fstream>
#include <sstream>
#include <chrono>

#define inf 1e19;

struct result{
    int ts_1;
    int ts_2;
    double d;
    double corr;
};

using namespace std;



double dtw_G(double *s, double *t, int w, int ns, int nt , int *len);
void read_dtw();
void read_compute_dtw();
void normalize(vector<double> *ts_1, vector<double> *ts_2);

double dtw_G(double *s, double *t, int w, int ns, int nt , int *len)
{
    double d=0;
       int sizediff=ns-nt>0 ? ns-nt : nt-ns;
    double * D , *P , *T , *tttmp , * M , *MP;
    int i,j,tttml,j1,j2,k;

    double cost,temp;
    if(w!=-1 && w<sizediff) w=sizediff;

    //Take the longer signal in S
    if( nt > ns )
    {
        tttmp = s;
        s = t;
        t = tttmp;
        tttml = ns;
        ns = nt;
        nt = tttml;
    }

    D =(double *)malloc((nt+1)*sizeof(double));
    P =(double *)malloc((nt+1)*sizeof(double));
    M =(double *)malloc((nt+1)*sizeof(double));
    MP =(double *)malloc((nt+1)*sizeof(double));


    for(i=0;i<nt+1;i++)
    {
       P[i]= inf;
       D[i] = inf;
       M[i] = 0;
       MP[i] = 0;
    }

       //printf("%d",w);
    P[0]=0;
    D[0]=inf;
    for(i=1;i<=ns;i++)
    {

        if(w==-1)
        {
            j1=1;
            j2=nt;
        }
        else
        {
            j1= i-w>1 ? i-w : 1;
            j2= i+w<nt ? i+w : nt;
        }

         D[j1-1] = inf;
         M[j1-1] = inf;

        for(j=j1;j<=j2;j++)
        {
            cost= (s[i-1]-t[j-1])*(s[i-1]-t[j-1]);

            if( P[j] < P[j-1] )
                temp = P[j];
            else
                temp = P[j-1];

            if(temp > D[j-1])
            {
                temp=D[j-1];
                M[j] = M[j-1]+1;
            }
            else if( P[j] < P[j-1] )
            {
                M[j] = MP[j] + 1;
            }
            else
            {
                M[j] = MP[j-1] + 1;
            }


            D[j]=cost+temp;
        }

       //Swap D and P , swap M and MP. P means prior. D means Data and M means
        T = P;
        P = D;
        D = T;
        T = MP;
        MP = M;
        M = T;

    }

    d=sqrt(P[nt]);
    *len = MP[nt];

    free(D);
    free(P);
    free(M);
    free(MP);


    return d;//(double)matchLength;
}

/*void read_dtw()
{
    fstream fin; // File pointer

    fin.open("ts1.csv", ios::in);
    string line, word, temp;
    int size_1, size_2;
    getline(fin, line); // read a row and store in 'line'
    stringstream s_1(line); // used for breaking words
    getline(s_1, word, ',');
    size_1 = stoi(word);
    double row_1[size_1];
    // read every column data of a row and store it in 'word'
    int i = 0;
    while (getline(s_1, word, ',')) {
        row_1[i] = stod(word);
        ++i;
    }
    fin.close();

    fin.open("ts2.csv", ios::in);
    line.clear();
    word.clear();
    temp.clear();
    getline(fin, line); // read a row and store in 'line'
    stringstream s_2(line); // used for breaking words
    getline(s_2, word, ',');
    size_2 = stoi(word);
    double row_2[size_2];
    // read every column data of a row and store it in 'word'
    i = 0;
    while (getline(s_2, word, ',')) {
        row_2[i] = stod(word);
        ++i;
    }
    fin.close();

    // Compute dtw
    int len = -1;
    auto t1 = std::chrono::high_resolution_clock::now();
    // TEST ///////////////
    //const int ns = 19;
    //const int nt = 12;
    //int w = -1;
    //double s[ns] = {1.0, 0.0, 0.0, 0.0, 0.0, 2.0, 1.0, 0.0, 0.0, 3.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0};
    //double t[nt] = {1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 2.0};

    //const int ns = 26;
    //const int nt = 26;
    //double s[ns] = {0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0};
    //double t[nt] = {0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0};
    //double s[ns] = {1, 0, 0, 1, 1, 3, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1};
    //double t[nt] = {1, 0, 0, 0, 2, 0, 2, 1, 0, 0, 0, 4, 5, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1};
    //double d = dtw_G(s, t, -1, ns, nt, &len);
    ///////////////////////
    double d = dtw_G(row_1, row_2, -1, size_1, size_2 , &len);
    auto t2 = std::chrono::high_resolution_clock::now();
    std::cout << "test function took "
              << std::chrono::duration_cast<std::chrono::milliseconds>(t2-t1).count()
              << " milliseconds\n";

    cout << "distance: " << d << endl;

}*/

// Min-max version. DO NOT USE
// Produce bad results compare to non normalized
/*void normalize(vector<double> *ts_1, vector<double> *ts_2) {
    double max1 = *max_element(ts_1->begin(), ts_1->end());
    double max2 = *max_element(ts_2->begin(), ts_2->end());
    double min1 = *min_element(ts_1->begin(), ts_1->end());
    double min2 = *min_element(ts_2->begin(), ts_2->end());
    double max_value = max(max1, max2);
    double min_value = min(min1, min2);
    double max_minus_min = max_value - min_value;

    for (int i = 0 ; i < ts_1->size() ; ++i) {
        (*ts_1)[i] = ((*ts_1)[i] - min_value) / max_minus_min;
    }
    for (int i = 0 ; i < ts_2->size() ; ++i) {
        (*ts_2)[i] = ((*ts_2)[i] - min_value) / max_minus_min;
    }
}*/

void read_compute_dtw() {
    fstream fin; // File pointer
    fin.open("ts.csv", ios::in);

    // Store all time series
    vector<vector<double> > tss;
    string line;
    string word;

    getline(fin, line); // read a row and store in 'line'
    stringstream s_1(line); // used for breaking words
    getline(s_1, word, ',');
    int w = stoi(word);

    while(getline(fin, line)) {
        word.clear();
        vector<double> ts;
        stringstream s_2(line); // used for breaking words
        while (getline(s_2, word, ',')) {
            ts.push_back(stod(word));
        }
        tss.push_back(ts);
    }

    // Compute the data time warping distance
    vector<result> ds;
    int len = -1;
    for (int i=0 ; i<tss.size() ; ++i) {
        for (int j=i+1 ; j < tss.size() ; ++j) {
            double d = dtw_G(&tss[i][0], &tss[j][0], w, tss[i].size(), tss[j].size(), &len);
            result res;
            res.ts_1 = i;
            res.ts_2 = j;
            res.d = d;
            res.corr = 1.0 - d*d/(2*len);
            ds.push_back(res);
        }
    }

    // Store it in a file
    stringstream out; // used for breaking words
    for (int i=0 ; i<ds.size() ; ++i) {
        out << ds[i].ts_1 << " " << ds[i].ts_2 << " " << ds[i].d << " "<< ds[i].corr << endl;
    }

    fstream fout; // File pointer
    fout.open("out.txt", ios::out);
    fout << out.str();
}

int main()
{
    auto t1 = std::chrono::high_resolution_clock::now();
    //read_dtw();
    read_compute_dtw();
    auto t2 = std::chrono::high_resolution_clock::now();
    std::cout << "test function took "
              << std::chrono::duration_cast<std::chrono::milliseconds>(t2-t1).count()
              << " milliseconds\n";
}
