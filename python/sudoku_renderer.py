import matplotlib.pyplot as plt


def draw_sudoku(board, title="Sudoku Puzzle"):
    """
    Draws a Sudoku board using matplotlib.

    board should be a 9x9 list.
    Empty cells = 0
    """

    fig, ax = plt.subplots(figsize=(6, 6))

    ax.set_xlim(0, 9)
    ax.set_ylim(9, 0)

    # Draw grid
    for i in range(10):

        linewidth = 2.5 if i % 3 == 0 else 0.8

        ax.plot([0, 9], [i, i], color="black", linewidth=linewidth)
        ax.plot([i, i], [0, 9], color="black", linewidth=linewidth)

    # Draw numbers
    for row in range(9):
        for col in range(9):

            value = board[row][col]

            if value != 0:
                ax.text(
                    col + 0.5,
                    row + 0.5,
                    str(value),
                    ha="center",
                    va="center",
                    fontsize=18,
                    fontweight="bold"
                )

    ax.set_xticks([])
    ax.set_yticks([])

    ax.set_title(title, fontsize=18)

    return fig