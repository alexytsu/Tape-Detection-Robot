#include <vector>
#include <iostream>

namespace frame {
    class Frame {
    public:
        std::vector<std::vector<double>> arr;
        std::vector<std::pair<int, int>> darkvec;
        std::vector<std::pair<int, int>> lightvec;
        Frame(std::vector<std::vector<double>> arr);
        ~Frame();
        std::vector<std::pair<int, int>> getPoints();
        std::vector<std::pair<std::pair<int, int>, std::pair<int, int>>> getLines();
    };
}