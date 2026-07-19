def divided_difference_table(x, y):

    n = len(x)

    table = [[0 for _ in range(n)] for _ in range(n)]

    for i in range(n):
        table[i][0] = y[i]

    for j in range(1, n):
        for i in range(n - j):

            numerator = table[i + 1][j - 1] - table[i][j - 1]
            denominator = x[i + j] - x[i]

            table[i][j] = numerator / denominator

    return table

def get_local_points(x, y, value, window=6):
    """
    Select the nearest data points around the target value.

    Parameters:
        x (list): x-values
        y (list): y-values
        value (float): point to interpolate
        window (int): number of neighboring points

    Returns:
        local_x, local_y
    """

    # Pair x and y together
    points = list(zip(x, y))

    # Sort by distance from the target
    points.sort(key=lambda point: abs(point[0] - value))

    # Keep only the nearest points
    nearest = points[:window]

    # Restore ascending x order
    nearest.sort(key=lambda point: point[0])

    local_x = [p[0] for p in nearest]
    local_y = [p[1] for p in nearest]

    return local_x, local_y

def newton_divided_interpolation(x, y, value, window=6):
    """
    Newton Divided Difference using local interpolation.
    """

    local_x, local_y = get_local_points(
        x,
        y,
        value,
        window
    )

    table = divided_difference_table(local_x, local_y)

    result = table[0][0]

    product = 1

    for i in range(1, len(local_x)):

        product *= (value - local_x[i - 1])

        result += table[0][i] * product

    return result
    table = divided_difference_table(x, y)

    result = table[0][0]

    product = 1

    for i in range(1, len(x)):

        product *= (value - x[i - 1])

        result += table[0][i] * product

    return result