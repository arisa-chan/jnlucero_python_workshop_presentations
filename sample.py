# %%
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# Read the Excel file
df = pd.read_excel("rebound_hammer_data.xlsx")

# Extract features (X) and target (y)
X = df[["Rebound Number"]]          # 2D array required by scikit-learn
y = df["Concrete Strength (MPa)"]

# Fit the linear regression model
model = LinearRegression()
model.fit(X, y)

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