#include <iostream>
#include <algorithm>
using namespace std;

class Move
{
public:
    int from_square;
    int to_square;
};

class Board
{
public:
    long long node[6];
    bool turn = true;

    bool get_square(long long bb, int squareNum){
        return (bb & (1 << squareNum));
    }

    void __repr__(){
        
    }
};

class Vorpal
{
public:
    int nodes = 0;
};

int main()
{
    Vorpal engine;
    return 0;
}