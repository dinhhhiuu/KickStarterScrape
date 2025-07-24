from flask import Flask, render_template, request, send_file
from scraper import scrape_kickstarter
import subprocess
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "scrape":
            url = request.form.get("url")
            if url:
                scrape_kickstarter(url)
                return render_template("index.html", message="✅ Đã lưu dữ liệu từ Kickstarter!")
        
        elif action == "xlsx":
            try:
                subprocess.run(["python", "jsontoxlsx.py"], check=True)
                return send_file("data/kickstarter_data.xlsx", as_attachment=True)
            except Exception as e:
                return f"Lỗi khi tạo file Excel: {e}"
    
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
