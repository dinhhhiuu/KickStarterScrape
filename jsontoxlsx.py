import json
import openpyxl
import os

# Đường dẫn tới file Excel
excel_path = './data/kickstarter_data.xlsx'

# Nếu file Excel đã tồn tại, xóa nó
if os.path.exists(excel_path):
    os.remove(excel_path)

# Đọc dữ liệu từ JSON
with open('data/data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Tạo workbook mới và ghi dữ liệu
wb = openpyxl.Workbook()
ws = wb.active
ws.title = 'Kickstarter Data'

headers = list(data[0].keys())
ws.append(headers)

for item in data:
    row = [item.get(key, '') for key in headers]
    ws.append(row)

# Lưu workbook vào file Excel mới
wb.save(excel_path)

# Xóa file JSON sau khi dùng
os.remove('data/data.json')

print("✅ Đã lưu thành file kickstarter_data.xlsx")
