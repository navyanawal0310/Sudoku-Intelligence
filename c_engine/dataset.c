#include <stdio.h>
#include <string.h>
#include "dataset.h"
#include <time.h>
#include "solver.h"

void processDataset(const char *inputFile,
                    const char *outputFile)
{
    FILE *fp = fopen(inputFile, "r");

    if (fp == NULL)
    {
        printf("Cannot open dataset.\n");
        return;
    }

    FILE *out = fopen(outputFile, "w");
    printf("Writing to: %s\n", outputFile);

    if (out == NULL)
    {
        printf("Cannot create output file.\n");
        fclose(fp);
        return;
    }

    fprintf(
        out,
        "id,empty_cells,recursive_calls,backtracks,candidate_checks,successful_assignments,failed_assignments,maximum_depth,execution_time_ms,solved\n"
    );

    char line[200];

    fgets(line, sizeof(line), fp);   // Skip header

    while (fgets(line, sizeof(line), fp))
    {
        char id[20];
        char puzzleString[100];

        sscanf(line, "%19[^,],%81s", id, puzzleString);

        Sudoku puzzle;

        loadPuzzleFromString(&puzzle, puzzleString);

        clock_t start = clock();

        int solved = solveSudoku(&puzzle);

        clock_t end = clock();

        double executionTime =
            (double)(end - start) * 1000.0 / CLOCKS_PER_SEC;

        printf("Puzzle %s solved\n", id);
        printf("Recursive Calls : %ld\n", puzzle.recursiveCalls);
        printf("Backtracks      : %ld\n", puzzle.backtracks);
        printf("Execution Time  : %.6f ms\n\n", executionTime);

        fprintf(
            out,
            "%s,%d,%ld,%ld,%ld,%ld,%ld,%d,%.3f,%d\n",
            id,
            puzzle.emptyCells,
            puzzle.recursiveCalls,
            puzzle.backtracks,
            puzzle.candidateChecks,
            puzzle.successfulAssignments,
            puzzle.failedAssignments,
            puzzle.maximumDepth,
            executionTime,
            solved
        );

        fflush(out);
    }

    fclose(fp);
    fclose(out);
}