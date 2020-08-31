#include <iostream>
#include <algorithm>
using namespace std;

class Glyph
{
public:
    char node[4][4] = {
        {'.', '.', '.', '.'},
        {'.', '.', '.', '.'},
        {'.', '.', '.', '.'},
        {'.', '.', '.', '.'},
    };
    int turn = 1;
    int nodes = 0;

    void show()
    {
        int x, y;
        for (x = 0; x < 4; ++x)
        {
            for (y = 0; y < 4; ++y)
            {
                cout << node[x][y] << ' ';
            }
            cout << '\n';
        }
        cout << '\n';
    }