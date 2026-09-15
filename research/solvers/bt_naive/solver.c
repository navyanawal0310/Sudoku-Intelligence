#include "solver.h"
#include <string.h>


void reset_metrics(SolverMetrics *metrics)
{
    memset(metrics, 0, sizeof(SolverMetrics));
}


int is_valid_grid(const int grid[SIZE][SIZE])
{
    /* Rows */
    for (int row = 0; row < SIZE; row++) {
        int seen[10] = {0};

        for (int col = 0; col < SIZE; col++) {
            int value = grid[row][col];

            if (value < 0 || value > 9)
                return 0;

            if (value != 0) {
                if (seen[value])
                    return 0;

                seen[value] = 1;
            }
        }
    }

    /* Columns */
    for (int col = 0; col < SIZE; col++) {
        int seen[10] = {0};

        for (int row = 0; row < SIZE; row++) {
            int value = grid[row][col];

            if (value != 0) {
                if (seen[value])
                    return 0;

                seen[value] = 1;
            }
        }
    }

    /* 3x3 boxes */
    for (int box_row = 0; box_row < SIZE; box_row += 3) {
        for (int box_col = 0; box_col < SIZE; box_col += 3) {

            int seen[10] = {0};

            for (int row = box_row; row < box_row + 3; row++) {
                for (int col = box_col; col < box_col + 3; col++) {

                    int value = grid[row][col];

                    if (value != 0) {
                        if (seen[value])
                            return 0;

                        seen[value] = 1;
                    }
                }
            }
        }
    }

    return 1;
}


static int find_empty_cell(
    const int grid[SIZE][SIZE],
    int *row,
    int *col
)
{
    /*
     * IMPORTANT:
     * Keep row-major selection.
     *
     * This is deliberately the naive baseline.
     * Do NOT introduce MRV here.
     */
    for (int r = 0; r < SIZE; r++) {
        for (int c = 0; c < SIZE; c++) {
            if (grid[r][c] == 0) {
                *row = r;
                *col = c;
                return 1;
            }
        }
    }

    return 0;
}


int is_safe(
    const int grid[SIZE][SIZE],
    int row,
    int col,
    int num,
    SolverMetrics *metrics
)
{
    metrics->candidate_checks++;

    /*
     * A candidate is counted as ONE constraint rejection,
     * regardless of how many Sudoku constraints it might violate.
     */

    /* Row constraint */
    for (int c = 0; c < SIZE; c++) {
        if (grid[row][c] == num) {
            metrics->constraint_rejections++;
            return 0;
        }
    }

    /* Column constraint */
    for (int r = 0; r < SIZE; r++) {
        if (grid[r][col] == num) {
            metrics->constraint_rejections++;
            return 0;
        }
    }

    /* Box constraint */
    int start_row = row - row % 3;
    int start_col = col - col % 3;

    for (int r = 0; r < 3; r++) {
        for (int c = 0; c < 3; c++) {
            if (grid[start_row + r][start_col + c] == num) {
                metrics->constraint_rejections++;
                return 0;
            }
        }
    }

    return 1;
}


static int solve_recursive(
    int grid[SIZE][SIZE],
    SolverMetrics *metrics,
    int depth
)
{
    metrics->recursive_calls++;
    metrics->search_nodes++;

    if (depth > metrics->max_depth)
        metrics->max_depth = depth;

    int row;
    int col;

    /* No empty cell means puzzle has been solved */
    if (!find_empty_cell(grid, &row, &col)) {
        metrics->solution_depth = depth;
        return 1;
    }

    int explored_candidate = 0;

    for (int num = 1; num <= 9; num++) {

        if (is_safe(grid, row, col, num, metrics)) {

            explored_candidate = 1;

            grid[row][col] = num;
            metrics->committed_assignments++;

            if (solve_recursive(grid, metrics, depth + 1))
                return 1;

            /*
             * Candidate was locally legal but ultimately
             * led to a dead end.
             */
            grid[row][col] = 0;
            metrics->backtracked_assignments++;
        }
    }

    /*
     * We exhausted at least one legal branch and none
     * produced a solution.
     */
    if (explored_candidate)
        metrics->backtrack_events++;

    return 0;
}


int solve_sudoku(
    int grid[SIZE][SIZE],
    SolverMetrics *metrics
)
{
    reset_metrics(metrics);

    if (!is_valid_grid((const int (*)[SIZE])grid))
        return 0;

    return solve_recursive(grid, metrics, 0);
}


int is_valid_solution(const int grid[SIZE][SIZE])
{
    /* A completed solution cannot contain zeros */
    for (int row = 0; row < SIZE; row++) {
        for (int col = 0; col < SIZE; col++) {
            if (grid[row][col] == 0)
                return 0;
        }
    }

    return is_valid_grid(grid);
}