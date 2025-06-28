from flask import Flask, render_template, request, redirect, url_for
import json
import datetime

app = Flask(__name__)

DATA_FILE = "study_plan.json"

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

if __name__ == "__main__":
    app.run(debug=True)