#include <iostream>
using namespace std;

class NCboard{
    public:
    int node[9];
    bool turn;
}

// to get the kth bit of n, (n >> k) & 1

void showBoard(int node)
{
    for(auto x : node)
    {
        cout << '\n';
    };
};

NCboard board;

string x;
bool y;
int main()
{
    board.node[9] = {
            0, 0, 0,
            0, 0, 0,
            0, 0, 0
            };
    cout << board.node;
    //y = showBoard(board.node);
    return 0;
}