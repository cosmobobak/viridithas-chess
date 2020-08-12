#include <iostream>
using namespace std;
using U64 = uint64_t;

class CBoard
{
    U64 whitePawns;
    U64 whiteKnights;
    U64 whiteBishops;
    U64 whiteRooks;
    U64 whiteQueens;
    U64 whiteKing;

    U64 blackPawns;
    U64 blackKnights;
    U64 blackBishops;
    U64 blackRooks;
    U64 blackQueens;
    U64 blackKing;
};

int main()
{
    CBoard board;

    cout << board;

    return 0;
}