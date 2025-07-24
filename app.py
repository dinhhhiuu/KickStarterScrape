from flask import Flask, render_template, request, send_file
from scraper import scrape_kickstarter
import io
import openpyxl
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        action = request.form.get("action")
        url = request.form.get("url")

        if action == "scrape" and url:
            scrape_kickstarter(url)
            return render_template("index.html", message="✅ Đã lưu vào MongoDB!")

        elif action == "xlsx":
            try:
                # Kết nối MongoDB
                client = MongoClient(os.getenv("MONGO_URI"))
                db = client["kickstarter"]
                collection = db["projects"]
                data = list(collection.find({}, {"_id": 0}))

                if not data:
                    return "❌ Không có dữ liệu để export!"

                # Tạo Excel trong bộ nhớ
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = "Kickstarter Data"

                headers = list(data[0].keys())
                ws.append(headers)

                for item in data:
                    row = [item.get(key, "") for key in headers]
                    ws.append(row)

                # Ghi vào bộ nhớ
                file_stream = io.BytesIO()
                wb.save(file_stream)
                file_stream.seek(0)

                return send_file(
                    file_stream,
                    as_attachment=True,
                    download_name="kickstarter_data.xlsx",
                    mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            except Exception as e:
                return f"Lỗi khi export: {e}"

    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Nếu PORT không có thì dùng 10000 mặc định
    app.run(host="0.0.0.0", port=port)
