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
    """
    Solve the quadratic equation a*x^2 + b*x + c = 0 using the standard quadratic formula.
    
    This function calculates the roots using the basic quadratic formula without any adjustments
    for numerical stability. It assumes real coefficients and only returns real roots.

    Parameters:
    a (float): Coefficient of x^2.
    b (float): Coefficient of x.
    c (float): Constant term.

    Returns:
    tuple:
    - (float): The first root.
    - (float or None): The second root, or None if there is only one distinct root due to a zero discriminant.

    Raises:
    """
    # Calculate the discriminant
    discriminant = b**2 - 4*a*c

    # Calculate the discriminant's square root
    sqrt_discriminant = math.sqrt(discriminant)

    # Compute both roots using the standard quadratic formula
    root1 = (-b + sqrt_discriminant) / (2 * a)
    root2 = (-b - sqrt_discriminant) / (2 * a)

    return (root1, root2)
# Example usage:
# NOTE: Also, as simple testing framework.
if __name__ == "__main__":
    try:
        roots = solve_quadratic_equation(1, -1000000.001, 1)  # Using the earlier example coefficients
        print("Roots:", roots)
    except ValueError as e:
        print("Error:", e)
