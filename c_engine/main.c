#include <stdio.h>
#include <time.h>
#include "solver.h"

int main()
{
    Sudoku puzzle;

    puzzle.recursiveCalls = 0;
    puzzle.backtracks = 0;

    loadPuzzle(&puzzle, "data/input/puzzle1.txt");

    printf("Original Sudoku Puzzle\n");
    printPuzzle(&puzzle);

    clock_t start = clock();

    if (solveSudoku(&puzzle))
    {
        clock_t end = clock();

        double executionTime =
            (double)(end - start) / CLOCKS_PER_SEC;

        printf("Solved Sudoku Puzzle\n");
        printPuzzle(&puzzle);

        printf("\nPerformance Statistics\n");
        printf("----------------------\n");
        printf("Recursive Calls : %ld\n", puzzle.recursiveCalls);
        printf("Backtracks      : %ld\n", puzzle.backtracks);
        printf("Execution Time  : %.6f seconds\n", executionTime);
    }
    else
    {
        printf("No solution exists.\n");
    }

    return 0;
}