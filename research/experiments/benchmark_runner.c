#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#include "../solvers/bt_naive/solver.h"

#define LINE_SIZE 512
#define PUZZLE_LENGTH 81


static int parse_puzzle(
    const char *puzzle_string,
    int grid[SIZE][SIZE]
)
{
    if (strlen(puzzle_string) != PUZZLE_LENGTH)
        return 0;

    for (int i = 0; i < PUZZLE_LENGTH; i++) {

        char ch = puzzle_string[i];

        if (ch < '0' || ch > '9')
            return 0;

        grid[i / SIZE][i % SIZE] = ch - '0';
    }

    return 1;
}


static int count_clues(int grid[SIZE][SIZE])
{
    int clues = 0;

    for (int r = 0; r < SIZE; r++) {
        for (int c = 0; c < SIZE; c++) {
            if (grid[r][c] != 0)
                clues++;
        }
    }

    return clues;
}


int main(void)
{
    const char *input_path =
        "research/data/pilot/puzzles_100.csv";

    const char *output_path =
        "research/results/solver_runs_100.csv";


    FILE *input = fopen(input_path, "r");

    if (input == NULL) {
        fprintf(stderr,
                "ERROR: could not open %s\n",
                input_path);

        return EXIT_FAILURE;
    }


    FILE *output = fopen(output_path, "w");

    if (output == NULL) {
        fprintf(stderr,
                "ERROR: could not create %s\n",
                output_path);

        fclose(input);

        return EXIT_FAILURE;
    }


    /*
     * Research V2 solver-run schema.
     */
    fprintf(
        output,
        "puzzle_id,"
        "source,"
        "source_difficulty,"
        "clue_count,"
        "solver,"
        "solver_version,"
        "solved,"
        "solution_valid,"
        "recursive_calls,"
        "candidate_checks,"
        "constraint_rejections,"
        "committed_assignments,"
        "backtracked_assignments,"
        "backtrack_events,"
        "search_nodes,"
        "max_depth,"
        "solution_depth\n"
    );


    char line[LINE_SIZE];

    /*
     * Skip CSV header.
     */
    if (fgets(line, sizeof(line), input) == NULL) {

        fprintf(stderr, "ERROR: empty input dataset\n");

        fclose(input);
        fclose(output);

        return EXIT_FAILURE;
    }


    int total = 0;
    int successful = 0;
    int rejected = 0;


    while (fgets(line, sizeof(line), input) != NULL) {

        /*
         * Remove newline characters.
         */
        line[strcspn(line, "\r\n")] = '\0';


        char *puzzle_id =
            strtok(line, ",");

        char *puzzle_string =
            strtok(NULL, ",");

        char *source =
            strtok(NULL, ",");

        char *source_record_id =
            strtok(NULL, ",");

        char *difficulty =
            strtok(NULL, ",");

        char *sampling_seed =
            strtok(NULL, ",");

        if (puzzle_id == NULL ||
            puzzle_string == NULL ||
            source == NULL ||
            source_record_id == NULL ||
            difficulty == NULL ||
            sampling_seed == NULL) {

                
            fprintf(
                stderr,
                "WARNING: malformed CSV row skipped\n"
            );

            rejected++;
            continue;
        }
        total++;


        int grid[SIZE][SIZE];

        if (!parse_puzzle(puzzle_string, grid)) {

            fprintf(stderr,
                    "WARNING: %s has malformed puzzle string\n",
                    puzzle_id);

            rejected++;
            continue;
        }


        int clues = count_clues(grid);


        /*
         * Reject structurally invalid initial Sudoku.
         */
        if (!is_valid_grid(grid)) {

            fprintf(stderr,
                    "WARNING: %s contains invalid givens\n",
                    puzzle_id);

            rejected++;
            continue;
        }


        SolverMetrics metrics;

        int solved =
            solve_sudoku(grid, &metrics);

        int solution_valid = 0;


        if (solved)
            solution_valid =
                is_valid_solution(grid);


        if (solved && solution_valid)
            successful++;


        fprintf(
            output,
            "%s,%s,%s,%d,"
            "BT_NAIVE,1.0,"
            "%d,%d,"
            "%llu,%llu,%llu,"
            "%llu,%llu,%llu,"
            "%llu,%d,%d\n",

            puzzle_id,
            source,
            difficulty,
            clues,

            solved,
            solution_valid,

            (unsigned long long)
                metrics.recursive_calls,

            (unsigned long long)
                metrics.candidate_checks,

            (unsigned long long)
                metrics.constraint_rejections,

            (unsigned long long)
                metrics.committed_assignments,

            (unsigned long long)
                metrics.backtracked_assignments,

            (unsigned long long)
                metrics.backtrack_events,

            (unsigned long long)
                metrics.search_nodes,

            metrics.max_depth,
            metrics.solution_depth
        );


        printf(
            "%s -> solved=%d, calls=%llu, backtracks=%llu\n",

            puzzle_id,
            solved,

            (unsigned long long)
                metrics.recursive_calls,

            (unsigned long long)
                metrics.backtracked_assignments
        );
    }


    fclose(input);
    fclose(output);


    printf("\nBenchmark complete\n");
    printf("------------------\n");

    printf("Puzzles processed : %d\n", total);
    printf("Valid solutions   : %d\n", successful);
    printf("Rejected rows     : %d\n", rejected);

    printf(
        "Results written to: %s\n",
        output_path
    );


    return EXIT_SUCCESS;
}