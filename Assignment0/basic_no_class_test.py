#----------------------------------------------------------------
# File:     basic_no_class_test.py
#----------------------------------------------------------------
#
# Author:   Marek Rychlik (rychlik@arizona.edu)
# Date:     Tue Jul 30 09:35:11 2024
# Copying:  (C) Marek Rychlik, 2020. All rights reserved.
# 
#----------------------------------------------------------------
# A basic test file without classes
import solve_quadratic_equation as quadratic

def test_something():
    roots = quadratic.solve_quadratic_equation(1, -1000000.001, 1)
    # The smaller root is returned first.  Its magnitude is around 1e-6 and
    # the product of both roots should equal ``c/a`` which is 1.
    assert abs(1e-6 - roots[0]) < 1e-12
    assert abs(roots[0] * roots[1] - 1.0) < 1e-6

