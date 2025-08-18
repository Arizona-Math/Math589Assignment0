```python
#----------------------------------------------------------------
# File:     solve_quadratic_equation.py
#----------------------------------------------------------------
#
# Author:   Marek Rychlik (rychlik@arizona.edu)
# Date:     Tue Jul 30 09:37:29 2024
# Copying:  (C) Marek Rychlik, 2020. All rights reserved.
#
#----------------------------------------------------------------
# A basic quadratic equation solver. High-school method.

import math


def solve_quadratic_equation(a, b, c):
    """Solve the quadratic equation ``a*x^2 + b*x + c = 0``.

    The implementation prefers numerical stability and always returns real
    roots. A repeated root is represented by ``(root, None)``. Linear
    equations (``a = 0``) are supported as a special case.

    Parameters
    ----------
    a : float
        Coefficient of :math:`x^2`.
    b : float
        Coefficient of :math:`x`.
    c : float
        Constant term.

    Returns
    -------
    tuple
        ``(root1, root2)`` where ``root1`` is the smaller root. ``root2`` is
        ``None`` when the equation has a repeated root or is linear.

    Raises
    ------
    ValueError
        If the equation has complex roots or is degenerate (``a = b = 0``).
    """

    # Handle linear equations first to avoid division by zero.
    if a == 0:
        if b == 0:
            raise ValueError("Not an equation: both 'a' and 'b' are zero")
        return (-c / b, None)

    # Calculate the discriminant
    discriminant = b ** 2 - 4 * a * c
    if discriminant < 0:
        raise ValueError("The equation has complex roots")

    sqrt_discriminant = math.sqrt(discriminant)

    # Check for a repeated root
    if discriminant == 0:
        return (-b / (2 * a), None)

    # Use a numerically stable version of the quadratic formula
    q = -0.5 * (b + math.copysign(sqrt_discriminant, b))
    root1 = q / a
    root2 = c / q

    # Return roots ordered from smallest to largest
    return (min(root1, root2), max(root1, root2))

# Example usage with enhanced testing and edge cases
if __name__ == "__main__":
    test_cases = [
        (1, -3, 2),  # Roots: 1, 2
        (1, 2, 1),   # Repeated root: -1
        (1, 0, -4),  # Roots: -4, 0
        (0, 2, -6),  # Linear case: 3
        (0, 0, 0),   # Degenerate case
    ]

    for a, b, c in test_cases:
        try:
            roots = solve_quadratic_equation(a, b, c)
            print(f"Roots for equation {a}x^2 + {b}x + {c} = 0: {roots}")
        except ValueError as e:
            print(f"Error for equation {a}x^2 + {b}x + {c} = 0: {e}")
```
