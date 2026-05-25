![Python logo](../picture_python_logo.png?scale=0.75)

# From Syntax to Solution: Basic Applications of Python to Data Science

## DLSU Data Science Society Python Workshop

<br/>Engr. Jaydee N. Lucero<br/>
Senior Structural Engineer I, Abinales Associates Engineers + Consultants<br/>
May 27, 2026

---

## Hi! I'm Jaydee.

- *Senior Structural Engineer I* (2021-present), Abinales Associates Engineers + Consultants
- *Part-time Review Instructor* (2019-present), Review Innovations
- *Associate Member* (2022-present), Association of Structural Engineers of the Philippines, Inc.
- *MS Civil Engineering (Structural Engineering) student* (2024-present), University of the Philippines Diliman
- `Pythonista since August 2024`

|||

![Jaydee Lucero](../picture_aboutme.png?scale=1.3)

---

## Outline

### Part One: Some Python stuff (90 minutes)

1. Why write in Python?
2. Writing Python syntax
3. Writing code Pythonically: *list comprehensions*
4. Writing faster code: *lists* vs. *sets* vs. *dictionaries* vs. *numpy arrays*
5. Writing functions that take in functions
6. Writing code using the "Big 3" libraries
   - *numpy*
   - *pandas*
   - *matplotlib*

### Part Two: Some Python examples (40 minutes)

7. Example: rebound hammer test results

---

## QR Codes

`Live codes for this talk`

![Google Colab QR Code](../qrcode_googlecolab.png?scale=1.2)

|||

`Python 3.14 cheat sheet`

![Python 3.14 cheat sheet QR Code](../qrcode_cheatsheet.png?scale=1.2)


---

# Part 1

**Why write in Python?**

---

## Why write in Python?

`[Python website](https://www.python.org/about/)`

- Python is powerful.
- Python is fast.
- Python plays well with others.
- Python runs everywhere.
- Python is friendly.
- Python is easy to learn.
- Python is open[-source].

|||

![Python logo](../picture_python_logo.png?scale=1.2)

---

## Why write in Python?

`[Python website](https://www.python.org/about/)`

- Python is powerful.
- Python is fast.
- Python plays well with others.
- Python runs everywhere.
- Python is friendly.
- `Python is easy to learn.`
- Python is open[-source].

|||
<!-- incremental -->
A C program to determine the maximum value in an array

```c
#include <stdio.h>

int main(void) {
    int arr[] = {3, 1, 6, 4};
    int n = 4;
    int max = arr[0];
    int i;
    
    for(i = 1; i < n; i++)
        if(arr[i] > max)
            max = arr[i];
    
    printf("max =  %d\n", max);
    return 0;
}
```

<!-- incremental -->
Equivalent Python program

```python
arr = [3, 1, 6, 4]
print(max(arr))
```

---

## Why write Python?

`[Python website](https://www.python.org/about/)`

- Python is powerful.
- Python is fast.
- Python plays well with others.
- `Python runs everywhere.`
- Python is friendly.
- Python is easy to learn.
- Python is open[-source].

|||

`[TIOBE Index, April 2026](https://www.tiobe.com/tiobe-index/)`

| Rank | Language   | Rating |
| ---- | --------   | ------ |
| 1    | Python     | 20.97% |
| 2    | C          | 12.34% |
| 3    | C++        | 8.03%  |
| 4    | Java       | 7.79%  |
| 5    | C#         | 5.98%  |
| 6    | Javascript | 3.11%  |
| 7    | VB         | 3.02%  |
| 8    | SQL        | 1.75%  |
| 9    | R          | 1.62%  |

---

## Why write in Python?

### Python is powerful.

Some of the Python libraries that we need in data science.

col_widths=80,300
| Library | Function |
| --- | --- |
| numpy   | arrays, fast math, linear algebra |
| scipy   | numerical math, stats, regression |
| scikit-learn   | machine learning applications |
| pandas  | data extraction, cleaning, analysis |
| matplotlib | data visualization |

---

# Part 2

**Writing Python syntax**

---

## Variables and data types

<!-- incremental -->

We can declare a variable in the same way we do in math.

<!-- incremental -->

```python
age = 29
```

<!-- incremental -->

Variables can hold any type of data possible, some of which are enumerated below.

<!-- incremental -->

```python
name         = "Airis"                      # string
gender       = 'F'                          # character
age          = 21                           # integer
money        = 125.36                       # float (decimal number)
is_single    = True                         # boolean
has_dogs     = None                         # the None keyword
siblings     = ["Eris", "Erin", "Erina"]    # list
siblings_age = (36, 25, 18)                 # tuple
parents      = {                            # dictionary
    "mother"        : "Airin",
    "mother_age"    : 50,
    "father"        : "Erik",
    "father_age"    : None
}

```

---

## Program output

Texts and variable values can be displayed using the `print` function.

```python
print("Hello world!")    # displays "Hello world!"
print(money)             # displays the value of the variable money
```

They can even be combined together using either
- the `.format` function
```python
print("Hello world! I'm {0} and my money is Php{1}.".format(name, money))
```
- or, f-strings
```python
print(f"Hello world! I'm {name} and my money is Php{money}.")
```
---

## Mathematics and library imports

You can do some simple math calculations in Python.

```python
print(3 + 5 - 3 * 5)    # addition, subtraction, multiplication
print(3 / 5)            # float division    (3/5 = 0.6)
print(3 // 5)           # integer division  (3/5 = 0 remainder 3, so 0)
print(3 % 5)            # remainder         (3/5 = 0 remainder 3, so 3)
print(3 ** 5)           # exponents         (3^5 = 243)
print(max(3, 5))        # maximum value
print(min(3, 5))        # minimum value
```

More advanced math functions require the `math` library. Import and use using

```python
import math
print(math.sqrt(25))    # square root
```

We can import only select functions from a specific library.

```python
from math import sqrt   # import just the square root function
print(sqrt(25))
```

Or import all functions in that library using
```python
from math import *      # import everything
print(sqrt(25))
```

---

## Control statements and loops

Check multiple conditions using `if...elif...else`.

```python
age = 29

if age < 18 :
    print("This person is a minor.")
elif 18 <= age < 65 :
    print("This person is an adult.")
else :
    print("This person is a senior citizen.")
```

Do repetitive operations using loops.

```python
sum = 0
for num in range(1, 101) :
    sum += num
print(sum)      # 5050, the sum of the first 100 positive integers
```

We can also combine conditions and repetitive operations using `while`.

---

## The `numpy` library


```python
import numpy as np
```
<!-- incremental -->
*for* loops and list comprehensions are slow when creating array-like objects.
<!-- incremental -->
```python
import time

t_start = time.time()
result = [x**2 for x in range(1_000_000)]
t_end = time.time()
print(round(t_end - t_start, 4))          # 0.1069 seconds
```
<!-- incremental -->
*numpy* arrays can make the same instruction `several times faster`.
<!-- incremental -->
```python
import time
import numpy as np

t_start = time.time()
result = np.arange(1_000_000) ** 2
t_end = time.time()
print(round(t_end - t_start, 4))          # 0.0213 seconds
```

---

## The numpy library

### Example 1

Solve the system of linear equations

5x + 3y + 2z = 15<br/>2x - 6y - 7z = -22<br/>4x - 8y + 3z = 9

using

1. matrix inverse method,
2. Cramer's rule, and
3. *numpy*'s own solver function.

---

## The numpy library
### Solution to #1

<!-- incremental -->

```python
import numpy as np

A = [[5, 3, 2], [2, -6, -7], [4, -8, 3]]
B = [15, -22, 9]
```

<!-- incremental -->

Iterators like lists and tuples can be converted to *numpy* arrays.

```python
A = np.array(A, dtype='float')
B = np.array(B, dtype='float')
```

<!-- incremental -->

Check if the system has a unique solution by finding the rank of A.

```python
A_rank = np.linalg.matrix_rank(A)   # matrix rank
print(rf"rank(A) = {A_rank}")       # rank(A) = 3
```

<!-- incremental -->

Now, solve the system using `AX = B --> X = A^-1 B`.

```python
A_inv = np.linalg.inv(A)            # matrix inverse
X = A_inv @ B                       # matrix multiplication
print(rf"X = {X} using matrix inverse method.")    
# X = [1.40570175 0.68640351 2.95614035] using matrix inverse method.
```

---

## The numpy library
### Solution to #2

<!-- incremental -->

Copy the coefficients matrix A by value.

```python
A_x = np.copy(A)
A_y = np.copy(A)
A_z = np.copy(A)
```

<!-- incremental -->

Replace each column in the coefficients matrix with the constants vector.

```python
print(A)        # [[ 5,  3,  2], [  2,  -6,  -7], [4, -8, 3]]
A_x[:, 0] = B   # [[15,  3,  2], [-22,  -6,  -7], [9, -8, 3]]
A_y[:, 1] = B   # [[ 5, 15,  2], [  2, -22,  -7], [4,  9, 3]]
A_z[:, 2] = B   # [[ 5,  3, 15], [  2,  -6, -22], [4, -8, 9]]
```

<!-- incremental -->

Next, calculate the required determinants.

```python
D = np.linalg.det(A)            # determinant
D_x = np.linalg.det(A_x)
D_y = np.linalg.det(A_y)
D_z = np.linalg.det(A_z)
```

---

## The numpy library
### Solution to #2 (continued)

<!-- incremental -->

Now, solve the system using `X = D_x/D, Y = D_y/D, Z = D_z/D`.

```python
X = np.array([D_x/D, D_y/D, D_z/D], dtype='float')  # solve the system
print(rf"X = {X} using Cramer's rule.")
# X = [1.40570175 0.68640351 2.95614035] using Cramer's rule.
```

<!-- incremental -->

### Solution to #3

<!-- incremental -->

*numpy* also has a function to solve linear systems directly. It uses [LU decomposition](https://www.netlib.org/lapack/explore-html/d8/da6/group__gesv.html) at its base.

```python
X = np.linalg.solve(A, B)
print(rf"X = {X} using numpy's own solver.")
# X = [1.40570175 0.68640351 2.95614035] using numpy's own solver.
```

---

# Part 3
**The `scipy`, `sympy` and `matplotlib` libraries**

---

## Numerical and symbolic computing

### Example 2

1. (MMC/2013) How many real solutions are there in the equation sin(x) = x^2?
2. Find the area between the curves y = sin(x) and y = x^2.

```pyxel-graph
width=160
height=110
bg=9
border=14
x=-2,2
y=-1.2,4.2
grid=true
plot sin(x) color=2
plot x^2 color=5
```

|||

<!-- incremental -->

`Solution outline`

<!-- incremental -->
1. Determine the number of solutions graphically.
<!-- incremental -->
2. Find the exact values of the solutions.
<!-- incremental -->
3. Calculate the area between the curves using any of the four methods.
<!-- incremental -->
  - Using trapezoidal rule
  <!-- incremental -->
  - Using Simpson's one-third rule
  <!-- incremental -->
  - Using Gaussian quadrature
  <!-- incremental -->
  - Using symbolic integration

---

## The `matplotlib` library

### Solution to #1
<!-- incremental -->
We use *matplotlib.pyplot* to graph the left and right sides of the equation and visually count the number of intersections.

```python
import numpy as np
import matplotlib.pyplot as plt
```
<!-- incremental -->
Generate a numpy array of 200 items of equal spacing from -pi to pi.
```python
x = np.linspace(-np.pi, np.pi, 200)
```
<!-- incremental -->
Create a figure and axis.
```python
fig, ax = plt.subplots()
```
<!-- incremental -->
Plot the functions.
```python
ax.plot(x, np.sin(x), label=rf"$f(x) = \sin x$")
ax.plot(x, x**2, label=rf"$g(x) = x^2$")
```

---
## The `matplotlib` library
### Solution to #1 (continued)
<!-- incremental -->
Add grid and axis lines.
```python
ax.axhline(0, color='black')
ax.axvline(0, color='black')
```
<!-- incremental -->
Set labels and title.
```python
ax.set_xlabel(rf"$x$")
ax.set_ylabel(rf"$y$")
ax.set_title(rf"Solutions to the equation $\sin x = x^2$")
```
<!-- incremental -->
Add legend and grid.
```python
ax.legend()
ax.grid()
```
<!-- incremental -->
Show the plot. `Note: Not required in a Jupyter notebook.`
```python
plt.show()
```

---
## The `scipy` library
### Solution to #1 (continued)

<!-- incremental -->
*scipy*'s `scipy.optimize.fsolve()` function is a wrapper to a [Fortran subroutine](https://www.netlib.org/minpack/hybrd.f) that uses a modification of [Powell hybrid method](https://en.wikipedia.org/wiki/Powell%27s_dog_leg_method) to solve nonlinear equations.

<!-- incremental -->
```python
import numpy as np
from scipy.optimize import fsolve
```

<!-- incremental -->
Write the equation as a function `f(x) = left side - right side = 0`.
```python
eqn = lambda x : np.sin(x) - x**2
```

<!-- incremental -->
Solve the equation. Multiple guess values can be fed to find multiple solutions.
```python
roots = fsolve(eqn, [-0.05, 1])
print(roots)    # [4.50822753e-14 8.76726215e-01]
```

---
## The `scipy` library
### Solution to #2
<!-- incremental -->
*scipy*'s `scipy.integrate` contains many methods for numerical integration.
<!-- incremental -->
- trapezoidal rule: `I = (h/2)(y_0 + 2y_1 + ... + 2y_(n-1) + y_n)`
<!-- incremental -->
- Simpson's one-third rule: `I = (h/3)(y_0 + 4y_1 + 2y_2 + ... + 2y_(n-2) + 4y_(n-1) + y_n)`
<!-- incremental -->
```python
import numpy as np
from scipy.integrate import trapezoid, simpson
```
<!-- incremental -->
Divide the region into 100 points.
```python
x = np.linspace(roots[0], roots[1], 100)
y = eqn(x)     # Calculate f_upper - f_lower = sin(x) - x^2
```
<!-- incremental -->
Calculate the integral.
```python
print(rf"A = {trapezoid(y, x)} by trapezoidal rule.")   # 0.13568369268723793
print(rf"A = {simpson(y, x)} by Simpson's rule.")       # 0.13569750707724645
```

---

## The `scipy` library
### Solution to #2 (continued)
<!-- incremental -->
*scipy*'s `scipy.integrate.quad()` function uses 21-point [Gauss-Kronrod quadrature](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.quad.html) to numerically evaluate integrals.

```python
from scipy.integrate import quad
```
<!-- incremental -->
`quad` requires three arguments: the integrand, and the lower and upper bounds of the integral. It returns two items: the value of the integral, and the error parameters.

```python
# *iterable unpacks a list or a tuple into comma-separated items.
# In the below example, *roots = *[roots[0], roots[1]] = roots[0], roots[1].
print(rf"A = {quad(eqn, *roots)[0]} by scipy quadrature.")    # 0.1356975072306028
```

---

## The `sympy` library
### Solution to #2 (continued)
<!-- incremental -->
*sympy* is a library used for symbolic mathematics, similar to Mathematica or Maple.

```python
import sympy as sp
```
<!-- incremental -->
Specify the symbolic variable.
```python
x = sp.symbols("x")
```
<!-- incremental -->
Construct the equation or function based on that symbolic equation.

```python
eqn = sp.sin(x) - x**2
```
<!-- incremental -->
*sympy* also has `solve()` function for symbolic solutions of equations, and `nsolve()` for numerical solutions.

```python
root_1 = sp.nsolve(eqn, x, 0)
root_2 = sp.nsolve(eqn, x, 1)
```

---
## The `sympy` library
### Solution to #2 (continued)
<!-- incremental -->
Symbolically evaluate the definite integral.
```python
print(rf"A = {sp.integrate(eqn, (x, root_1, root_2))} by symbolic integration.")
# 0.135697507230603
```
---

# Part 4

**The `pandas` library**

---

## The `pandas` library
### Example 3

Given the population of the Philippines from 1840 to 2024 [based on national census](https://psa.gov.ph/system/files/psy/2025_T1_4.xlsx), answer the following questions.

1. The population growth of a certain country is said to be *sustainable* if the annual growth rate is between [0.5% and 1.2%](https://philarchive.org/archive/MALTIP-2). List out the years in which the population growth of the Philippines was sustainable.
2. Based from the provided population data, calculate the average annual growth rate in percent for each listed year.
3. Based from the provided annual growth rate, calculate the maximum and minimum growth rate, and the respective years in which they occurred.

---

## The `pandas` library

*pandas* is a Python library used for data analysis.

<!-- incremental -->
```python
import pandas as pd
```

<!-- incremental -->
*pandas* can import Excel and CSV files.

```python
ph_population = pd.read_excel("2025_T1_4.xlsx")
```
<!-- incremental -->
Imported data can sometimes contain invalid data like `NaN` (not a number) or `None` values. `dropna()` can be used to remove these values.

```python
ph_population = ph_population.dropna()
```
<!-- incremental -->
Like lists or *numpy* arrays, we can specify the rows that we will get as data.

```python
ph_population = ph_population[1:]    # Exclude the first row (i.e. index 0).
```
<!-- incremental -->
`.columns` can be used to specify the column names.

```python
ph_population.columns = ["Year", "Population", "Annual Growth Rate (%)", "Source"]
```

---

## The `pandas` library

### Solution to #1

<!-- incremental -->
We can filter the data by specifying conditions within square brackets.

```python
sustainable = ph_population[ph_population["Annual Growth Rate (%)"] >= 0.5]
sustainable = ph_population[ph_population["Annual Growth Rate (%)"] <= 1.2]
```
<!-- incremental -->
We can also specify which columns will be considered.
```python
print(sustainable[["Year", "Annual Growth Rate (%)"]])
```
<!-- incremental -->
| Year | Annual Growth Rate (%) |
|------|------------------------|
| 1870 | 0.78                   |
| 1887 | 0.72                   |
| 1896 | 0.5                    |
| 2024 | 0.8                    |

---

## The `pandas` library
### Solution to #2

<!-- incremental -->
`.diff()` calculates the difference between consecutive values.

```python
ph_population["Annual Increase"] = ph_population["Population"].diff()/ \
                                                            ph_population["Year"].diff()
```
<!-- incremental -->
`.shift()` shifts the values in a column by a specified number of periods.
```python
ph_population["Calculated Rate (%)"] = ph_population["Annual Increase"]/ \
                                              ph_population["Population"].shift(1) * 100
```
<!-- incremental -->
Show only the last two rows.
```python
print(ph_population[["Year", "Population", "Annual Increase", 
                                                           "Calculated Rate (%)"]][-2:])
```
<!-- incremental -->
| Year | Population | Annual Increase | Calculated Rate (%) |
|------|------------|-----------------|---------------------|
| 2020 | 109033245  | 1610788.4       | 1.595167            |
| 2024 | 112729484  | 924059.75       | 0.847503            |

---
## The `pandas` library
### Solution to #3
<!-- incremental -->
Some statistical measures that can be computed using *pandas* are `max()`, `min()`, `mean()`, `median()`, `std()`, `count()` and `sum()`.
```python
# Maximum and minimum annual growth rates.
print(ph_population["Annual Growth Rate (%)"].max())    # 3.08
print(ph_population["Annual Growth Rate (%)"].min())    # 0.5
```
<!-- incremental -->
`.idxmax()` and `.idxmin()` returns the index numbers of the maximum and minimum values, respectively.
<!-- incremental -->
<br/>Using that index, we can retrieve the corresponding row using `.loc[]`.

```python
# Year with which they respectively occurred.
print(ph_population.loc[ph_population["Annual Growth Rate (%)"].idxmax(), "Year"]) # 1970
print(ph_population.loc[ph_population["Annual Growth Rate (%)"].idxmin(), "Year"]) # 1896
```
---

## The `pandas` library
### EXTRA: From tables to graphs
<!-- incremental -->
`.to_numpy()` converts a pandas Series to a *numpy* array.

```python
import matplotlib.pyplot as plt

year = ph_population["Year"].to_numpy(dtype='float')
population = ph_population["Population"].to_numpy(dtype='float')
```
<!-- incremental -->
From this, we can plot the data using *matplotlib*.

```python
# A vertical bar plot
fig, ax = plt.subplots()
ax.bar([str(y) for y in year], population)   # Convert years from numbers to strings
ax.tick_params("x", rotation=90)             # Rotate x-axis labels by 90 degrees
ax.set_xlabel(ph_population.columns[0])      # Set x-axis label
ax.set_ylabel(ph_population.columns[1])      # Set y-axis label
ax.set_title("Philippine Population (PSA Census Data)")  # Set plot title
```

---

## The `pandas` library
### EXTRA: From tables to graphs
<!-- incremental -->
Several plots can be placed in a single figure using `plt.subplots()`.
```python
fig, ax = plt.subplots(1, 4)                 # Set up 4 subplots in a row
fig.set_size_inches(24, 6)                   # Set the overall figure size

for i, cur_col in enumerate((1, 2, 4, 5)) :  # Loop through the columns we want to plot
    # Plot the data
    ax[i].plot(year, ph_population[ph_population.columns[cur_col]], 'ro-', linewidth=2)

    # Set the axis labels
    ax[i].set_xlabel(ph_population.columns[0])
    ax[i].set_ylabel(ph_population.columns[cur_col])

    # Set the title
    ax[i].set_title(ph_population.columns[cur_col])
```
---

## The `pandas` library
### EXTRA: Regression analysis
<!-- incremental -->
`scipy.optimize.curve_fit()` function can be used to construct regression models from given data. 

```python
from scipy.optimize import curve_fit

lin_curve = lambda x, A, B : A + B * x       # linear regression equation y = A + Bx
pow_curve = lambda x, A, B : A * B ** x      # power regression equation y = A * B^x

lin_params, _ = curve_fit(lin_curve, year, population)   # fit linear curve to data
pow_params, _ = curve_fit(pow_curve, year, population)   # fit power curve to data

# Plot the data and the resulting regression curves.
fig, ax = plt.subplots()
ax.scatter(year, population)
ax.plot(year, lin_curve(year, *lin_params), linestyle='dashed', color='red',
               label=rf"population = {lin_params[0]:.2f} + {lin_params[1]:.2f} * year")
ax.plot(year, pow_curve(year, *pow_params), linestyle='dashed', color='green',
               label=rf"population = {pow_params[0]:.2f} * {pow_params[1]:.2f}^x")
ax.set_xlabel("Year")
ax.set_ylabel("Population")
ax.legend()
```

---

## The `pandas` library
### EXTRA: Regression analysis

<!-- incremental -->
`scipy.optimize.curve_fit()` does not have a direct function to calculate R^2 values. So, we have to construct it ourselves.

<!-- incremental -->
```python
# Calculate R^2 value
def r_squared(y_actual, y_calculated) :
    residuals = y_actual - y_calculated
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y_actual - np.mean(y_actual))**2)
  
    return 1 - ss_res/ss_tot

# Linear curve
r_squared_linear = r_squared(population, lin_curve(year, *lin_params))
print(rf"R^2 = {r_squared_linear:.2f} for linear curve")

# Power curve
r_squared_power = r_squared(population, pow_curve(year, *pow_params))
print(rf"R^2 = {r_squared_power:.2f} for power curve")
```
<!-- incremental -->
An alternative to *scipy* for regression analysis is *scikit-learn*.

---

# Part 4
** A famous math example **

---

## A famous math example
### Example 4

Random points (x, y) are placed in the Cartesian plane such that 0 <= x, y <= 1. Estimate the value of pi.

```pyxel-canvas
width=152
height=152
bg=0
border=0
rect 16 16 121 121 color=14 fill=0
area 16,136 136,136 134,115 129,95 120,76 108,59 93,44 76,32 57,23 37,18 16,16 fill=12 color=12
curve 136,136 136,70 82,16 16,16 color=4 steps=48
line 16 136 136 136 color=14
line 16 16 16 136 color=14
point 39 102 color=2 size=2
point 30 99 color=2 size=2
point 53 114 color=2 size=2
point 84 48 color=2 size=2
point 41 75 color=2 size=2
point 35 19 color=2 size=2
point 54 75 color=2 size=2
point 96 96 color=2 size=2
point 73 28 color=5 size=2
point 82 111 color=2 size=2
point 123 102 color=2 size=2
point 48 75 color=2 size=2
point 90 48 color=2 size=2
point 46 133 color=2 size=2
point 31 57 color=2 size=2
point 28 100 color=2 size=2
point 44 19 color=5 size=2
point 30 48 color=2 size=2
point 131 28 color=5 size=2
point 36 71 color=2 size=2
point 67 17 color=5 size=2
point 130 99 color=2 size=2
point 114 122 color=2 size=2
point 65 74 color=2 size=2
point 118 94 color=2 size=2
point 67 66 color=2 size=2
point 131 50 color=5 size=2
point 128 43 color=5 size=2
point 80 106 color=2 size=2
point 120 21 color=5 size=2
point 131 33 color=5 size=2
point 55 87 color=2 size=2
point 58 135 color=2 size=2
point 61 70 color=2 size=2
point 22 33 color=2 size=2
point 100 58 color=2 size=2
point 109 131 color=2 size=2
point 87 121 color=2 size=2
point 35 37 color=2 size=2
point 39 34 color=2 size=2
point 47 29 color=2 size=2
point 98 105 color=2 size=2
text 20 142 "inside=34/42  pi~3.24" color=1
```

|||

<!-- incremental -->
`Solution`
<!-- incremental -->
- A(square) = 1^2 = 1
<!-- incremental -->
- A(quarter-circle) = (1/4)(pi * 1^2) = pi/4
<!-- incremental -->
- A(quarter-circle) / A(square) = (pi/4) / 1 = pi/4
<!-- incremental -->
- pi = 4 * A(quarter-circle) / A(square)<br/>= `4 * N(points in quarter-circle) / N(points in square)`

---

# Part 5
**Next steps**

---

## Next steps

1. Create your Github account.
<!-- incremental -->
2. Read the library documentation **a lot**.
<!-- incremental -->
3. Stop coding examples. Start building your own projects.
<!-- incremental -->
4. Feel free to make mistakes.
<!-- incremental -->
5. Feel free to ask questions.
<!-- incremental -->
6. When using AI, `always` verify the results.
<!-- incremental -->
7. Find your desired specialization (e.g. actuarial science, finance, AI/ML, software and game development, etc).
<!-- incremental -->
8. Join a community (e.g. Reddit, Discord, community groups, etc).
<!-- incremental -->
9. Continue learning.

---

## Closing

This presentation was created using a heavily modified version of [Pyxel slides](https://github.com/shimizukawa/pyxel-slide-pyasia-2026), which I learned at PythonAsia 2026 from the presentation of [Takayuki Shimizukawa](https://github.com/shimizukawa). Special thanks to Shimizukawa-sensei for creating such an amazing tool!

`Contact me`

- Email: [jaydee.lucero@gmail.com](mailto:jaydee.lucero@gmail.com)
- Facebook: [facebook.com/jaydee.lucero](https://www.facebook.com/jaydee.lucero)
- Linkedin: [linkedin.com/in/jaydee-lucero-977070200](https://www.linkedin.com/in/jaydee-lucero-977070200)
- Github: [github.com/arisa-chan](https://github.com/arisa-chan)
- Website: [engrjaydee.com](https://engrjaydee.com/)

|||

`PDF and source code of presentation`

![Github repository](../qrcode_presentation.png?scale=1.2)

---

# Thank you very much!

**Do you have any questions?**


