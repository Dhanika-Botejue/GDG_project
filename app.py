from ai import extract_tasks_from_image
import datetime
from flask import Flask, render_template, request, redirect, url_for
import json
import os
from werkzeug.utils import secure_filename
import pymongo
from bson.objectid import ObjectId
from dotenv import load_dotenv

load_dotenv() # Load variables from .env file

app = Flask(__name__)

# --- MongoDB Configuration ---
MONGO_USERNAME = os.getenv("MONGO_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_CLUSTER_URL = os.getenv("MONGO_CLUSTER_URL")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "study_planner")

# Construct the MongoDB URI from environment variables
MONGO_URI = f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_CLUSTER_URL}/{MONGO_DB_NAME}?retryWrites=true&w=majority&appName=Cluster0"

client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
tasks_collection = db.tasks

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/tasks")
def tasks():
    all_tasks = list(tasks_collection.find().sort("due_date", pymongo.ASCENDING))
    return render_template("tasks.html", tasks=all_tasks)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        subject = request.form["subject"]
        task = request.form["task"]
        due_date = request.form["due_date"]
        reminder = request.form.get("reminder") == "on"

        new_task = {
            "subject": subject,
            "task": task,
            "due_date": due_date,
            "reminder": reminder,
            "completed": False
        }
        tasks_collection.insert_one(new_task)
        return redirect(url_for("tasks"))

    return render_template("add.html")

@app.route('/complete/<string:task_id>', methods=['POST'])
def complete(task_id):
    try:
        tasks_collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {"completed": True}}
        )
    except Exception as e:
        print(f"Error completing task: {e}")
    return redirect('/tasks')

@app.route("/reminders")
def reminders():
    today = datetime.date.today().isoformat()
    query = {"reminder": True, "completed": False, "due_date": today}
    today_tasks = list(tasks_collection.find(query))
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
            # Ensure all tasks from AI have the 'completed' field
            for task in tasks:
                task['completed'] = False
            tasks_collection.insert_many(tasks)
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