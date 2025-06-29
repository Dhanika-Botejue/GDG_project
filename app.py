from ai import extract_tasks_from_image
import datetime
from flask import Flask, render_template, request, redirect, url_for
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

DATA_FILE = "study_plan.json"
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"tasks": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/tasks")
def tasks():
    data = load_data()
    return render_template("tasks.html", tasks=data["tasks"])

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        subject = request.form["subject"]
        task = request.form["task"]
        due_date = request.form["due_date"]
        reminder = request.form.get("reminder") == "on"

        data = load_data()
        data["tasks"].append({
            "subject": subject,
            "task": task,
            "due_date": due_date,
            "reminder": reminder,
            "completed": False
        })
        save_data(data)
        return redirect(url_for("tasks"))

    return render_template("add.html")

@app.route('/complete/<int:task_id>', methods=['POST'])
def complete(task_id):
    data = load_data()
    if 0 <= task_id < len(data['tasks']):
        data['tasks'][task_id]['completed'] = True
        save_data(data)
    return redirect('/tasks')

@app.route("/reminders")
def reminders():
    data = load_data()
    today = datetime.date.today().isoformat()
    today_tasks = [t for t in data["tasks"] if t["reminder"] and not t["completed"] and t["due_date"] == today]
    return render_template("reminders.html", reminders=today_tasks)

@app.route("/ai", methods=["POST"])
def ai_extract():
    # Check if a file was uploaded
    if 'image' not in request.files:
        print("No file part")
        return redirect("/")
    
    file = request.files['image']
    
    # If user doesn't select file, browser also submits an empty part without filename
    if file.filename == '' or file.filename is None:
        print("No selected file")
        return redirect("/")
    
    if file and allowed_file(file.filename):
        # Secure the filename and save the file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        print(f"File saved to: {filepath}")
        
        # Extract tasks using the AI
        tasks = extract_tasks_from_image(filepath)
        
        if tasks:
            data = load_data()
            data["tasks"].extend(tasks)
            save_data(data)
            print(f"Added {len(tasks)} tasks from AI extraction")
        else:
            print("No tasks extracted by AI")
        
        # Clean up the uploaded file
        try:
            os.remove(filepath)
        except OSError:
            pass  # File might already be deleted
        
        return redirect("/tasks")
    
    print("Invalid file type")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)