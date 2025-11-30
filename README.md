# 🧠 Smart Grading Engine  
### AI-Powered Automatic Grading System for Teachers  

A Flask-based web app that uses **Mistral AI OCR** to automatically extract text from handwritten student answer sheets, compare it with a teacher’s reference answer, and generate grades instantly.  
Includes an **analytics dashboard** for tracking student performance, grade distribution, and progress trends.

---

## 🚀 Features

- 🤖 **Automatic AI Grading** — Grades written answers using keyword similarity.  
- 🧾 **OCR Integration (Mistral AI)** — Extracts text from images with high accuracy.  
- 📊 **Analytics Dashboard** — Visual charts for student progress and grade trends.  
- 💾 **Persistent Database (SQLite)** — Stores all student results for review.  
- 📤 **Export Results (CSV)** — Download complete grading data.  
- 💬 **Keyword Feedback** — Highlights matched and missing terms.  

---

## 🧩 Tech Stack

| Layer | Technology |
|--------|-------------|
| **Frontend** | HTML5, CSS3, Bootstrap 5, Chart.js |
| **Backend** | Flask (Python) |
| **OCR / AI** | Mistral AI |
| **Database** | SQLite (SQLAlchemy ORM) |
| **Deployment** | Railway / Render / Replit |

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Ojasvi2006/Smart-Grading-Engine.git
cd Smart-Grading-Engine

2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate      # On Windows
source venv/bin/activate   # On macOS/Linux

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Add Mistral API Key

Set your environment variable:

# Windows
set MISTRAL_API_KEY=your_api_key_here

# macOS/Linux
export MISTRAL_API_KEY=your_api_key_here

5️⃣ Run the App
python app.py
Visit 👉 http://127.0.0.1:5000

📊 Dashboard

Visualize grades, averages, and progress trends at:

/dashboard

Includes:

🥧 Grade Distribution

📈 Average Marks by Student

📅 Class Performance Over Time

📤 CSV Export

📜 Grading Logic
Similarity (%)	Grade	Marks
≥ 90	A	100
75–89	B	85
60–74	C	70
40–59	D	55
< 40	F	30

📁 Project Structure
Smart-Grading-Engine/
├── app.py
├── models.py
├── requirements.txt
├── runtime.txt
├── templates/
│   ├── index.html
│   ├── result.html
│   └── dashboard.html
├── uploads/
└── smart_grading.db

Environment Variables
Variable	Description
MISTRAL_API_KEY	Your Mistral AI OCR API key

Future Enhancements

🧾 AI-based semantic grading (LLM-powered)

📬 Automated student feedback

👥 Multi-user (Teacher/Student) login system

🧾 Downloadable PDF report cards
