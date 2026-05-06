# 📘 Exam Cell Management System

## 🚀 Overview

A web-based database application developed to automate the examination process, including exam scheduling, room allocation, and faculty invigilation assignment.

## 🎯 Problem Solved

Manual exam planning is time-consuming and error-prone. This system ensures:

* Efficient room utilization
* Fair faculty duty distribution
* Conflict-free scheduling

---

## ⚙️ Features

### 📝 Exam Creation

* Create exams with date and slot (FN/AN)

### 📚 Course Selection

* Filter by branch
* Automatically fetch registered student count

### 🏫 Room Allocation

* Greedy algorithm (largest capacity first)
* Ensures minimum number of rooms
* Avoids duplicate room usage

### 👨‍🏫 Faculty Allocation

* Assigns based on least assigned duties
* Prevents same-slot conflicts
* Respects maximum duty limits

### 📊 Reports

* Exam schedule
* Room allocation
* Faculty assignments
* Summary statistics

---

## 🛠️ Tech Stack

| Layer    | Technology           |
| -------- | -------------------- |
| Frontend | HTML, CSS, Bootstrap |
| Backend  | Flask (Python)       |
| Database | MySQL                |

---

## 🧠 Core Logic

### Room Allocation

Rooms are sorted by capacity in descending order and selected until total capacity satisfies the number of students.

### Faculty Allocation

Faculty are assigned based on least assigned duties while ensuring no scheduling conflicts.

---

## 📂 Project Structure

```text
create-exam/
├── app.py
├── db_setup.sql
├── templates/
├── static/
```

---

## ▶️ How to Run

```bash
pip install -r requirements.txt
python app.py
```

---

## 📌 Notes

* Designed during a 4-hour hackathon
* Focused on correctness, constraints, and optimization logic
