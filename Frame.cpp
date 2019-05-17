#include "Frame.h"

using namespace frame;

Frame::Frame(std::vector<std::vector<double>> f)
{
    arr = f;
}

Frame::~Frame()
{

}

int Frame::getSize()
{
    std::cout << "c++ print" << std::endl;
    return 100;
}