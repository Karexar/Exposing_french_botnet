#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <iostream>
#include <vector>
#include <fstream>
#include <sstream>
#include <chrono>

#define inf 1e19;
#define MIN(X, Y) (((X) < (Y)) ? (X) : (Y))

using namespace std;

class DTW{
    public:
        struct result{
            int ts_1;
            int ts_2;
            double d;
        };

        double UBCases(double a, double b, char c)
        {
            double v = 0;
            if( a > 0  && b > 0 )
                v = (a-b)*(a-b);
            else if ( a> 0 && b < 0 )
            {
                if( c=='l' )
                    v = a*a;

                else

                    v = (-b)*a*a;

            }
            else if ( a < 0 && b > 0 )
            {
                if( c == 't' )
                    v = b*b;
                else
                    v = (-a)*b*b;

            }
            else
                v = 0;

            return v;
        }

        double dtw_G(double *s, double *t, int c, int ns, int nt )
        {
            double d=0;
            double ** D;
            int i,j;

            double a1, a2, a3;

            D = (double **) malloc((ns+1)*sizeof(double *));
            for( i = 0 ; i <= ns ; i++ )
                D[i] =(double *)malloc((nt+1)*sizeof(double));




            for(i=0;i<ns+1;i++)
            {
               D[i][0] = inf;

            }

            for(i=0;i<nt+1;i++)
            {
               D[0][i] = inf;

            }

            D[0][0]=0;


            for(i=0;i<ns;i++)
            {

                for(j=0;j<nt;j++)
                {

                    a1 = D[i][j] + (s[i]-t[j])*(s[i]-t[j]);

                    if( i > 0  && j > 0 )
                        a1 = D[i][j] + UBCases(s[i],t[j],'d');
                    a2 = D[i+1][j] + UBCases(s[i],t[j],'t');
                    a3 = D[i][j+1] + UBCases(s[i],t[j],'l');

                    D[i+1][j+1]= MIN(a3,MIN(a1,a2));
                    //cout << D[i+1][j+1] << " ";
                }
                //cout << endl;

            }

            d = sqrt(D[ns][nt]);

            for( i = 0 ; i <= ns ; i++ )
                free(D[i]);
            free(D);

            return d;//(double)matchLength;
        }

        void read_compute_dtw() {
            fstream fin; // File pointer
            fin.open("correlation/awarp_wrapper/ts.csv", ios::in);

            // Store all time series
            vector<vector<double> > tss;
            string line;
            while(getline(fin, line)) {
                vector<double> ts;
                stringstream s_1(line); // used for breaking words
                string word;
                while (getline(s_1, word, ',')) {
                    ts.push_back(stod(word));
                }
                tss.push_back(ts);
            }

            // Compute the data time warping distance
            vector<result> ds;
            for (int i=0 ; i<tss.size() ; ++i) {
                for (int j=i+1 ; j < tss.size() ; ++j) {
                    double* ts_1 = &tss[i][0];
                    double* ts_2 = &tss[j][0];
                    double d = dtw_G(ts_1, ts_2, -1, tss[i].size(), tss[j].size());
                    result res;
                    res.ts_1 = i;
                    res.ts_2 = j;
                    res.d = d;
                    ds.push_back(res);
                }
            }

            // Store it in a file
            stringstream out; // used for breaking words
            for (int i=0 ; i<ds.size() ; ++i) {
                out << ds[i].ts_1 << " " << ds[i].ts_2 << " " << ds[i].d << endl;
            }

            fstream fout; // File pointer
            fout.open("correlation/awarp_wrapper/out.txt", ios::out);
            fout << out.str();
        }

        void run(){
            auto t1 = std::chrono::high_resolution_clock::now();
            //read_dtw();
            read_compute_dtw();
            auto t2 = std::chrono::high_resolution_clock::now();
            std::cout << "test function took "
                      << std::chrono::duration_cast<std::chrono::milliseconds>(t2-t1).count()
                      << " milliseconds\n";
        }
};

extern "C" {
    DTW* DTW_new(){ return new DTW(); }
    void DTW_bar(DTW* dtw){ dtw->run(); }
}
