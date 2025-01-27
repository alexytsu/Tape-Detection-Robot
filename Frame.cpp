#include "Frame.h"
#include <cmath>

using namespace frame;
using namespace std;

Frame::Frame(vector<vector<double>> f)
{
    arr = f;
    // percentage of the frame to consider for navigation purposes
    percentage = 1;
}

Frame::~Frame()
{
}

vector<pair<int, int>> Frame::getTapePoints(bool top)
{
    vector<pair<int, int>> darkvec;
    vector<pair<int, int>> lightvec;
    for (uint32_t i = (uint32_t)(arr.size() * (1 - this->percentage)); i < (uint32_t)(arr.size()); i++)
    {

        int dark_j = 0;
        int n_dark = 0;

        int light_j = 0;
        int n_light = 0;


        uint32_t width = arr[0].size();
        uint16_t limit = width/4;
        if (top == true) limit = 0;


        for (uint32_t j = 0; j < width; j++)
        {

            if (arr[i][j] == 1 && j < width - limit)
            {
                n_dark++;
                dark_j += j;
            }

            if (arr[i][j] == 3 && j > limit)
            {
                n_light++;
                light_j += j;
            }

        }

        if(n_dark != 0 && n_light != 0) {
        uint16_t dark_centroid = dark_j / n_dark;
        uint16_t light_centroid = light_j / n_light;

        uint16_t middle = width/2;
        if (dark_centroid > light_centroid) {
            middle = (dark_centroid + light_centroid) / 2;
            if(middle > width/2) {
                n_dark = 0;
            } else {
                n_light = 0;
            }
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

        if (n_dark != 0 && n_light != 0)
        {
            midpoints.push_back(make_pair(
                (int)(((dark_j / n_dark) + (light_j / n_light)) / 2), i));
        }
    }

    this->lightvec = lightvec;
    this->darkvec = darkvec;
    this->midpoints = midpoints;

    return lightvec;
}

vector<pair<int, int>> Frame::getMidPoints()
{
    return midpoints;
}

vector<pair<int, int>> Frame::getLightPoints()
{
    return lightvec;
}

vector<pair<int, int>> Frame::getDarkPoints()
{
    return darkvec;
}

vector<pair<pair<int, int>, pair<int, int>>> Frame::getBlueLine()
{
    vector<pair<pair<int, int>, pair<int, int>>> lines;

    // PLOT POINTS FOR DARK VEC
    double xsum = 0, ysum = 0, x2sum = 0, xysum = 0;
    uint32_t n = darkvec.size();
    if (n <= 1){
        return lines;
    }
    for (uint32_t i = 0; i < n; i++)
    {
        xsum += darkvec[i].first;
        ysum += darkvec[i].second;
        x2sum += pow(darkvec[i].first, 2);
        xysum += darkvec[i].first * darkvec[i].second;
    }

    double slope = (n * xysum - xsum * ysum) / (n * x2sum - xsum * xsum); //calculate slope
    double intercept = (x2sum * ysum - xsum * xysum) / (x2sum * n - xsum * xsum);

    // (y-b)/m
    int basex, basey, endx, endy;
    basey = 0;
    basex = (int)((basey - intercept) / slope);

    endy = arr.size();
    endx = (int)((endy - intercept) / slope);

    pair<int, int> base = make_pair(basex, basey);
    pair<int, int> end = make_pair(endx, endy);
    pair<pair<int, int>, pair<int, int>> line = make_pair(base, end);
    lines.push_back(line);
    return lines;
}

vector<pair<pair<int, int>, pair<int, int>>> Frame::getYellowLine()
{
    vector<pair<pair<int, int>, pair<int, int>>> lines;

    // PLOT POINTS FOR DARK VEC
    double xsum = 0, ysum = 0, x2sum = 0, xysum = 0;
    uint32_t n = lightvec.size();
    if (n <= 1){
        return lines;
    }
    for (uint32_t i = 0; i < n; i++)
    {
        xsum += lightvec[i].first;
        ysum += lightvec[i].second;
        x2sum += pow(lightvec[i].first, 2);
        xysum += lightvec[i].first * lightvec[i].second;
    }

    double slope = (n * xysum - xsum * ysum) / (n * x2sum - xsum * xsum); //calculate slope
    double intercept = (x2sum * ysum - xsum * xysum) / (x2sum * n - xsum * xsum);

    // (y-b)/m
    int basex, basey, endx, endy;
    basey = 0;
    basex = (int)((basey - intercept) / slope);

    endy = arr.size();
    endx = (int)((endy - intercept) / slope);

    pair<int, int> base = make_pair(basex, basey);
    pair<int, int> end = make_pair(endx, endy);
    pair<pair<int, int>, pair<int, int>> line = make_pair(base, end);
    lines.push_back(line);
    return lines;
}

vector<pair<pair<int, int>, pair<int, int>>> Frame::getNavLine()
{
    vector<pair<pair<int, int>, pair<int, int>>> lines;

    // PLOT POINTS FOR DARK VEC
    double xsum = 0, ysum = 0, x2sum = 0, xysum = 0;
    uint32_t n = midpoints.size();
    if (n <= 1){
        return lines;
    }
    for (uint32_t i = 0; i < n; i++)
    {
        xsum += midpoints[i].first;
        ysum += midpoints[i].second;
        x2sum += pow(midpoints[i].first, 2);
        xysum += midpoints[i].first * midpoints[i].second;
    }

    double slope = (n * xysum - xsum * ysum) / (n * x2sum - xsum * xsum); //calculate slope
    double intercept = (x2sum * ysum - xsum * xysum) / (x2sum * n - xsum * xsum);

    // (y-b)/m
    int basex, basey, endx, endy;
    basey = 0;
    basex = (int)((basey - intercept) / slope);

    endy = arr.size();
    endx = (int)((endy - intercept) / slope);

    pair<int, int> base = make_pair(basex, basey);
    pair<int, int> end = make_pair(endx, endy);
    pair<pair<int, int>, pair<int, int>> line = make_pair(base, end);
    lines.push_back(line);
    return lines;
}
