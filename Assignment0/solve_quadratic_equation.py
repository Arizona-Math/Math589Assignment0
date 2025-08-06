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
    roots.  A repeated root is represented by ``(root, None)``.  Linear
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
        ``(root1, root2)`` where ``root1`` is the smaller root.  ``root2`` is
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

    # Calculate the discriminant and check for real roots
    discriminant = b * b - 4 * a * c
    if discriminant < 0:
        raise ValueError("The equation has complex roots")

    sqrt_discriminant = math.sqrt(discriminant)

    # Repeated root
    if discriminant == 0:
        return (-b / (2 * a), None)

    # Use a numerically stable version of the quadratic formula
    q = -0.5 * (b + math.copysign(sqrt_discriminant, b))
    root1 = q / a
    root2 = c / q

    # Ensure the roots are ordered from smallest to largest
    root1, root2 = (root1, root2) if root1 <= root2 else (root2, root1)
    return (root1, root2)
# Example usage:
# NOTE: Also, as simple testing framework.
if __name__ == "__main__":
    try:
        roots = solve_quadratic_equation(1, -1000000.001, 1)  # Using the earlier example coefficients
        print("Roots:", roots)
    except ValueError as e:
        print("Error:", e)
