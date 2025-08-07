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
