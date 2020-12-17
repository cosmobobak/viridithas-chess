#include <iostream>
#include <vector>
#include <algorithm>
#include <unordered_map>

auto main(std::vector<int> run, int runlength, int loops){
    std::unordered_map<int, int> distanceToNums;

    int count = runlength;
    for (auto &&r : run)
    {
        distanceToNums[r] = count + 1;
        count--;
        if (count == 0)
        {
            break;
        }
    }

    int current = run[-1];
    for (int i = runlength; i < loops; i++)
    {
        int probe = distanceToNums.contains(current) ? distanceToNums.find(current) : (-1);
        distanceToNums[current] = 0;
        if (probe == -1)
            {current = 0;}
        else
            {current = probe;}
        distanceToNums = {k: v + 1 for k, v in distanceToNums.items()};
        if (i % 10000 == 0)
            {print(f"{i/300000}% done!");}
    }

    return current
}