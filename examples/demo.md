# Python for Applied Mathematics
## A Rapid Primer

**PUP Technical Skills Workshop**
*April 30, 2026 · 45 Minutes*

![Python logo](https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/200px-Python-logo-notext.svg.png)

---

## Workshop Roadmap

1. **Part 1 — The Python Ecosystem** *(5 min)*
2. **Part 2 — Fast Computational Math** *(10 min)*
3. **Part 3 — Data Analysis & Visualization** *(15 min)*
4. **Part 4 — Capstone: Monte Carlo Simulation** *(10 min)*
5. **Part 5 — Q&A and Next Steps** *(5 min)*

Follow along: open the shared **Google Colab** notebook now!

---

# Part 1
## The Python Ecosystem

*5 Minutes*

---

## Why Python Dominates Science & Math

- **Readable syntax** — almost reads like pseudocode
- **Massive ecosystem** — 400 000+ packages on PyPI
- **#1 language** in data science & quantitative research
- Used at NASA, Google DeepMind, CERN, central banks

![Stack Overflow Developer Survey](https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Python_logo_01.svg/320px-Python_logo_01.svg.png)

---

## The SciPy Stack

The four libraries every mathematician needs:

| Library | Role |
| ------- | ---- |
| **NumPy** | Fast arrays, linear algebra |
| **SciPy** | Numerical methods, statistics |
| **Pandas** | Tabular data, time-series |
| **Matplotlib** | Publication-quality plots |

![NumPy logo](https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/NumPy_logo_2020.svg/320px-NumPy_logo_2020.svg.png)

---

## Your Environment: Google Colab

- Zero install — runs in the browser
- Free GPU & TPU access
- All SciPy-stack libraries **pre-installed**
- Share a link → everyone gets the same notebook

![Google Colab logo](https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Google_Colaboratory_SVG_Logo.svg/320px-Google_Colaboratory_SVG_Logo.svg.png)

---

# Part 2
## Fast Computational Math

*10 Minutes*

---

## NumPy: Stop Writing `for` Loops

**Slow (pure Python):**
```python
result = [x**2 for x in range(1_000_000)]  # 0.3 s
```

**Fast (NumPy vectorization):**
```python
import numpy as np
x = np.arange(1_000_000)
result = x ** 2                             # 0.002 s — 150× faster
```

Vectorization pushes loops into **compiled C code**.

![NumPy array visualization](https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/NumPy_logo_2020.svg/260px-NumPy_logo_2020.svg.png)

---

## NumPy: Matrix Operations

Create and manipulate matrices in seconds:

```python
A = np.array([[3, 1], [1, 2]])
b = np.array([9, 8])

# Solve the linear system Ax = b
x = np.linalg.solve(A, b)
print(x)   # [2. 3.]
```

$$Ax = b \quad\Rightarrow\quad x = A^{-1}b$$

Also: eigenvalues, SVD, QR decomposition — all one-liners.

---

## SciPy: Numerical Methods in 2 Lines

**Find the root of a function:**
```python
from scipy.optimize import brentq
f = lambda x: x**3 - 2*x - 5
root = brentq(f, 1, 3)   # 2.0945...
```

**Numerical integration:**
```python
from scipy.integrate import quad
result, err = quad(lambda x: x**2, 0, 1)  # 0.3333...
```

$$\int_0^1 x^2\,dx = \frac{1}{3}$$

![SciPy logo](https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/SCIPY_2.svg/260px-SCIPY_2.svg.png)

---

# Part 3
## Data Analysis & Visualization

*15 Minutes*

---

## Pandas: Loading Real Data

```python
import pandas as pd

# Load a CSV — local file or URL
df = pd.read_csv("ph_demographics.csv")

# One line for all key statistics
df.describe()
```

Output: `count`, `mean`, `std`, `min`, `25%`, `50%`, `75%`, `max`
for every numeric column — instantly.

![Pandas logo](https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Pandas_logo.svg/320px-Pandas_logo.svg.png)

---

## Pandas: Descriptive Statistics

```python
# Mean, median, standard deviation
print(df["income"].mean())
print(df["income"].median())
print(df["income"].std())

# Correlation matrix
df.corr()

# Filter: regions with income above average
df[df["income"] > df["income"].mean()]
```

All operations run on **optimised C extensions** — no loops.

---

## Visualizing with Matplotlib

```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 2 * np.pi, 300)
plt.plot(x, np.sin(x), label="sin(x)")
plt.plot(x, np.cos(x), label="cos(x)")
plt.legend()
plt.title("Trigonometric Functions")
plt.show()
```

$$f(x) = \sin(x), \quad g(x) = \cos(x), \quad x \in [0,\, 2\pi]$$

![Matplotlib icon](https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Matplotlib_icon.svg/200px-Matplotlib_icon.svg.png)

---

## Seaborn: Regression in One Line

```python
import seaborn as sns

# Built-in example dataset
tips = sns.load_dataset("tips")

# Scatter plot with regression line
sns.regplot(x="total_bill", y="tip", data=tips)
plt.title("Bill vs Tip — Regression Analysis")
plt.show()
```

*Seaborn is built on top of Matplotlib and understands
Pandas DataFrames natively.*

![Normal distribution](https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Normal_Distribution_PDF.svg/360px-Normal_Distribution_PDF.svg.png)

---

# Part 4
## Capstone: Monte Carlo Simulation

*10 Minutes*

---

## What is Monte Carlo?

**Core idea:** use *random sampling* to solve deterministic problems.

- Named after the casino district in Monaco
- Powers option pricing, climate models, particle physics
- Embarrassingly parallelizable

**Today's task:** estimate $\pi$ using random geometry.

$$\frac{\text{points inside circle}}{\text{total points}} \approx \frac{\pi r^2}{(2r)^2} = \frac{\pi}{4}$$

![Monte Carlo integration](https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/MonteCarloIntegration.png/300px-MonteCarloIntegration.png)

---

## Estimating Pi — The Algorithm

1. Generate $N$ random points $(x, y)$ in $[-1, 1]^2$
2. Count points inside the unit circle: $x^2 + y^2 \leq 1$
3. Estimate: $\hat{\pi} \approx 4 \times \dfrac{\text{inside}}{N}$

```python
import numpy as np

N = 1_000_000
x, y = np.random.uniform(-1, 1, (2, N))
inside = (x**2 + y**2) <= 1.0
pi_estimate = 4 * inside.sum() / N
print(f"π ≈ {pi_estimate:.5f}")   # π ≈ 3.14159
```

**More points → higher accuracy:** error $\propto N^{-1/2}$.

---

## Visualizing the Simulation

```python
import matplotlib.pyplot as plt

# Plot a sample of 10 000 points
sample = 10_000
inside_s  = inside[:sample]
outside_s = ~inside[:sample]

plt.scatter(x[:sample][inside_s],  y[:sample][inside_s],
            s=0.5, color="steelblue")
plt.scatter(x[:sample][outside_s], y[:sample][outside_s],
            s=0.5, color="salmon")
plt.gca().set_aspect("equal")
plt.title(f"Monte Carlo Pi ≈ {pi_estimate:.5f}")
plt.show()
```

![Monte Carlo Pi estimation](https://upload.wikimedia.org/wikipedia/commons/8/84/Pi_30K.gif)

---

# Part 5
## Next Steps & Q&A

*5 Minutes*

---

## Skill Up Before You Step Up

**Top 3 things a math student can do to get hired:**

1. **Build a GitHub portfolio**
   - Push your Colab notebooks to GitHub today
   - Employers look for *evidence* of technical work

2. **Learn SQL next**
   - Data lives in databases before it reaches Python
   - 80% of real data jobs require SQL

3. **Pick one domain to specialise in**
   - Actuarial / Risk: learn `statsmodels`, `lifelines`
   - ML / AI: learn `scikit-learn`, `PyTorch`
   - Finance: learn `QuantLib`, `pandas-ta`

![GitHub logo](https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Octicons-mark-github.svg/200px-Octicons-mark-github.svg.png)

---

## Take-Home Challenge

The notebook has an **unsolved section** at the bottom:

> *Using the Monte Carlo approach, estimate the value of*
> $$\int_0^1 \sqrt{1 - x^2}\,dx = \frac{\pi}{4}$$
> *without using `scipy.integrate`. Compare your answer to
> the `scipy.integrate.quad` result.*

- Hint: this integral is the area of a quarter-circle.
- Target: accuracy within 0.001 using $N = 500\,000$.

---

# Thanks!

**Resources:**
- Colab notebook: *link shared in chat*
- NumPy docs: [numpy.org](https://numpy.org)
- SciPy docs: [scipy.org](https://scipy.org)
- Pandas docs: [pandas.pydata.org](https://pandas.pydata.org)

*Questions? Raise your hand or drop them in the chat.*

Built with [pyxel-slides](https://github.com/kitao/pyxel) — the retro presentation engine.


