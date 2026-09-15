#ifndef SOLVER_H
#define SOLVER_H

#include <stdint.h>

#define SIZE 9

typedef struct {
    uint64_t recursive_calls;
    uint64_t candidate_checks;
    uint64_t constraint_rejections;

    uint64_t committed_assignments;
    uint64_t backtracked_assignments;
    uint64_t backtrack_events;

    uint64_t search_nodes;

    int max_depth;
    int solution_depth;
} SolverMetrics;

/* Reset all instrumentation counters */
void reset_metrics(SolverMetrics *metrics);

/* Check whether the initial Sudoku grid is valid */
int is_valid_grid(const int grid[SIZE][SIZE]);

/* Check whether a candidate can legally be placed */
int is_safe(
    const int grid[SIZE][SIZE],
    int row,
    int col,
    int num,
    SolverMetrics *metrics
);

/* Solve puzzle using deterministic row-major backtracking */
int solve_sudoku(
    int grid[SIZE][SIZE],
    SolverMetrics *metrics
);

/* Verify that a completed grid is a valid Sudoku solution */
int is_valid_solution(const int grid[SIZE][SIZE]);

#endif