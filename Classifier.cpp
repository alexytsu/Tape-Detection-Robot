#include "Classifier.h"
#include <cmath>

using namespace classifier;
using namespace std;

Classifier::Classifier(){
    vector<int> v1(256, 0);
    vector<vector<int>> v1d2(256, v1);
    arr = v1d2;
}

Classifier::~Classifier()
{
}

void Classifier::train(int hue, int sat, int color)
{
    arr[hue][sat] = color;
}

int Classifier::lookup(int hue, int sat)
{
    return arr[hue][sat];
}