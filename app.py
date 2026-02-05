from flask import Flask, render_template, request, redirect, url_for, session
from models import db, Admin, Company, Student, Job, Application
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mad1-secret-key'

# ---------------- DATABASE CONFIG ----------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
os.makedirs(os.path.join(BASE_DIR, 'database'), exist_ok=True)

DB_PATH = os.path.join(BASE_DIR, 'database', 'db.sqlite3')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ---------------- HOME ----------------
@app.route('/')
def home():
    return "Placement Portal App - MAD I"


# ------------------ ADMIN AUTH -------------------
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        admin = Admin.query.filter_by(email=email, password=password).first()
        if admin:
            session['role'] = 'admin'
            session['user_id'] = admin.id
            return redirect(url_for('admin_dashboard'))

    return render_template('login.html', role='Admin')


# --------------- ADMIN DASHBOARD -----------------
@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))

    data = {
        'students': Student.query.count(),
        'companies': Company.query.count(),
        'jobs': Job.query.count(),
        'applications': Application.query.count()
    }

    return render_template('admin_dashboard.html', data=data)


# ----------------- COMPANY AUTH ----------------------
@app.route('/company/register', methods=['GET', 'POST'])
def company_register():
    if request.method == 'POST':
        company = Company(
            name=request.form['name'],
            email=request.form['email'],
            password=request.form['password']
        )
        db.session.add(company)
        db.session.commit()
        return "Registration submitted. Wait for admin approval."

    return render_template('register.html', role='Company')


@app.route('/company/login', methods=['GET', 'POST'])
def company_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        company = Company.query.filter_by(email=email, password=password).first()
        if company and company.approved and company.is_active:
            session['role'] = 'company'
            session['user_id'] = company.id
            return redirect(url_for('company_dashboard'))

    return render_template('login.html', role='Company')


@app.route('/company/dashboard')
def company_dashboard():
    if session.get('role') != 'company':
        return redirect(url_for('company_login'))
    return "Company Dashboard"


# ----------------------- STUDENT AUTH --------------------
@app.route('/student/register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        student = Student(
            name=request.form['name'],
            email=request.form['email'],
            password=request.form['password']
        )
        db.session.add(student)
        db.session.commit()
        return redirect(url_for('student_login'))

    return render_template('register.html', role='Student')


@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        student = Student.query.filter_by(email=email, password=password).first()
        if student and student.is_active:
            session['role'] = 'student'
            session['user_id'] = student.id
            return redirect(url_for('student_dashboard'))

    return render_template('login.html', role='Student')


@app.route('/student/dashboard')
def student_dashboard():
    if session.get('role') != 'student':
        return redirect(url_for('student_login'))
    return "Student Dashboard"


# ------------------ ADMIN MANAGEMENT -----------------
@app.route('/admin/companies')
def admin_companies():
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))

    companies = Company.query.all()
    return render_template('admin_companies.html', companies=companies)


@app.route('/admin/company/<int:id>/approve')
def approve_company(id):
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))

    company = Company.query.get(id)
    if company:
        company.approved = True
        db.session.commit()

    return redirect(url_for('admin_companies'))


@app.route('/admin/company/<int:id>/deactivate')
def deactivate_company(id):
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))

    company = Company.query.get(id)
    if company:
        company.is_active = False
        db.session.commit()

    return redirect(url_for('admin_companies'))


@app.route('/admin/students')
def admin_students():
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))

    students = Student.query.all()
    return render_template('admin_students.html', students=students)


@app.route('/admin/student/<int:id>/deactivate')
def deactivate_student(id):
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))

    student = Student.query.get(id)
    if student:
        student.is_active = False
        db.session.commit()

    return redirect(url_for('admin_students'))


@app.route('/admin/jobs')
def admin_jobs():
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))

    jobs = Job.query.all()
    return render_template('admin_jobs.html', jobs=jobs)


@app.route('/admin/job/<int:id>/approve')
def approve_job(id):
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))

    job = Job.query.get(id)
    if job:
        job.approved = True
        db.session.commit()

    return redirect(url_for('admin_jobs'))


# ------------------------- LOGOUT ---------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# ------------------------- RUN APP --------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Create admin only once
        if not Admin.query.filter_by(email="admin@iitm.ac.in").first():
            admin = Admin(email="admin@iitm.ac.in", password="admin123")
            db.session.add(admin)
            db.session.commit()

    app.run(debug=True)
