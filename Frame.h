#include <vector>
#include <iostream>

namespace frame {
    class Frame {
    public:
        std::vector<std::vector<double>> arr;
        Frame(std::vector<std::vector<double>> arr);
        ~Frame();
        int getSize();
    };
}