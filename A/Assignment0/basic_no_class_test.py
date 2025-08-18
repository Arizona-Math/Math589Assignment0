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
    # print("Testing without classes/unittest, indeed...")
    assert( abs(1000000 -  roots[0] ) < 1e-7 )

