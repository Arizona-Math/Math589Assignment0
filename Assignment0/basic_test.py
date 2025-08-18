#----------------------------------------------------------------
# File:     basic_test.py
#----------------------------------------------------------------
#
# Author:   Marek Rychlik (rychlik@arizona.edu)
# Date:     Tue Jul 30 09:36:03 2024
# Copying:  (C) Marek Rychlik, 2020. All rights reserved.
# 
#----------------------------------------------------------------
# A basic unit test with the "unittest framework".

import unittest
import math
import solve_quadratic_equation as quadratic

class MyTestCase(unittest.TestCase):
    def test_easy_case(self):
        a, b, c = 1, -3, 2
        x1, x2 = quadratic.solve_quadratic_equation(a, b, c)
        self.assertAlmostEqual(1, x1)
        self.assertAlmostEqual(2, x2)        

    def test_big_coefficient(self):
        roots = quadratic.solve_quadratic_equation(1, -1000000.001, 1)
        # The function should return the smaller root first and avoid the
        # catastrophic cancellation that occurs for large coefficients.
        self.assertAlmostEqual(1e-6, roots[0], places=12)
        self.assertAlmostEqual(1.0, roots[0] * roots[1], places=6)

    def test_double_root_case(self):
        """Solving a quadratic equation with a repeated root."""
        a, b, c = 1, 2, 1
        x1, x2 = quadratic.solve_quadratic_equation(a, b, c)
        self.assertAlmostEqual(-1, x1)
        self.assertAlmostEqual(None, x2)        
        
    def test_degenerate_quadratic_case(self):
        """Solving a quadratic with a=0."""
        a, b, c = 0, 1, 1
        x1, x2 = quadratic.solve_quadratic_equation(a, b, c)
        self.assertAlmostEqual(-1, x1)
        self.assertIsNone(x2)

    def test_no_real_roots(self):
        """Equation with no real roots should return (None, None)."""
        a, b, c = 1, 0, 1
        x1, x2 = quadratic.solve_quadratic_equation(a, b, c)
        self.assertIsNone(x1)
        self.assertIsNone(x2)

    def test_all_coefficients_zero(self):
        """Equation 0 = 0 is indeterminate; roots are not defined."""
        a, b, c = 0, 0, 0
        x1, x2 = quadratic.solve_quadratic_equation(a, b, c)
        # Assuming the solver returns (None, None) or raises an exception
        self.assertIsNone(x1)
        self.assertIsNone(x2)

    def test_linear_equation_zero_root(self):
        """Linear equation bx + c = 0 with b != 0 and c = 0 should return root 0."""
        a, b, c = 0, 2, 0
        x1, x2 = quadratic.solve_quadratic_equation(a, b, c)
        self.assertAlmostEqual(0, x1)
        self.assertIsNone(x2)

    def test_small_coefficients(self):
        """Test with very small coefficients to check numerical stability."""
        a, b, c = 1e-15, -3e-15, 2e-15
        x1, x2 = quadratic.solve_quadratic_equation(a, b, c)
        self.assertAlmostEqual(1, x1)
        self.assertAlmostEqual(2, x2)

    def test_negative_a_coefficient(self):
        """A negative 'a' coefficient should not affect root calculation."""
        a, b, c = -1, 3, -2
        x1, x2 = quadratic.solve_quadratic_equation(a, b, c)
        self.assertAlmostEqual(1, x1)
        self.assertAlmostEqual(2, x2)

    def test_very_large_and_small_roots(self):
        """Test case with roots differing by many orders of magnitude."""
        a, b, c = 1, -1e8 - 1e-8, 1e0
        x1, x2 = quadratic.solve_quadratic_equation(a, b, c)
        self.assertTrue(abs(x1) < 1e-6 or abs(x2) < 1e-6)
        self.assertTrue(abs(x1) > 1e7 or abs(x2) > 1e7)
