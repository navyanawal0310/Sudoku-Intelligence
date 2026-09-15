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