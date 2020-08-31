#include <iostream>
#include <algorithm>
using namespace std;

class Glyph
{
    public:
        char node[3][3] = {
            {'.', '.', '.'}, 
            {'.', '.', '.'}, 
            {'.', '.', '.'}
            };
        int turn = 1;
        int nodes = 0;

        bool is_full()
        {
            for (int x = 0; x < 3; x++){
                for (int y = 0; y < 3; y++){
                    if (node[x][y] == '.'){
                        return false;
                    }
                }
            }
            return true;
        }

        void show()
        {
            int x, y;
            for (x = 0; x < 3; ++x){
                for (y = 0; y < 3; ++y){
                    cout << node[x][y] << ' ';
                }
                cout << '\n';
            }
            cout << '\n';
        }
        void play(int x, int y)
        {
            if (turn == 1){
                node[x][y] = 'X';
                turn = -1;
            }else{
                node[x][y] = '0';
                turn = 1;
            }
        }
        void unplay(int x, int y)
        {
            node[x][y] = '.';
            if (turn == 1){turn = -1;} else {turn = 1;}
        }
        int evaluate()
        {
            for (int row = 0; row < 3; row++){
                if (node[row][0] == node[row][1] && node[row][1] == node[row][2]){
                    if (node[row][0] == 'X'){return 1;}
                    else if (node[row][0] == '0'){return -1;}
                }
            }
            for (int col = 0; col < 3; col++){
                if (node[0][col] == node[1][col] && node[1][col] == node[2][col]){
                    if (node[0][col] == 'X'){return 1;}
                    else if (node[0][col] == '0'){return -1;}
                }
            }
            if (node[0][0] == node[1][1] && node[1][1] == node[2][2]){
                if (node[0][0] == 'X'){return 1;}
                else if (node[0][0] == '0'){return -1;}
            }
            if (node[0][2] == node[1][1] && node[1][1] == node[2][0]){
                if (node[0][2] == 'X'){return 1;}
                else if (node[0][2] == '0'){return -1;}
            }
            return 0;
        }

        int negamax(int colour, int a = -20, int b = 20)
        {
            if(evaluate() != 0 || is_full() == true){return turn * evaluate();}
            int score;
            int x, y;

            for (int x = 0; x < 3; x++){
                for (int y = 0; y < 3; y++){
                    if (node[x][y] == '.'){
                        play(x, y);
                        nodes++;
                        score = -negamax(-colour, -b, -a);
                        unplay(x, y);

                        if (score > b){return b;}
                        if (score > a){a = score;}
                    }
                }
            }
            return a;
        }
        int max_pos(int arr[])
        {
            int max, index;
            max = arr[0];
            index = 0;
            for (int i = 0; i < 9; i++){
                if (arr[i] > max){
                    max = arr[i];
                    index = i;
                }
            }
            return index;
        }
        int min_pos(int arr[])
        {
            int min, index;
            min = arr[0];
            index = 0;
            for (int i = 0; i < 9; i++){
                if (arr[i] < min){
                    min = arr[i];
                    index = i;
                }
            }
            return index;
        }
        void engine_move()
        {
            int x, y, index;
            int scores [9] = {-9,-9,-9,-9,-9,-9,-9,-9,-9};
            
            for (int row = 0; row < 3; row++){
                for (int col = 0; col < 3; col++){
                    if (node[row][col] == '.'){
                        play(row, col);
                        scores[row*3+col] = -negamax(turn);
                        unplay(row, col);
                    }
                }
            }
            //cout << '{'; for (int i = 0; i < 9; i++){cout << scores[i] << ", ";}; cout << '}';
            //cout << '\n';
            index = max_pos(scores);
            x = index/3;
            y = index%3;
            play(x, y);
        }
        void show_result()
        {
            int r;
            r = evaluate();
            if (r == 0)
            {
                cout << "1/2-1/2" << '\n';
            }
            else if (r == 1)
            {
                cout << "1-0" << '\n';
            }
            else
            {
                cout << "0-1" << '\n';
            }
        }
};

int main()
{
    Glyph glyph;
    int x, y;
    while (glyph.evaluate() == 0 && glyph.is_full() == false)
    {

        glyph.engine_move();
        glyph.show();
        /*
        if (glyph.evaluate() != 0 || glyph.is_full() == true)
        {
            break;
        }

        cin >> x;
        cin >> y;
        glyph.play(x, y);
        glyph.show();*/
    }
    glyph.show_result();
    return 0;
}