

### 🧩 File: `app.py`

import os
import re
import json
import datetime
import base64
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Result
from mistralai import Mistral

API_KEY = "yh7N5DKDvK7ru8EV8taxaUqbPKsiKH5B"
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
DATABASE_URL = 'sqlite:///smart_grading.db'

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

client = Mistral(api_key=API_KEY)

STOP_WORDS = set(['the','a','an','and','or','but','in','on','at','to','for','of','with','by','is','was','are','be','have','has','had','do','does','did','from','that','this','these','those','it','its','as'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def encode_image(image_location):
    with open(image_location, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def clean_text(text):
    text = (text or '').lower().strip()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text

def extract_text_from_image(file_path):
    try:
        base64_file = encode_image(file_path)
        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "image_url",
                "image_url": f"data:image/jpeg;base64,{base64_file}"
            }
        )
        extracted_text = ''
        if hasattr(ocr_response, 'markdown'):
            extracted_text = ocr_response.markdown
        elif hasattr(ocr_response, 'pages') and ocr_response.pages:
            page = ocr_response.pages[0]
            if hasattr(page, 'markdown'):
                extracted_text = page.markdown
            elif isinstance(page, str):
                extracted_text = page
        elif hasattr(ocr_response, 'content'):
            extracted_text = ocr_response.content
        return clean_text(extracted_text)
    except Exception as e:
        print('OCR Error:', e)
        return ''

def calculate_grade(student_text, teacher_text):
    student_text = clean_text(student_text)
    teacher_text = clean_text(teacher_text)
    student_words = set(student_text.split()) - STOP_WORDS
    teacher_words = set(teacher_text.split()) - STOP_WORDS
    if not teacher_words:
        return 0, 'F', [], [], 0
    matched = student_words.intersection(teacher_words)
    missing = teacher_words - student_words
    similarity = (len(matched) / len(teacher_words)) * 100
    if similarity >= 90:
        grade, marks = 'A', 100
    elif similarity >= 75:
        grade, marks = 'B', 85
    elif similarity >= 60:
        grade, marks = 'C', 70
    elif similarity >= 40:
        grade, marks = 'D', 55
    else:
        grade, marks = 'F', 30
    return round(similarity, 2), grade, sorted(list(matched))[:15], sorted(list(missing))[:15], marks

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        student_name = request.form.get('student_name', '').strip() or 'Anonymous'
        question_id = request.form.get('question_id', '').strip() or 'Q1'
        teacher_answer = request.form.get('teacher_answer', '').strip()
        if not teacher_answer:
            return render_template('index.html', error="Please enter teacher's answer")
        if 'student_image' not in request.files:
            return render_template('index.html', error="Please upload student image")
        student_image = request.files['student_image']
        if not student_image or student_image.filename == '' or not allowed_file(student_image.filename):
            return render_template('index.html', error="Invalid image format")
        filename = secure_filename(student_image.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        student_image.save(filepath)
        student_text = extract_text_from_image(filepath)
        if not student_text:
            return render_template('index.html', error="Text extraction failed, try clearer image.")
        similarity, grade, matched, missing, marks = calculate_grade(student_text, teacher_answer)
        session = Session()
        result = Result(
            student_name=student_name,
            question_id=question_id,
            student_text=student_text,
            teacher_text=teacher_answer,
            similarity=similarity,
            grade=grade,
            marks=marks,
            matched_keywords=json.dumps(matched),
            missing_keywords=json.dumps(missing),
            timestamp=datetime.datetime.utcnow()
        )
        session.add(result)
        session.commit()
        session.close()
        warning = None
        if similarity < 40:
            warning = "⚠️ WARNING: Student scored below 40%. Manual review recommended!"
        return render_template('result.html', student_name=student_name, question_id=question_id, student_text=student_text, teacher_text=teacher_answer, similarity=similarity, grade=grade, marks=marks, matched_keywords=matched, missing_keywords=missing, warning=warning)
    return render_template('index.html', error=None)

@app.route('/dashboard')
def dashboard():
    session = Session()
    results = session.query(Result).all()
    session.close()
    by_grade, by_student, time_series = {}, {}, {}
    for r in results:
        by_grade[r.grade] = by_grade.get(r.grade, 0) + 1
        by_student.setdefault(r.student_name, []).append(r.marks)
        date_key = r.timestamp.strftime('%Y-%m-%d')
        time_series.setdefault(date_key, []).append(r.marks)
    avg_by_student = [{ 'student': n, 'avg': round(sum(s)/len(s),2)} for n,s in by_student.items()]
    avg_time_series = sorted([{'date': d, 'avg_marks': round(sum(v)/len(v),2)} for d,v in time_series.items()], key=lambda x:x['date'])
    return render_template('dashboard.html', results=results, by_grade=by_grade, avg_by_student=avg_by_student, time_series=avg_time_series)

@app.route('/export/csv')
def export_csv():
    import csv
    session = Session()
    results = session.query(Result).all()
    session.close()
    csv_path = 'student_results.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID','Student','Question','Marks','Grade','Similarity','Timestamp'])
        for r in results:
            writer.writerow([r.id, r.student_name, r.question_id, r.marks, r.grade, r.similarity, r.timestamp.isoformat()])
    return send_file(csv_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
