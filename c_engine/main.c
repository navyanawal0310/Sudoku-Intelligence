#include <stdio.h>
#include "solver.h"

int main()
{
    Sudoku puzzle;

    loadPuzzle(&puzzle, "data/input/puzzle1.txt");
    printf("Original Sudoku Puzzle\n");
    printf("Original Sudoku Puzzle\n");
    printPuzzle(&puzzle);
    if (solveSudoku(&puzzle))
    {
        printf("Solved Sudoku Puzzle\n");
        printPuzzle(&puzzle);
    }
    else
    {
        printf("No solution exists.\n");
    }
    return 0;
}