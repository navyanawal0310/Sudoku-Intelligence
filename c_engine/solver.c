#include <stdio.h>
#include "solver.h"
#include <time.h>

void loadPuzzle(Sudoku *puzzle, const char *filename)
{
    FILE *fp = fopen(filename, "r");

    if (fp == NULL)
    {
        printf("Error: Could not open %s\n", filename);
        return;
    }
    printf("Successfully opened: %s\n", filename);
    char ch;

    for (int i = 0; i < SIZE; i++)
    {
        for (int j = 0; j < SIZE; j++)
        {
            ch = fgetc(fp);

            puzzle->board[i][j] = ch - '0';
        }

        fgetc(fp);      
    }

    fclose(fp);

    initializeMetrics(puzzle);
}
void printPuzzle(const Sudoku *puzzle)
{
    printf("\n");

    for (int i = 0; i < SIZE; i++)
    {
        for (int j = 0; j < SIZE; j++)
        {
            printf("%d ", puzzle->board[i][j]);

            if ((j + 1) % 3 == 0 && j != SIZE - 1)
                printf("| ");
        }

        printf("\n");

        if ((i + 1) % 3 == 0 && i != SIZE - 1)
            printf("---------------------\n");
    }

    printf("\n");
}
int isSafe(Sudoku *puzzle, int row, int col, int num)
{
    puzzle->candidateChecks++;
    for (int i = 0; i < SIZE; i++)
    {
        if (puzzle->board[row][i] == num)
            return 0;
    }
    for (int i = 0; i < SIZE; i++)
    {
        if (puzzle->board[i][col] == num)
            return 0;
    }
    int startRow = row - row % 3;
    int startCol = col - col % 3;

    for (int i = 0; i < 3; i++)
    {
        for (int j = 0; j < 3; j++)
        {
            if (puzzle->board[startRow + i][startCol + j] == num)
                return 0;
        }
    }
    return 1;
}
int solveSudoku(Sudoku *puzzle)
{
    puzzle->recursiveCalls++;
    puzzle->currentDepth++;

    if (puzzle->currentDepth > puzzle->maximumDepth)
    {
        puzzle->maximumDepth = puzzle->currentDepth;
    }

    int row, col;

    if (!findEmptyCell(puzzle, &row, &col))
    {
        puzzle->currentDepth--;
        return 1;   // Puzzle solved
    }

    for (int num = 1; num <= 9; num++)
    {
        if (isSafe(puzzle, row, col, num))
        {
            puzzle->board[row][col] = num;
            puzzle->successfulAssignments++;

            if (solveSudoku(puzzle))
            {
                puzzle->currentDepth--;
                return 1;
            }

            puzzle->board[row][col] = 0;
            puzzle->backtracks++;
            puzzle->failedAssignments++;
        }
    }

    puzzle->currentDepth--;
    return 0;
}
int findEmptyCell(const Sudoku *puzzle, int *row, int *col)
{
    for (*row = 0; *row < SIZE; (*row)++)
    {
        for (*col = 0; *col < SIZE; (*col)++)
        {
            if (puzzle->board[*row][*col] == 0)
            {
                return 1;
            }
        }
    }
    return 0;
}
void loadPuzzleFromString(Sudoku *puzzle, const char *str)
{
    int index = 0;

    for (int i = 0; i < SIZE; i++)
    {
        for (int j = 0; j < SIZE; j++)
        {
            puzzle->board[i][j] = str[index++] - '0';
        }
    }
    initializeMetrics(puzzle);
}
void initializeMetrics(Sudoku *puzzle)
{
    puzzle->recursiveCalls = 0;
    puzzle->backtracks = 0;
    puzzle->candidateChecks = 0;
    puzzle->successfulAssignments = 0;
    puzzle->failedAssignments = 0;

    puzzle->currentDepth = 0;
    puzzle->maximumDepth = 0;

    puzzle->emptyCells = countEmptyCells(puzzle);
}

int countEmptyCells(const Sudoku *puzzle)
{
    int count = 0;

    for(int i=0;i<SIZE;i++)
    {
        for(int j=0;j<SIZE;j++)
        {
            if(puzzle->board[i][j]==0)
                count++;
        }
    }

    return count;
}