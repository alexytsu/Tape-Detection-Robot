#include <vector>
#include <iostream>

using namespace std;

namespace frame {
    class Frame {
    public:
        vector<vector<double>> arr;
        vector<pair<int, int>> darkvec;
        vector<pair<int, int>> lightvec;
        vector<pair<int, int>> midpoints;
        double percentage;
        Frame(vector<vector<double>> arr);
        ~Frame();
        vector<pair<int, int>> getTapePoints(bool top);
        vector<pair<int, int>> getMidPoints();
        vector<pair<int, int>> getLightPoints();
        vector<pair<int, int>> getDarkPoints();
        vector<pair<pair<int, int>, pair<int, int>>> getNavLine();
        vector<pair<pair<int, int>, pair<int, int>>> getYellowLine();
        vector<pair<pair<int, int>, pair<int, int>>> getBlueLine();
    };

}