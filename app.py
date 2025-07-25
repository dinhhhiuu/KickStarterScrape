import tkinter as tk
from tkinter import messagebox
from scraper import scrape_kickstarter, export_to_excel

def scrape_action():
    url = url_entry.get()
    if url:
        try:
            scrape_kickstarter(url)
            messagebox.showinfo("Thành công", "✅ Dữ liệu đã được lưu vào MongoDB!")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
    else:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập URL!")

def export_action():
    try:
        export_to_excel()
        messagebox.showinfo("Xuất Excel", "✅ Đã xuất file kickstarter_data.xlsx!")
    except Exception as e:
        messagebox.showerror("Lỗi", str(e))

# Tkinter GUI
app = tk.Tk()
app.title("Kickstarter Scraper")
app.geometry("400x200")

tk.Label(app, text="Nhập URL Kickstarter:").pack(pady=5)
url_entry = tk.Entry(app, width=50)
url_entry.pack(pady=5)

tk.Button(app, text="Scrape", command=scrape_action).pack(pady=10)
tk.Button(app, text="Export to Excel", command=export_action).pack(pady=5)

app.mainloop()