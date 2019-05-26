#include <vector>

using namespace std;

namespace classifier
{
    class Classifier
    {
        public:
            Classifier();
            ~Classifier();
            vector<vector<int>> arr;
            void train(int hue, int sat, int color);
            int lookup(int hue, int sat);
    };
} // namespace classifier