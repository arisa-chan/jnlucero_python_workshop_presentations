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

1. Writing in Python: why?
2. Writing Python syntax
3. Writing code Pythonically
4. Writing faster code
5. Writing functions that take in functions
6. Writing code using the "Big 3" libraries
7. Writing the next steps

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

`[TIOBE Index, May 2026](https://www.tiobe.com/tiobe-index/)`

| Rank | Language   | Rating |
| ---- | --------   | ------ |
| 1    | Python     | 19.98% |
| 2    | C          | 11.55% |
| 3    | Java       | 7.94%  |
| 4    | C++        | 7.92%  |
| 5    | C#         | 5.41%  |
| 6    | Javascript | 3.08%  |
| 7    | VB         | 2.90%  |
| 8    | R          | 1.77%  |
| 9    | SQL        | 1.57%  |

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
name            = "Airis"                      # string
gender          = 'F'                          # character
age             = 21                           # integer
money           = 125.36                       # float (decimal number)
is_single       = True                         # boolean
has_dogs        = None                         # the None keyword
siblings        = ["Eris", "Erin", "Erina"]    # list
siblings_age    = (36, 25, 18)                 # tuple
siblings_gender = {'F', 'F', 'F'}              # set
parents         = {                            # dictionary
    "mother"        : "Airin",
    "mother_age"    : 50,
    "father"        : "Erik",
    "father_age"    : None
}

```

---

## Program output

<!-- incremental -->
Texts and variable values can be displayed using the `print` function.

<!-- incremental -->
```python
print("Hello world!")    # displays "Hello world!"
print(money)             # displays the value of the variable money
```

<!-- incremental -->
They can even be combined together using either

<!-- incremental -->
- the `.format` function
<!-- incremental -->
```python
print("Hello world! I'm {0} and my money is Php{1}.".format(name, money))
```
<!-- incremental -->
- or, f-strings
<!-- incremental -->
```python
print(f"Hello world! I'm {name} and my money is Php{money}.")
```
---

## Mathematics and library imports

<!-- incremental -->
You can do some simple math calculations in Python.

<!-- incremental -->
```python
print(3 + 5 - 3 * 5)    # addition, subtraction, multiplication
print(3 / 5)            # float division    (3/5 = 0.6)
print(3 // 5)           # integer division  (3/5 = 0 remainder 3, so 0)
print(3 % 5)            # remainder         (3/5 = 0 remainder 3, so 3)
print(3 ** 5)           # exponents         (3^5 = 243)
print(max(3, 5))        # maximum value
print(min(3, 5))        # minimum value
```

<!-- incremental -->
More advanced math functions require the `math` library. Import and use using

<!-- incremental -->
```python
import math
print(math.sqrt(25))    # square root
```

<!-- incremental -->
We can import only select functions from a specific library.

<!-- incremental -->
```python
from math import sqrt   # import just the square root function
print(sqrt(25))
```

<!-- incremental -->
Or import all functions in that library using

<!-- incremental -->
```python
from math import *      # import everything
print(sqrt(25))
```

---

## Control statements and loops

<!-- incremental -->
Check multiple conditions using `if...elif...else`.

<!-- incremental -->
```python
age = 29

if age < 18 :
    print("A minor.")
elif 18 <= age < 65 :
    print("An adult.")
else :
    print("A senior citizen.") # An adult.
```

<!-- incremental -->
Do repetitive operations using loops.

<!-- incremental -->
```python
# Calculate the sum of the first 100
# positive integers.
sum = 0

for num in range(1, 101) :
    sum += num

print(sum)    # 5050
```

|||

<!-- incremental -->
We can also combine conditions and repetitive operations using `while`.

<!-- incremental -->
```python
# Another way to calculate the sum of the
# first 100 positive integers.
sum = 0

current_num = 1
while current_num <= 100 :
    sum += num
    current_num += 1
print(sum)    # 5050
```

<!-- incremental -->
or

<!-- incremental -->
```python
sum = 0

current_num = 1
while True :
    sum += num
    if current_num > 100 :
        break
print(sum)    # 5050
```

---

## Lists, tuples, dictionaries

<!-- incremental -->
Accesss the elements in lists and tuples using

<!-- incremental -->
```python
# index  0,  1,  2,  3 
# index -4, -3, -2, -1
a =    [ 1,  2,  3,  4]
print(a[1])                      # 2
print(a[-2])                     # 3

```

<!-- incremental -->
and for dictionaries,

<!-- incremental -->
```python
person = {
    "name" : "James",
    "age"  : 41
}
print(person["name"])            # James
```

<!-- incremental -->
You can also access multiple elements at once using the `:` symbol.

<!-- incremental -->
```python
# from index 1 (included) to 3 (excluded)
print(a[1:3])                    # [2, 3]
```

|||

<!-- incremental -->
Modify elements in lists using
<!-- incremental -->
```python
a[1] = 100
print(a)                # [1, 100, 3, 4]
```
<!-- incremental -->
and in dictionaries using
<!-- incremental -->

```python
person["age"] += 1
print(person["age"])    # 42
```

<!-- incremental -->
You can't do that on tuples though since they're immutable.

<!-- incremental -->
```python
b = (1, 2, 3, 4, 5)
b[2] = 100
# TypeError: 'tuple' object does not 
# support item assignment
```

<!-- incremental -->
Add new elements to lists using

<!-- incremental -->
```python
a.append(200)
print(a)            # [1, 100, 3, 4, 200]
```

---

# Part 3
**Write code Pythonically**

---

## Writing code Pythonically

<!-- incremental -->
==**Example 1**== Find the sum of the first 100 positive perfect square numbers.

<!-- incremental -->
==Manual computation==

1^2 + 2^2 + ... + n^2 = n(n + 1)(2n + 1)/6<br/>
1^2 + 2^2 + ... + 100^2 = 100(100 + 1)[2(100) + 1]/6 = `338350`

<!-- incremental -->
==Solution 1== using `for` loops

```python
total = 0
for n in range(1, 100 + 1) :
  total += n**2
print(total)
```

<!-- incremental -->
==Solution 2==

```python
print(sum([n**2 for n in range(1, 100 + 1)]))
```

<!-- incremental -->
> <u>**List comprehensions**</u><br/>`[(1) for (2) in (3) if (4)]` generates a list of items generated by part (1) for each item (2) in the iterable (3) based on conditions set by (4).

---

## Writing code Pythonically

==**Example 2**== Suppose that we have the following record of transactions in US Dollars. Notice that some transactions are corrupted (the amount is either `None` or negative value). We want to determine the total amount of all valid transactions only, converted to Euros using the conversion 1 US Dollar = 0.85 Euro.

<!-- incremental -->
==Solution==

```python
transactions_usd = [10.50, None, -5.00, 25.00, 100.00, None, 12.50]
usd_to_euro = 0.85

total_euros = sum([amount * usd_to_euro for amount in transactions_usd 
                    if amount is not None and amount > 0])
print(total_euros)
```

---

# Part 4
**Write faster code**

---

## Writing faster code

<!-- incremental -->
<u>**Some ways to make code faster**</u>

<!-- incremental -->
- Use `numpy` arrays instead of lists.

<!-- incremental -->
- Use raw iterator objects instead of lists when using all its contents.
<!-- incremental -->
- Use dictionaries instead of lists.
<!-- incremental -->
- Use sets instead of lists.

|||

<!-- incremental -->
*Containment time complexities*

| Data structure | Average | Worst case    |
|:--------------:|:-------:|:-------------:|
| List/Tuple     | O(n)    | O(n)          |
| Dictionary     | O(n)    | O(n)          |
| Set            | O(1)    | O(n)          |

<!-- incremental -->
*Iteration time complexities*

| Data structure | Average | Worst case    |
|:--------------:|:-------:|:-------------:|
| List/Tuple     | O(n)    | O(n)          |
| Dictionary     | O(n)    | O(n)          |
| Set            | O(n)    | O(n)          |

---

## Writing faster code

<!-- incremental -->
### Creating lists

<!-- incremental -->
```python
import time

time_start = time.time()
numbers = [num for num in range(1, int(1e8) + 1)]
time_end = time.time()

print(f"time = {time_end - time_start:.4f} seconds.")    # 1.6669 seconds
```

<!-- incremental -->
### Creating numpy arrays

<!-- incremental -->
```python
import time
import numpy as np

time_start = time.time()
numbers = np.arange(1, int(1e8) + 1)
time_end = time.time()

print(f"time = {time_end - time_start:.4f} seconds.")    # 0.0978 seconds
```

<!-- incremental -->
`About 17 times faster!`

---

## Writing faster code

<!-- incremental -->
### Finding elements in lists

<!-- incremental -->
```python
import time
numbers = [num for num in range(1, int(1e8) + 1)]

time_start = time.time()
number_found = int(1e8) in numbers
time_end = time.time()
print(f"time = {time_end - time_start:.4f} seconds.")    # 0.4242 seconds
```

<!-- incremental -->
### Finding elements in sets

<!-- incremental -->
```python
import time
numbers = set([num for num in range(1, int(1e8) + 1)])

time_start = time.time()
number_found = int(1e8) in numbers
time_end = time.time()
print(f"time = {time_end - time_start:.6f} seconds.")    # 0.000005 seconds
```

<!-- incremental -->
`About 80,000 times faster!`

---

# Part 5
**Functions that take in functions**

---

## Functions as objects

<!-- incremental -->

> <u>**Functions as objects**</u><br/>Function *names* can be inputted as arguments in a function.

<!-- incremental -->
==**Example 3**== Solve the equation e^x = x + 5 using Newton-Raphson method.

<!-- incremental -->
==**Solution**==

```python hl=7
import math

# The equation, expressed as left - right. This should be equal to zero.
eqn = lambda x : math.exp(x) - x - 5

# Define a function that takes an equation (a function) as an argument.
def newton_raphson(func, x0=0, tol=1e-6) :
    xn = x0     # guess value
    h = 1e-6    # marching step for numerical differentiation
    # Check if the equation is close to zero.
    while abs(func(xn)) >= tol :
        d_func = (func(xn + h) - func(xn - h))/(2*h)    # derivative
        xn -= func(xn)/d_func                           # new guess value
    return xn   # root found

print(newton_raphson(eqn, x0=1))        # 1.936847407229323
```

---

## Functions as objects
<!-- incremental -->
### Applications to pandas
<!-- incremental -->

> <u>**The pandas apply function**</u><br/>`[pandas Series].apply([function])` takes a *pandas* Series, feeds its contents one by one into a function, then returns a new *pandas* Series.
<!-- incremental -->
==**Example 4**== UP Diliman implements the following honorific scholarships based on the general weighted average (GWA) of a student for a given semester.

| Item                    | Range                         |
|:-----------------------:|:-----------------------------:|
| University Scholar (US) | GWA <= 1.45                   |
| College Scholar (CS)    | 1.45 < GWA <= 1.75            |
| No scholarship          | GWA > 1.75                    |

Given a *pandas* DataFrame of students and their corresponding GWA for a specific semester, output the honorific scholarship of each student.

---

## Functions as objects
### Applications to pandas
==**Solution**==

```python hl=17
import pandas as pd

data = {
  "Students" : ["Jinx", "Lux", "Ahri", "Annie", "Ezreal"],
  "GWA"      : [1.1356, 1.2578, 1.6703, 1.8935, 2.2410]
}
data = pd.DataFrame(data)

def scholarship(gwa) :
    if gwa <= 1.45 :
        return "University Scholar (US)"
    elif gwa <= 1.75 :
        return "College Scholar (CS)"
    else :
        return "No scholarship"

data["Scholarship"] = data["GWA"].apply(scholarship)
print(data)
```

---

# Part 6
**Write code using the "Big 3" libraries**

---

## The numpy library

<!-- incremental -->
==**Example 5**== Given the system of linear equations

5x + 3y + 2z = 15<br/>2x - 6y - 7z = -22<br/>4x - 8y + 3z = 9

find the value of x^2 + y^2 + z^2.

|||

<!-- incremental -->
==Solution==

<!-- incremental -->
```python
import numpy as np

A = [[5,  3,  2],   # coefficients matrix
     [2, -6, -7], 
     [4, -8,  3]]
B = [15, -22, 9]    # constants vector
```

<!-- incremental -->
Using matrix inverse method,

<!-- incremental -->
```python
X = np.linalg.inv(A) @ B
```

<!-- incremental -->
or, using *numpy*'s own solver,

<!-- incremental -->
```python
X = np.linalg.solve(A, B)
```
<!-- incremental -->
Either way, we have

<!-- incremental -->
```python
result = np.sum(X**2)
print(result)
```

---

## The numpy library

==**Example 6**== The Civil Engineering Licensure Examination has three subjects with codes MSTC, HGE and PSAD. A future engineer is required to take all these three subjects. His/Her overall rating is then calculated according to the formula

`rating = 0.35 x MSTC + 0.30 x HGE + 0.35 x PSAD`

He/She is said to have passed the exam if the following conditions are satisfied:

- rating <u>></u> 70
- MSTC, HGE, PSAD <u>></u> 50

Given the results from ten students as shown below, determine whether each student has passed the exam.

```python
# student       1   2   3   4   5   6   7   8   9  10
scores_MSTC = [96, 92, 89, 83, 72, 66, 59, 51, 42, 38]
scores_HGE  = [88, 85, 84, 80, 83, 68, 52, 63, 30, 28]
scores_PSAD = [90, 49, 83, 75, 86, 47, 56, 62, 96, 58]
```

---

## The numpy library

<!-- incremental -->
==Solution 1== using lists

<!-- incremental -->

```python
scores_MSTC = [96, 92, 89, 83, 72, 66, 59, 51, 42, 38]
scores_HGE = [88, 85, 84, 80, 83, 68, 52, 63, 30, 28]
scores_PSAD = [90, 49, 83, 75, 86, 47, 56, 62, 96, 58]

rating = [0.35*mstc + 0.30*hge + 0.35*psad \
          for mstc, hge, psad in zip(scores_MSTC, scores_HGE, scores_PSAD)]
is_passed = [rating >= 70.0 and mstc >= 50.0 and hge >= 50.0 and psad >= 50.0 \
             for rating, mstc, hge, psad in \
             zip(rating, scores_MSTC, scores_HGE, scores_PSAD)]

print(rating)
print(is_passed)
```

<!-- incremental -->
> `NOTE` The *zip* function aggregates elements from multiple iterables (like lists, tuples, or strings) into a single iterator of tuples. Each tuple contains elements that share the same index in their original sequences.

---
## The numpy library
<!-- incremental -->
==Solution 2== using *numpy* arrays

<!-- incremental -->

```python hl=11,12,13
scores_MSTC = [96, 92, 89, 83, 72, 66, 59, 51, 42, 38]
scores_HGE = [88, 85, 84, 80, 83, 68, 52, 63, 30, 28]
scores_PSAD = [90, 49, 83, 75, 86, 47, 56, 62, 96, 58]

import numpy as np

scores_MSTC = np.array(scores_MSTC, dtype='float')
scores_HGE = np.array(scores_HGE, dtype='float')
scores_PSAD = np.array(scores_PSAD, dtype='float')

rating = 0.35*scores_MSTC + 0.30*scores_HGE + 0.35*scores_PSAD
is_passed = (rating >= 70.0) & (scores_MSTC >= 50.0) & (scores_HGE >= 50.0) \
            & (scores_PSAD >= 50.0)

print(rating)
print(is_passed)
```

---

## The `pandas` library

==**Example 7**== Given the population of the Philippines from 1840 to 2024 [based on national census](https://psa.gov.ph/system/files/psy/2025_T1_4.xlsx), answer the following questions.

1. The population growth of a certain country is said to be *sustainable* if the annual growth rate is between [0.5% and 1.2%](https://philarchive.org/archive/MALTIP-2). List out the years in which the population growth of the Philippines was sustainable.
2. Based from the provided population data, calculate the average annual growth rate in percent for each listed year.
3. Based from the provided annual growth rate, calculate the maximum and minimum growth rate, and the respective years in which they occurred.
4. Create the following: (a) a bar graph of population for each year, (b) multiple line graphs in a single figure, covering population, population increase and provided and calculated annual growth rate.
---

## The `pandas` library

==Solution #1==

<!-- incremental -->
```python
import pandas as pd
```

<!-- incremental -->
*pandas* can import Excel and CSV files.

<!-- incremental -->
```python
ph_population = pd.read_excel("2025_T1_4.xlsx")
```
<!-- incremental -->
Imported data can sometimes contain invalid data like `NaN` (not a number) or `None` values. `dropna()` can be used to remove these values.

<!-- incremental -->
```python
ph_population = ph_population.dropna()
```
<!-- incremental -->
Like lists or *numpy* arrays, we can specify the rows that we will get as data.

<!-- incremental -->
```python
ph_population = ph_population[1:]    # Exclude the first row (i.e. index 0).
```
<!-- incremental -->
`.columns` can be used to specify the column names.

<!-- incremental -->
```python
ph_population.columns = ["Year", "Population", "Annual Growth Rate (%)", "Source"]
```

---

## The `pandas` library

==Solution #1==

<!-- incremental -->
We can filter the data by specifying conditions within square brackets.

<!-- incremental -->
```python
sustainable = ph_population[ph_population["Annual Growth Rate (%)"] >= 0.5]
sustainable = ph_population[ph_population["Annual Growth Rate (%)"] <= 1.2]
```
<!-- incremental -->
We can also specify which columns will be considered.
<!-- incremental -->
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

==Solution #2==

<!-- incremental -->
`.diff()` calculates the difference between consecutive values.

<!-- incremental -->
```python
ph_population["Annual Increase"] = ph_population["Population"].diff()/ \
                                                            ph_population["Year"].diff()
```
<!-- incremental -->
`.shift()` shifts the values in a column by a specified number of periods.
<!-- incremental -->
```python
ph_population["Calculated Rate (%)"] = ph_population["Annual Increase"]/ \
                                              ph_population["Population"].shift(1) * 100
```
<!-- incremental -->
Show only the last two rows.
<!-- incremental -->
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

==Solution #3==
<!-- incremental -->
Some statistical measures that can be computed using *pandas* are `max()`, `min()`, `mean()`, `median()`, `std()`, `count()` and `sum()`.
<!-- incremental -->
```python
# Maximum and minimum annual growth rates.
print(ph_population["Annual Growth Rate (%)"].max())    # 3.08
print(ph_population["Annual Growth Rate (%)"].min())    # 0.5
```
<!-- incremental -->
`.idxmax()` and `.idxmin()` returns the index numbers of the maximum and minimum values, respectively.
<!-- incremental -->
<br/>Using that index, we can retrieve the corresponding row using `.loc[]`.

<!-- incremental -->
```python
# Year with which they respectively occurred.
print(ph_population.loc[ph_population["Annual Growth Rate (%)"].idxmax(), "Year"]) # 1970
print(ph_population.loc[ph_population["Annual Growth Rate (%)"].idxmin(), "Year"]) # 1896
```
---

## The `matplotlib` library

==Solution #4 (a)==

<!-- incremental -->
`.to_numpy()` converts a pandas Series to a *numpy* array.

<!-- incremental -->
```python
import matplotlib.pyplot as plt

year = ph_population["Year"].to_numpy(dtype='float')
population = ph_population["Population"].to_numpy(dtype='float')
```
<!-- incremental -->
From this, we can plot the data using *matplotlib*.

<!-- incremental -->
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

## The `matplotlib` library

==Solution #4 (b)==

<!-- incremental -->
Several plots can be placed in a single figure using `plt.subplots()`.

<!-- incremental -->
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

## The `scikit-learn` library

==**Example 8**== Given an Excel file of 200 rebound hammer test results reported from different parts of a single building, construct a best-fit line that can be used to estimate the compressive strength (in MPa) of a part of the same building given the obtained rebound number.

==Solution==

```python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
```
As usual, read the Excel file and extract the data as *pandas* Series. However
```python
df = pd.read_excel("rebound_hammer_data.xlsx")
X = df[["Rebound Number"]]
y = df["Concrete Strength (MPa)"]
```

```python
# Fit the linear regression model
model = LinearRegression()
model.fit(X, y)
```

---
## The `scikit-learn` library

```python
# Get the regression coefficients and R² value
slope     = model.coef_[0]
intercept = model.intercept_
r2        = r2_score(y, model.predict(X))

# Generate points for the regression line
x_line = np.linspace(X.min(), X.max(), 300)
y_line = model.predict(x_line)

# Plot
fig, ax = plt.subplots(figsize=(8, 5))

ax.scatter(X, y, color="steelblue", alpha=0.6, label="Data points")
ax.plot(x_line, y_line, color="tomato", linewidth=2, label="Regression line")

# Annotate with the equation and R²
equation = f"y = {slope:.4f}x + {intercept:.4f}\n$R^2$ = {r2:.4f}"
ax.text(0.05, 0.95, equation, transform=ax.transAxes,
        fontsize=11, verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))

ax.set_xlabel("Rebound Number")
ax.set_ylabel("Concrete Strength (MPa)")
ax.set_title("Concrete Strength vs. Rebound Number")
ax.legend()

plt.tight_layout()
plt.show()
```

---

# Part 7
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


