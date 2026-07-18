#include <stdio.h>
#include "solver.h"

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