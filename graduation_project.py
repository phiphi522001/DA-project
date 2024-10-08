# -*- coding: utf-8 -*-
"""Graduation project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1uIqO5uLDBr-BR-qcdbbJ0mz5rjAEDqLZ

# **PROJECT TỐT NGHIỆP**

Import các thư viện cần thiết để sử dụng.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import statsmodels.api as sm
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

"""Định nghĩa các hàm sử dụng cho các trường hợp riêng để tối ưu hoá hiệu suất code."""

def remove_outliers_iqr(df): # Hàm remove giá trị ngoại lệ
    numeric_cols = df.select_dtypes(include=[np.number]) # Chọn các cột số của df
    non_numeric_cols = df.select_dtypes(exclude=[np.number]) # Chọn các cột không phải cột số

    # Tính toán tứ phân vị
    Q1 = numeric_cols.quantile(0.25)
    Q3 = numeric_cols.quantile(0.75)
    IQR = Q3 - Q1 # Tính toán IQR
    # Tính toán giá trị giới hạn
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    numeric_cols_cleaned = numeric_cols[~((numeric_cols < lower_bound) | (numeric_cols > upper_bound)).any(axis=1)] # Loại bỏ ngoại lệ cho cột số

    df_cleaned = pd.concat([non_numeric_cols, numeric_cols_cleaned], axis=1) # Kết hợp lại DataFrame
    df_cleaned.reset_index(drop=True, inplace=True) # Đặt lại chỉ số
    df_cleaned.dropna(inplace=True) # Xóa các dòng chứa giá trị NaN

    return df_cleaned

"""Tải dữ liệu từ file csv vào pandas dataframe."""

df = pd.read_csv('https://raw.githubusercontent.com/phiphi522001/DA-project/main/food_nutrition_dataset.csv')

"""## **1. Data cleaning**

Thực hiện quy trình làm sạch dữ liệu.

### **1.1. Data profiling**

Lấy ra và xem sơ lược qua các giá trị ở 10 hàng ngẫu nhiên.
"""

df.sample(10)

"""Xem thông tin và cấu trúc của df được khởi tạo."""

df.info()

"""Hiển thị thống kê mô tả của toàn bộ các cột trong tập dữ liệu."""

df.describe()

"""Thống kê mô tả của các cột có type là object."""

df.describe(include='object')

"""Số lượng các hàng có dữ liệu ở tất cả các cột đều bị trùng."""

df.duplicated().sum()

"""Số lượng giá trị bị trùng ở cột `Description`."""

df['Description'].duplicated().sum()

"""### **1.2. Fixing data types**

Chuyển đổi các kiểu dữ liệu bị sai về kiểu phù hợp.
"""

df = df.astype({'Category': 'category'}) # Chuyển đổi kiểu object của cột `Category` về kiểu category
df = df.astype({'Description':'string'}) # Chuyển đổi kiểu object của cột `Description` về kiểu string

"""Xem lại thông tin của 2 cột sau khi đã chuyển đổi kiểu dữ liệu.

"""

df[['Category', 'Description']].info()

"""### **1.3. Remove những giá trị trùng lặp**

Xoá những giá trị bị trùng ở cột `Description`.
"""

df = df.drop_duplicates(subset='Description', keep='first')
df.duplicated().sum()

"""### **1.4. Remove outliers**

:Loại bỏ các giá trị ngoại lệ của cột `Calorie` trong df.
"""

# Tính toán tứ phân vị của cột `Calorie`
Q1 = df['Calorie'].quantile(0.25)
Q3 = df['Calorie'].quantile(0.75)
IQR = Q3 - Q1 # Tính toán IQR
# Tính toán giá trị giới hạn
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
df_clean = df[(df['Calorie'] >= lower_bound) & (df['Calorie'] <= upper_bound)] # Loại bỏ các giá trị ngoại lệ

df_clean.info()

"""Xem lại thống kê mô tả của df sau khi được làm sạch."""

df_clean.describe()

"""Xuất df đã được làm sạch ra một file csv mới."""

# df_clean.to_csv('food_nutrition_dataset_clean.csv', index=False)

"""## **2. Phân tích tương quan**

Phân tích về mối tương quan giữa các biến.

### **2.1. Ma trận tương quan**

Tính toán ma trận tương quan và trực quan hoá.
"""

numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist() # Select các cột chỉ chứa số
corr_matrix = df_clean[numeric_cols].corr() # Tính toán ma trận tương quan

# Tạo heatmap trực quan
plt.figure(figsize=(25, 12))
sns.heatmap(corr_matrix, annot=True, cmap='plasma', linewidths=0.5)
plt.title('Correlation Matrix')
plt.show

"""### **2.2. Insights**

> **Hệ số tương quan của Carbohydrate so với lượng đường, calo, ... và các chất dinh dưỡng khác:** \
- Hệ số tương quan của carbohydrate so với tổng lượng đường và lượng calo đều là $0.6$, mối tương quan này là mạnh. Thức ăn càng nhiều đường và calo thì carbohydrate càng cao. Còn đối với các chất dinh dưỡng khác thì mối quan hệ tuyến tính thể hiện từ rất yếu đến vừa phải.

> **Hệ số tương quan của Calo so với tổng lượng chất béo, chất béo bão hoà, chất béo chưa bão hoà đa, chất béo chưa bão hoà đơn:**
- Hệ số giữa calo và các nhóm chất béo ở mức mạnh đến rất mạnh, càng nhiều calo thì chất béo càng cao và ngược lại.

> **Hệ số tương quan của Niacin so với các vitamin nhóm B và sắt:**
- Hệ số tương quan tuyến tính từ mạnh đến rất mạnh giữa niacin với các vitamin nhóm B, sắt. Lượng niacin trong món ăn càng cao thì hàm lượng các vitamin nhóm B và sắt càng cao.

## **3. Mô hình dự báo**

Dự đoán giá trị `Calorie` dựa trên các yếu tố khác.

### **3.1. Model summary**

Tính toán lần đầu để chọn lọc các biến độc lập có ý nghĩa thống kê tốt (p-value < 0.05).
"""

numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist() # Chọn những cột số trong df
removed_item = numeric_cols.pop(3) # Xoá phần tử có giá trị là 'Calorie' trong list phía trên và gán vào biến này

# Chia tách dữ liệu trong df_clean thành 2 phần
X = df_clean[numeric_cols]
y = df_clean[removed_item]

# X.isnull().sum()

X = sm.add_constant(X) # Thêm một cột giá trị hằng số (1) vào df
model = sm.OLS(y, X).fit() # Xây dựng và huấn luyện mô hình linear regression
print(model.summary()) # Xem tóm tắt mô hình

"""Tính toán lại lần thứ 2 do có vài feature có p-value > 0.05 (không có ý nghĩa thống kê)."""

numeric_cols = [item for item in numeric_cols if item not in ['Cholesterol', 'Manganese', 'Pantothenic Acid', 'Retinol',
                                                              'Riboflavin', 'Monounsaturated Fat', 'Polyunsaturated Fat', 'Saturated Fat', 'Vitamin A - RAE',
                                                              'Vitamin E', 'Vitamin K', 'Potassium', 'Sodium', 'Calcium']] # Chọn những cột có ý nghĩa thống kê từ summary phía trên
X = df_clean[numeric_cols] # ...
X = sm.add_constant(X) # ...
model = sm.OLS(y, X).fit() # Xây dựng và huấn luyện ...
print(model.summary()) # ...

"""### **3.2. Tạo forecast**

Tạo forecast.
"""

# new_data = pd.DataFrame({
#     ...
# }) # Tập dữ liệu dùng để dự đoán

# new_data = sm.add_constant(new_data) # Thêm một cột hằng số vào df new_data
# forecast = model.predict(new_data) # Tạo một dự báo, dự báo giá trị `Calorie` dựa trên những giá trị còn lại
# print(forecast)

"""### **3.3. Đánh giá mô hình**

Đánh giá mức độ phù hợp của mô hình đối với dữ liệu và tính chính xác trong các dự báo tương lai.
"""

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2) # Chia dữ liệu thành 2 phần train và test
# X_train = sm.add_constant(X_train) # Thêm cột hằng số vào X_train

# Tạo và huấn luyện mô hình
model = LinearRegression()
model.fit(X_train, y_train)

# Dự đoán
y_pred = model.predict(X_test)

# Đánh giá mô hình
print('R-squared:', r2_score(y_test, y_pred))
print('Mean Squared Error:', mean_squared_error(y_test, y_pred))
print('Root Mean Squared Error:', np.sqrt(mean_squared_error(y_test, y_pred)))

# # predictions = model.predict(X_test) # Tạo dự báo dựa trên tập dữ liệu test

# # # Đánh giá mô hình
# # mse = np.mean((y_test - predictions) ** 2)
# # rmse = np.sqrt(mse)

# # print('mse:', mse)
# # print('rmse:', rmse)

"""So sánh RMSE và MSE với thống kê mô tả của cột `Calorie`."""

df_clean['Calorie'].describe()

"""**Tóm tắt:**

* **So với trung bình của cột:** RMSE bằng khoảng $6.52\%$ giá trị trung bình, sai số khá nhỏ, cho thấy mô hình rất phù hợp với dữ liệu.
* **So với độ lệch chuẩn:** RMSE bằng khoảng $9.15\%$ độ lệch chuẩn, tương đối nhỏ so với độ biến thiên của dữ liệu, cho thấy hiệu suất mô hình tốt.
* **So với phạm vi:** Sai số khá nhỏ so với phạm vi dữ liệu, RMSE bằng khoảng $1.95\%$.
"""