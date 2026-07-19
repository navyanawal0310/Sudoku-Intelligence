#include <stdio.h>
#include "dataset.h"

int main()
{
    processDataset(
    "../data/dataset/sudoku_dataset.csv",
    "../data/output/results.csv"
);
    printf("\nDataset processing completed successfully.\n");

    return 0;
}