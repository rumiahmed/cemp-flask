import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Create dataset (manually, so no download required)
data = {
    'Month': ['Jan', 'Jan', 'Jan', 'Jan', 'Feb', 'Feb', 'Feb', 'Feb', 'Mar', 'Mar', 'Mar', 'Mar'],
    'Region': ['North', 'South', 'East', 'West'] * 3,
    'Sales': [10500, 9800, 11000, 9700, 11200, 9900, 11800, 9500, 11500, 10000, 12100, 9600]
}
df = pd.DataFrame(data)

# Convert Month to category for better plotting
df['Month'] = pd.Categorical(df['Month'], categories=['Jan', 'Feb', 'Mar'], ordered=True)

# ------------------------
# 🔴 BAD VISUALIZATION 1: Pie chart for time-series data (wrong chart type)
# ------------------------
jan_sales = df[df['Month'] == 'Jan']
plt.figure(figsize=(6,6))
plt.pie(jan_sales['Sales'], labels=jan_sales['Region'], autopct='%1.1f%%')
plt.title('🔴 Pie Chart of Sales by Region (Jan) – Misleading for Time Series')
plt.savefig('bad_pie_chart.png')
plt.close()

# ------------------------
# 🔴 BAD VISUALIZATION 2: Bar chart with truncated Y-axis
# ------------------------
mean_sales = df.groupby('Region')['Sales'].mean().reset_index()
plt.figure(figsize=(8,5))
sns.barplot(data=mean_sales, x='Region', y='Sales', color='salmon')
plt.ylim(9000, 12500)  # Truncated Y-axis
plt.title('🔴 Average Sales by Region – Exaggerated Differences (Bad Axis)')
plt.savefig('bad_bar_chart.png')
plt.close()

# ------------------------
# 🔴 BAD VISUALIZATION 3: Cluttered line chart with poor color
# ------------------------
plt.figure(figsize=(10,6))
for region in df['Region'].unique():
    region_data = df[df['Region'] == region]
    plt.plot(region_data['Month'], region_data['Sales'], label=region, linestyle='--', linewidth=2)
plt.title('🔴 Monthly Sales Trends – Cluttered Lines and Poor Contrast')
plt.savefig('bad_line_chart.png')
plt.close()

# ------------------------
# ✅ GOOD VISUALIZATION 1: Line chart with colorblind-safe palette
# ------------------------
plt.figure(figsize=(10,6))
sns.lineplot(data=df, x='Month', y='Sales', hue='Region', marker='o', palette='colorblind')
plt.title('✅ Monthly Sales Trends by Region – Clean & Clear')
plt.ylabel('Sales ($)')
plt.xlabel('Month')
plt.legend(title='Region')
plt.grid(True)
plt.savefig('good_line_chart.png')
plt.close()

# ------------------------
# ✅ GOOD VISUALIZATION 2: Proper bar chart with full Y-axis
# ------------------------
plt.figure(figsize=(8,5))
sns.barplot(data=mean_sales, x='Region', y='Sales', palette='colorblind')
plt.title('✅ Average Sales by Region – Accurate Comparison')
plt.ylim(0, 13000)  # Full Y-axis
plt.ylabel('Average Sales ($)')
plt.savefig('good_bar_chart.png')
plt.close()

print("✅ All charts saved! Check your project folder.")
