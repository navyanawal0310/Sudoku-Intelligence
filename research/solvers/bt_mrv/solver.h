#ifndef MRV_SOLVER_H
#define MRV_SOLVER_H

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

void reset_metrics(SolverMetrics *metrics);

int is_valid_grid(
    int grid[SIZE][SIZE]
);

int is_safe(
    int grid[SIZE][SIZE],
    int row,
    int col,
    int num,
    SolverMetrics *metrics
);

int solve_sudoku(
    int grid[SIZE][SIZE],
    SolverMetrics *metrics
);

int is_valid_solution(
    int grid[SIZE][SIZE]
);

#endif