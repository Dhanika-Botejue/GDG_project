import json
import datetime

# test2.py

"""
Personalized Study Planner - Command Line Version

This script allows students to create a custom study schedule, set reminders, and track progress for their courses or exams.
"""


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

def add_task(data):
    subject = input("Enter subject/course: ")
    task = input("Enter task/goal: ")
    due_date = input("Enter due date (YYYY-MM-DD): ")
    reminder = input("Set reminder? (yes/no): ").lower() == "yes"
    data["tasks"].append({
        "subject": subject,
        "task": task,
        "due_date": due_date,
        "reminder": reminder,
        "completed": False
    })
    save_data(data)
    print("Task added!\n")

def view_tasks(data):
    print("\nYour Study Tasks:")
    for idx, t in enumerate(data["tasks"], 1):
        status = "✅" if t["completed"] else "❌"
        print(f"{idx}. [{status}] {t['subject']} - {t['task']} (Due: {t['due_date']})")
    print()

def mark_completed(data):
    view_tasks(data)
    idx = int(input("Enter task number to mark as completed: ")) - 1
    if 0 <= idx < len(data["tasks"]):
        data["tasks"][idx]["completed"] = True
        save_data(data)
        print("Task marked as completed!\n")
    else:
        print("Invalid task number.\n")

def show_reminders(data):
    today = datetime.date.today().isoformat()
    print("\nReminders for today:")
    for t in data["tasks"]:
        if t["reminder"] and not t["completed"] and t["due_date"] == today:
            print(f"- {t['subject']}: {t['task']} (Due today!)")
    print()

def main():
    data = load_data()
    while True:
        print("1. Add Study Task")
        print("2. View Tasks")
        print("3. Mark Task as Completed")
        print("4. Show Today's Reminders")
        print("5. Exit")
        choice = input("Choose an option: ")
        if choice == "1":
            add_task(data)
        elif choice == "2":
            view_tasks(data)
        elif choice == "3":
            mark_completed(data)
        elif choice == "4":
            show_reminders(data)
        elif choice == "5":
            break
        else:
            print("Invalid choice.\n")

if __name__ == "__main__":
    main()