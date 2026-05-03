'''
    Final Project: CC102

    Title: Weighted Task Scheduler & Planner

    By: Mon Raven Lapso

'''

import tkinter as tk
from tkinter import messagebox
import json
from datetime import datetime

FILE = "task-scheduler-data.json"


## Open tasks.json and read all content
def load_tasks():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return []

## Overwrite contents of tasks.json and put the content of tasks variable
def save_tasks(tasks):
    with open(FILE, "w") as f:
        json.dump(tasks, f, indent=4)

'''
    tasks: <List> data structure of tasks
    each task is a <Dictionary> with the following attribute:
        - id
        - name
        - deadline
        - importance
        - effort
        - score
'''

tasks = load_tasks()



## Computes priority score of a given task
def compute_score(task):
    try:
        # Get deadline of task
        deadline = datetime.strptime(task["deadline"], "%Y-%m-%d")

        # How many days until deadline
        days_remaining = max((deadline - datetime.now()).days, 0)
    except:
        days_remaining = 0

    # Weighted formula for priority score
    urgency = 1 / (days_remaining + 1)
    score = (5 * urgency) + (3 * task["importance"]) - (1 * task["effort"])
    return round(score, 2)

## Give sorted task based on priorty score
def sort_tasks(tasks):

    # Recompute score of every tasks
    for task in tasks:
        task["score"] = compute_score(task)

    # Sort task by priority scores: highest -> lowest
    return sorted(tasks, key=lambda x: x["score"], reverse=True)


## Render task list
def refresh_list():

    # Clear list box
    listbox.delete(0, tk.END)
    
    # Get sorted tasks
    scheduled = sort_tasks(tasks)

    # Format all tasks and display
    for t in scheduled:
        display = f"{t['id']:02d} | {t['name']:<20} | Score: {t['score']:<6} | Due: {t['deadline']}"
        listbox.insert(tk.END, display)

## Clears every input typed 
def clear_inputs():
    name_entry.delete(0, tk.END)
    deadline_entry.delete(0, tk.END)
    importance_entry.delete(0, tk.END)
    effort_entry.delete(0, tk.END)

## Adds a task based on the input variables
def add_task():
    try:
        task = {
            "id": len(tasks) + 1,
            "name": name_entry.get(),
            "deadline": deadline_entry.get(),
            "importance": int(importance_entry.get()),
            "effort": int(effort_entry.get()),
            "score": 0
        }

        if not task["name"]:
            raise ValueError

        # Add to the dictionary
        tasks.append(task)

        save_tasks(tasks)
        refresh_list()
        clear_inputs()

    except:
        messagebox.showerror("Error", "Invalid input.")

## Deletes selected task
def delete_task():
    try:
        # Get current selected task
        selected = listbox.get(listbox.curselection())

        # Determine id
        task_id = int(selected.split("|")[0])

        # Search for the task in the dictionary based on its id
        global tasks
        tasks = [t for t in tasks if t["id"] != task_id]

        # Persist change
        save_tasks(tasks)
        refresh_list()

    except:
        messagebox.showerror("Error", "Select a task.")


def load_selected_task():
    try:
        selected = listbox.get(listbox.curselection())
        task_id = int(selected.split("|")[0])

        for t in tasks:
            if t["id"] == task_id:
                name_entry.delete(0, tk.END)
                name_entry.insert(0, t["name"])

                deadline_entry.delete(0, tk.END)
                deadline_entry.insert(0, t["deadline"])

                importance_entry.delete(0, tk.END)
                importance_entry.insert(0, t["importance"])

                effort_entry.delete(0, tk.END)
                effort_entry.insert(0, t["effort"])

    except:
        messagebox.showerror("Error", "Select a task first.")

## Modies an existing task attributes
def update_task():
    try:
        selected = listbox.get(listbox.curselection())
        task_id = int(selected.split("|")[0])

        # Find the task first -> then reassign each attribute to new inputs
        for t in tasks:
            if t["id"] == task_id:
                t["name"] = name_entry.get()
                t["deadline"] = deadline_entry.get()
                t["importance"] = int(importance_entry.get())
                t["effort"] = int(effort_entry.get())

        save_tasks(tasks)
        refresh_list()
        clear_inputs()

    except:
        messagebox.showerror("Error", "Update failed.")


def generate_report():
    if not tasks:
        messagebox.showinfo("Report", "No tasks available.")
        return

    scheduled = sort_tasks(tasks)
    total_tasks = len(tasks)
    avg_score = sum(t["score"] for t in scheduled) / total_tasks

    report = f"Total Tasks: {total_tasks}\nAverage Score: {avg_score:.2f}\n\nTop Tasks:\n"

    for t in scheduled[:5]:
        report += f"- {t['name']} (Score: {t['score']})\n"

    messagebox.showinfo("Task Report", report)



# Initialize TKinter and make a GUI
root = tk.Tk()
root.title("Weighted Task Scheduler")
root.geometry("700x500")

# Input frame: group inputs
input_frame = tk.Frame(root, padx=10, pady=10)
input_frame.pack(fill="x")

tk.Label(input_frame, text="Task Name").grid(row=0, column=0, sticky="w")
name_entry = tk.Entry(input_frame, width=30)
name_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Deadline (YYYY-MM-DD)").grid(row=1, column=0, sticky="w")
deadline_entry = tk.Entry(input_frame, width=30)
deadline_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Importance (1-10)").grid(row=0, column=2, sticky="w")
importance_entry = tk.Entry(input_frame, width=10)
importance_entry.grid(row=0, column=3, padx=5, pady=5)

tk.Label(input_frame, text="Effort (hrs)").grid(row=1, column=2, sticky="w")
effort_entry = tk.Entry(input_frame, width=10)
effort_entry.grid(row=1, column=3, padx=5, pady=5)


# ===== BUTTON FRAME =====
button_frame = tk.Frame(root, pady=5)
button_frame.pack(fill="x")

def styled_button(text, command):
    return tk.Button(
        button_frame,
        text=text,
        command=command,
        bg="#4a90e2",
        fg="white",
        padx=10,
        pady=5,
        relief="flat"
    )

styled_button("Add", add_task).pack(side="left", padx=5)
styled_button("Update", update_task).pack(side="left", padx=5)
styled_button("Delete", delete_task).pack(side="left", padx=5)
styled_button("Load", load_selected_task).pack(side="left", padx=5)
styled_button("Report", generate_report).pack(side="left", padx=5)


# ===== LIST FRAME =====
list_frame = tk.Frame(root)
list_frame.pack(fill="both", expand=True, padx=10, pady=10)

scrollbar = tk.Scrollbar(list_frame)
scrollbar.pack(side="right", fill="y")

listbox = tk.Listbox(
    list_frame,
    yscrollcommand=scrollbar.set)
listbox.pack(fill="both", expand=True)

scrollbar.config(command=listbox.yview)


# INIT
refresh_list()

root.mainloop()