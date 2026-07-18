#include <stdio.h>
#include "solver.h"

int main()
{
    Sudoku puzzle;

    loadPuzzle(&puzzle, "data/input/puzzle1.txt");
    printf("Original Sudoku Puzzle\n");
    printPuzzle(&puzzle);

    return 0;
}