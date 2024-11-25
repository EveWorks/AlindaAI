from sympy import symbols, Function, Eq, solve, exp

# Define variables and function
x, y, c = symbols('x y c')
f = Function('f')

# Define the functional equation
eq = Eq(f(x + y), f(x) * f(y))

# Assume f(x) = exp(c * x) (based on the general solution of such equations)
f_exp = exp(c * x)

# Substitute into the equation to verify
solution = eq.subs(f(x), f_exp)

# Output the simplified solution
print(solution.simplify())  # Should verify f(x) = exp(c*x) works
