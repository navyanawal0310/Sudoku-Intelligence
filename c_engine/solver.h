#ifndef SOLVER_H
#define SOLVER_H

#define SIZE 9

typedef struct
{
    int board[SIZE][SIZE];
    long recursiveCalls;
    long backtracks;
} Sudoku;

void loadPuzzle(Sudoku *puzzle, const char *filename);
void printPuzzle(const Sudoku *puzzle);
int isSafe(const Sudoku *puzzle, int row, int col, int num);
int solveSudoku(Sudoku *puzzle);
int findEmptyCell(const Sudoku *puzzle, int *row, int *col);
#endif


