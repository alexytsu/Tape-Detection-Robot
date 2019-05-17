#include "Frame.h"

using namespace frame;

Frame::Frame(std::vector<std::vector<double>> f)
{
    arr = f;
}

Frame::~Frame()
{
}

std::vector<std::pair<int, int>> Frame::getSize()
{
    std::vector<std::pair<int, int>> vec;
    int angle = 0;
    for (uint32_t i = 0; i < arr.size(); i++)
    {

        int dark_j = 0;
        int n_dark = 0;
        int dark_centroid = 0;

        int light_j = 0;
        int n_light = 0;
        int light_centroid = 0;


        uint32_t width = arr[0].size();
        for (uint32_t j = 0; j < width; j++)
        {
            if(arr[i][j] == 0.2){
                n_dark ++;
                dark_j += j;
            }
            if(arr[i][j] == 0.6){
                n_light ++;
                light_j += j;
            }
        }

        if(n_dark != 0){
            dark_centroid = (int)(dark_j/n_dark);
            angle += dark_centroid;
        }

        if(n_light != 0){
            light_centroid = (int)(light_j/n_light);
            angle += light_centroid;
        }


    }

    std::cout << angle << std::endl;
    vec.push_back(std::make_pair(angle, arr.size()/2));

    return vec;
}