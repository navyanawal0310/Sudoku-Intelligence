#ifndef SOLVER_H
#define SOLVER_H

#define SIZE 9

typedef struct
{
    int board[SIZE][SIZE];
} Sudoku;

void loadPuzzle(Sudoku *puzzle, const char *filename);
void printPuzzle(const Sudoku *puzzle);

#endif