# Internship Management System

An Internship Management System built with **Django** and **MySQL** to streamline the process of handling internship applications, department requirements, approvals, and student placements.  

This project helps organizations manage internships by allowing students to apply online, departments to submit requirements, and admins to approve and monitor the overall process.

---

## Features

- 📝 **Student Applications** – Students can apply for internship opportunities via an online form.  
- 🏢 **Department Management** – Departments can submit requirements and view assigned interns.  
- ✅ **Approval Workflow** – Admins can review, approve, or reject applications.  
- 📊 **Dashboard** – Track approved interns, assigned departments, and statistics.  
- 💾 **Database Integration** – Data stored securely in MySQL.  
- 📂 **Export Support** – Generate reports (Excel/CSV) for approved internships.  

---

## Tech Stack

- **Backend:** Django (Python)  
- **Frontend:** HTML, CSS, JavaScript (Vanilla + Bootstrap)  
- **Database:** MySQL  
- **Other Tools:** Django Admin Panel  

---

## Installation

### 1. Clone the repository
git clone https://github.com/your-username/internship-management-system.git
cd internship-management-system
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
### Usage

Admin Panel: Manage students, departments, and approvals at
👉 http://127.0.0.1:8000/admin/

Students: Apply for internships through the application form.

Departments: Submit requirements via their portal.

Approvals: View and approve submitted applications.

###Project Structure

internship-management-system/
│── applications/     # Handles student applications
│── departments/      # Department requirements module
│── approved/         # Approved internships
│── matches/          # Matching interns to departments
│── adminpanel/       # Custom admin logic
│── internship/       # Core Django project files
│── templates/        # HTML templates
│── static/           # CSS, JS, Images
└── manage.py
###License




###Authors

Internship Management System Project Team
Built as part of internship/project work
