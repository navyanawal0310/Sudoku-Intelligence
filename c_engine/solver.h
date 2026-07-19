#ifndef SOLVER_H
#define SOLVER_H

#define SIZE 9

typedef struct
{
    int board[SIZE][SIZE];

    long recursiveCalls;
    long backtracks;
    long candidateChecks;
    long successfulAssignments;
    long failedAssignments;
    int currentDepth;
    int maximumDepth;
    int emptyCells;

}Sudoku;

void loadPuzzle(Sudoku *puzzle, const char *filename);
void printPuzzle(const Sudoku *puzzle);
int isSafe(Sudoku *puzzle, int row, int col, int num);
int solveSudoku(Sudoku *puzzle);
int findEmptyCell(const Sudoku *puzzle, int *row, int *col);
void loadPuzzleFromString(Sudoku *puzzle, const char *str);
void initializeMetrics(Sudoku *puzzle);
int countEmptyCells(const Sudoku *puzzle);
#endif