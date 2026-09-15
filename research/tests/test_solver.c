#include <stdio.h>
#include <assert.h>

#include "../solvers/bt_naive/solver.h"


void test_already_solved(void)
{
    int grid[SIZE][SIZE] = {
        {5,3,4,6,7,8,9,1,2},
        {6,7,2,1,9,5,3,4,8},
        {1,9,8,3,4,2,5,6,7},
        {8,5,9,7,6,1,4,2,3},
        {4,2,6,8,5,3,7,9,1},
        {7,1,3,9,2,4,8,5,6},
        {9,6,1,5,3,7,2,8,4},
        {2,8,7,4,1,9,6,3,5},
        {3,4,5,2,8,6,1,7,9}
    };

    SolverMetrics metrics;

    int solved = solve_sudoku(grid, &metrics);

    assert(solved == 1);
    assert(is_valid_solution(grid) == 1);

    assert(metrics.recursive_calls == 1);
    assert(metrics.search_nodes == 1);
    assert(metrics.candidate_checks == 0);
    assert(metrics.constraint_rejections == 0);
    assert(metrics.committed_assignments == 0);
    assert(metrics.backtracked_assignments == 0);
    assert(metrics.backtrack_events == 0);
    assert(metrics.max_depth == 0);
    assert(metrics.solution_depth == 0);

    printf("PASS: already solved puzzle\n");
}


void test_one_missing_cell(void)
{
    int grid[SIZE][SIZE] = {
        {5,3,4,6,7,8,9,1,2},
        {6,7,2,1,9,5,3,4,8},
        {1,9,8,3,4,2,5,6,7},
        {8,5,9,7,6,1,4,2,3},
        {4,2,6,8,5,3,7,9,1},
        {7,1,3,9,2,4,8,5,6},
        {9,6,1,5,3,7,2,8,4},
        {2,8,7,4,1,9,6,3,5},
        {3,4,5,2,8,6,1,7,0}
    };

    SolverMetrics metrics;

    int solved = solve_sudoku(grid, &metrics);

    assert(solved == 1);
    assert(grid[8][8] == 9);
    assert(is_valid_solution(grid) == 1);

    assert(metrics.recursive_calls == 2);
    assert(metrics.search_nodes == 2);
    assert(metrics.committed_assignments == 1);
    assert(metrics.backtracked_assignments == 0);
    assert(metrics.max_depth == 1);
    assert(metrics.solution_depth == 1);

    /*
     * Candidates are tested sequentially 1..9.
     * For this cell, 1 through 8 are rejected and
     * 9 is accepted.
     */
    assert(metrics.candidate_checks == 9);
    assert(metrics.constraint_rejections == 8);

    printf("PASS: one missing cell\n");
}


void test_invalid_grid(void)
{
    int grid[SIZE][SIZE] = {
        {5,5,4,6,7,8,9,1,2}, /* duplicate 5 */
        {6,7,2,1,9,5,3,4,8},
        {1,9,8,3,4,2,5,6,7},
        {8,5,9,7,6,1,4,2,3},
        {4,2,6,8,5,3,7,9,1},
        {7,1,3,9,2,4,8,5,6},
        {9,6,1,5,3,7,2,8,4},
        {2,8,7,4,1,9,6,3,5},
        {3,4,5,2,8,6,1,7,9}
    };

    SolverMetrics metrics;

    int solved = solve_sudoku(grid, &metrics);

    assert(solved == 0);

    /*
     * Invalid input must be rejected BEFORE recursive
     * search starts.
     */
    assert(metrics.recursive_calls == 0);
    assert(metrics.search_nodes == 0);

    printf("PASS: invalid puzzle rejected\n");
}


int main(void)
{
    printf("\nSudoku Research V2 - Solver Tests\n");
    printf("---------------------------------\n");

    test_already_solved();
    test_one_missing_cell();
    test_invalid_grid();

    printf("---------------------------------\n");
    printf("ALL TESTS PASSED\n\n");

    return 0;
}