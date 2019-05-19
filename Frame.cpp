#include "Frame.h"
#include <cmath>

using namespace frame;
using namespace std;

Frame::Frame(vector<vector<double>> f)
{
    arr = f;
}

Frame::~Frame()
{
}

vector<pair<int, int>> Frame::getPoints()
{
    vector<pair<int, int>> darkvec;
    vector<pair<int, int>> lightvec;
    for (uint32_t i = arr.size()/2; i < arr.size(); i++)
    {

        int dark_j = 0;
        int n_dark = 0;

        int light_j = 0;
        int n_light = 0;

        uint32_t width = arr[0].size();
        for (uint32_t j = 0; j < width; j++)
        {
            if (arr[i][j] == 0.2)
            {
                n_dark++;
                dark_j += j;
            }
            if (arr[i][j] == 0.6)
            {
                n_light++;
                light_j += j;
            }
        }

        if (n_dark != 0)
        {
            darkvec.push_back(make_pair(dark_j / n_dark, i));
        }

        if (n_light != 0)
        {
            lightvec.push_back(make_pair(light_j / n_light, i));
        }
    }

    this->lightvec = lightvec;
    this->darkvec = darkvec;

    lightvec.insert(lightvec.end(), darkvec.begin(), darkvec.end());

    return lightvec;
}

vector<pair<pair<int, int>, pair<int, int>>> Frame::getLines()
{
    vector<pair<pair<int, int>, pair<int, int>>> lines;
    // perform a linear fit by method of least squares
    double xsum = 0, ysum = 0, x2sum = 0, xysum = 0;
    uint32_t n = darkvec.size();
    cout << "n: " << n << endl;
    for (uint32_t i = 0; i < n; i++)
    {
        xsum += darkvec[i].first;
        ysum += darkvec[i].second;
        x2sum += pow(darkvec[i].first, 2);
        xysum += darkvec[i].first * darkvec[i].second;
    }

    double avg_slope;
    double avg_intercept;

    double slope = (n*xysum-xsum*ysum)/(n*x2sum-xsum*xsum);            //calculate slope
    double intercept = (x2sum*ysum-xsum*xysum)/(x2sum*n-xsum*xsum); 

    avg_slope = slope;
    avg_intercept = intercept;

    // (y-b)/m
    int basex, basey, endx, endy;
    basey = 0;
    basex =  (int)(basey-intercept)/slope;

    endy = arr.size();
    endx = (int)(endy-intercept)/slope;

    pair<int, int> base = make_pair(basex, basey);
    pair<int, int> end = make_pair(endx, endy);
    pair<pair<int, int>, pair<int, int>> line = make_pair(base, end);
    lines.push_back(line);


    n = lightvec.size();
    xsum = 0;
    ysum = 0;
    x2sum = 0;
    xysum = 0;
    for (uint32_t i = 0; i < n; i++)
    {
        xsum += lightvec[i].first;
        ysum += lightvec[i].second;
        x2sum += pow(lightvec[i].first, 2);
        xysum += lightvec[i].first * lightvec[i].second;
    }

    slope = (n*xysum-xsum*ysum)/(n*x2sum-xsum*xsum);            //calculate slope
    intercept = (x2sum*ysum-xsum*xysum)/(x2sum*n-xsum*xsum); 

    avg_slope += slope;
    avg_intercept += intercept;
    avg_slope = avg_slope / 2;
    avg_intercept = avg_intercept / 2;

    basey = 0;
    basex =  (int)(basey-intercept)/slope;

    endy = arr.size();
    endx = (int)(endy-intercept)/slope;

    base = make_pair(basex, basey);
    end = make_pair(endx, endy);
    line = make_pair(base, end);
    lines.push_back(line);

    basey = 0;
    basex =  (int)(basey-avg_intercept)/avg_slope;

    endy = arr.size();
    endx = (int)(endy-avg_intercept)/avg_slope;

    base = make_pair(basex, basey);
    end = make_pair(endx, endy);
    line = make_pair(base, end);
    lines.push_back(line);



    return lines;
}