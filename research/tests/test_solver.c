#include <stdio.h>
#include <assert.h>

#include "../solvers/bt_naive/solver.h"


/* =========================================================
   TEST 1: ALREADY SOLVED PUZZLE
   ========================================================= */

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


/* =========================================================
   TEST 2: ONE MISSING CELL
   ========================================================= */

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

    assert(metrics.candidate_checks == 9);
    assert(metrics.constraint_rejections == 8);

    printf("PASS: one missing cell\n");
}


/* =========================================================
   TEST 3: INVALID GRID
   ========================================================= */

void test_invalid_grid(void)
{
    int grid[SIZE][SIZE] = {
        {5,5,4,6,7,8,9,1,2},
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

    assert(metrics.recursive_calls == 0);
    assert(metrics.search_nodes == 0);

    printf("PASS: invalid puzzle rejected\n");
}


/* =========================================================
   TEST 4: STANDARD PUZZLE + METRIC INVARIANTS
   ========================================================= */

void test_standard_puzzle(void)
{
    int grid[SIZE][SIZE] = {
        {5,3,0,0,7,0,0,0,0},
        {6,0,0,1,9,5,0,0,0},
        {0,9,8,0,0,0,0,6,0},
        {8,0,0,0,6,0,0,0,3},
        {4,0,0,8,0,3,0,0,1},
        {7,0,0,0,2,0,0,0,6},
        {0,6,0,0,0,0,2,8,0},
        {0,0,0,4,1,9,0,0,5},
        {0,0,0,0,8,0,0,7,9}
    };

    SolverMetrics metrics;

    int solved = solve_sudoku(grid, &metrics);

    assert(solved == 1);
    assert(is_valid_solution(grid) == 1);

    /* Fundamental metric invariants */

    assert(metrics.recursive_calls > 1);

    assert(metrics.search_nodes ==
           metrics.recursive_calls);

    assert(metrics.candidate_checks >=
           metrics.constraint_rejections);

    assert(metrics.committed_assignments >=
           metrics.backtracked_assignments);

    assert(metrics.max_depth >=
           metrics.solution_depth);

    /*
     * Original puzzle contains 51 empty cells.
     * Successful solution therefore terminates at depth 51.
     */
    assert(metrics.solution_depth == 51);

    printf("PASS: standard puzzle\n");

    printf("  recursive calls       : %llu\n",
           (unsigned long long)metrics.recursive_calls);

    printf("  candidate checks      : %llu\n",
           (unsigned long long)metrics.candidate_checks);

    printf("  constraint rejections : %llu\n",
           (unsigned long long)metrics.constraint_rejections);

    printf("  committed assignments : %llu\n",
           (unsigned long long)metrics.committed_assignments);

    printf("  backtracked assigns   : %llu\n",
           (unsigned long long)metrics.backtracked_assignments);

    printf("  backtrack events      : %llu\n",
           (unsigned long long)metrics.backtrack_events);

    printf("  search nodes          : %llu\n",
           (unsigned long long)metrics.search_nodes);

    printf("  max depth             : %d\n",
           metrics.max_depth);

    printf("  solution depth        : %d\n",
           metrics.solution_depth);
}


/* =========================================================
   TEST 5: 100-RUN DETERMINISM
   ========================================================= */

void test_determinism(void)
{
    SolverMetrics baseline;

    for (int run = 0; run < 100; run++) {

        int grid[SIZE][SIZE] = {
            {5,3,0,0,7,0,0,0,0},
            {6,0,0,1,9,5,0,0,0},
            {0,9,8,0,0,0,0,6,0},
            {8,0,0,0,6,0,0,0,3},
            {4,0,0,8,0,3,0,0,1},
            {7,0,0,0,2,0,0,0,6},
            {0,6,0,0,0,0,2,8,0},
            {0,0,0,4,1,9,0,0,5},
            {0,0,0,0,8,0,0,7,9}
        };

        SolverMetrics current;

        int solved = solve_sudoku(grid, &current);

        assert(solved == 1);
        assert(is_valid_solution(grid) == 1);

        if (run == 0) {
            baseline = current;
        }
        else {

            assert(current.recursive_calls ==
                   baseline.recursive_calls);

            assert(current.candidate_checks ==
                   baseline.candidate_checks);

            assert(current.constraint_rejections ==
                   baseline.constraint_rejections);

            assert(current.committed_assignments ==
                   baseline.committed_assignments);

            assert(current.backtracked_assignments ==
                   baseline.backtracked_assignments);

            assert(current.backtrack_events ==
                   baseline.backtrack_events);

            assert(current.search_nodes ==
                   baseline.search_nodes);

            assert(current.max_depth ==
                   baseline.max_depth);

            assert(current.solution_depth ==
                   baseline.solution_depth);
        }
    }

    printf("PASS: deterministic metrics across 100 runs\n");
}


/* =========================================================
   MAIN TEST RUNNER
   ========================================================= */

int main(void)
{
    printf("\nSudoku Research V2 - Solver Tests\n");
    printf("---------------------------------\n");

    test_already_solved();
    test_one_missing_cell();
    test_invalid_grid();

    printf("\nInstrumentation Tests\n");
    printf("---------------------------------\n");

    test_standard_puzzle();
    test_determinism();

    printf("---------------------------------\n");
    printf("ALL TESTS PASSED\n\n");

    return 0;
}