#include <string.h>

#include "solver.h"


void reset_metrics(SolverMetrics *metrics)
{
    memset(metrics, 0, sizeof(SolverMetrics));
}


int is_valid_grid(int grid[SIZE][SIZE])
{
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


int is_safe(
    int grid[SIZE][SIZE],
    int row,
    int col,
    int num,
    SolverMetrics *metrics
)
{
    metrics->candidate_checks++;

    for (int x = 0; x < SIZE; x++) {
        if (grid[row][x] == num) {
            metrics->constraint_rejections++;
            return 0;
        }
    }

    for (int x = 0; x < SIZE; x++) {
        if (grid[x][col] == num) {
            metrics->constraint_rejections++;
            return 0;
        }
    }

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


/*
 * Candidate tests used only to select the MRV cell.
 * These are deliberately NOT counted in candidate_checks.
 */
static int candidate_is_legal(
    int grid[SIZE][SIZE],
    int row,
    int col,
    int num
)
{
    for (int x = 0; x < SIZE; x++) {
        if (grid[row][x] == num)
            return 0;
    }

    for (int x = 0; x < SIZE; x++) {
        if (grid[x][col] == num)
            return 0;
    }

    int start_row = row - row % 3;
    int start_col = col - col % 3;

    for (int r = 0; r < 3; r++) {
        for (int c = 0; c < 3; c++) {
            if (grid[start_row + r][start_col + c] == num)
                return 0;
        }
    }

    return 1;
}


static int count_candidates(
    int grid[SIZE][SIZE],
    int row,
    int col
)
{
    int count = 0;

    for (int num = 1; num <= 9; num++) {
        if (candidate_is_legal(grid, row, col, num))
            count++;
    }

    return count;
}


/*
 * MRV variable selection.
 *
 * Tie-breaking is deterministic:
 * first minimum encountered in row-major order.
 */
static int find_mrv_cell(
    int grid[SIZE][SIZE],
    int *selected_row,
    int *selected_col
)
{
    int best_count = 10;
    int found = 0;

    for (int row = 0; row < SIZE; row++) {
        for (int col = 0; col < SIZE; col++) {

            if (grid[row][col] != 0)
                continue;

            int count = count_candidates(
                grid,
                row,
                col
            );

            if (count < best_count) {
                best_count = count;
                *selected_row = row;
                *selected_col = col;
                found = 1;

                if (best_count == 0)
                    return 1;
            }
        }
    }

    return found;
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

    if (!find_mrv_cell(grid, &row, &col)) {
        metrics->solution_depth = depth;
        return 1;
    }

    int explored_legal_candidate = 0;

    for (int num = 1; num <= 9; num++) {

        if (is_safe(
            grid,
            row,
            col,
            num,
            metrics
        )) {
            explored_legal_candidate = 1;

            grid[row][col] = num;
            metrics->committed_assignments++;

            if (solve_recursive(
                grid,
                metrics,
                depth + 1
            )) {
                return 1;
            }

            grid[row][col] = 0;
            metrics->backtracked_assignments++;
        }
    }

    if (explored_legal_candidate)
        metrics->backtrack_events++;

    return 0;
}


int solve_sudoku(
    int grid[SIZE][SIZE],
    SolverMetrics *metrics
)
{
    reset_metrics(metrics);

    if (!is_valid_grid(grid))
        return 0;

    return solve_recursive(grid, metrics, 0);
}


int is_valid_solution(int grid[SIZE][SIZE])
{
    for (int row = 0; row < SIZE; row++) {
        for (int col = 0; col < SIZE; col++) {
            if (grid[row][col] == 0)
                return 0;
        }
    }

    return is_valid_grid(grid);
}