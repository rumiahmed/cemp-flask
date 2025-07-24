import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# Dataset
data = {
    'YearsExperience': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'Salary': [45000, 50000, 60000, 65000, 70000, 80000, 85000, 95000, 100000, 110000]
}

# Convert to DataFrame
df = pd.DataFrame(data)

# Reshape input data
X = df[['YearsExperience']]  # Features (2D)
y = df['Salary']             # Target (1D)

# Create and train the model
model = LinearRegression()
model.fit(X, y)

# Predict salaries
predicted_salary = model.predict(X)

# Print coefficients
print(f"Intercept: {model.intercept_}")
print(f"Coefficient: {model.coef_[0]}")

# Plotting
plt.scatter(X, y, color='blue', label='Actual Salaries')
plt.plot(X, predicted_salary, color='red', label='Regression Line')
plt.xlabel('Years of Experience')
plt.ylabel('Salary')
plt.title('Salary vs. Years of Experience')
plt.legend()
plt.grid(True)
plt.show()
