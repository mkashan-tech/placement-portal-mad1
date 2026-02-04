from flask import Flask, render_template, request, redirect, url_for, session
from models import db, Admin, Company, Student
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mad1-secret-key'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
os.makedirs(os.path.join(BASE_DIR, 'database'), exist_ok=True)

DB_PATH = os.path.join(BASE_DIR, 'database', 'db.sqlite3')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ---------------- HOME --------------------
@app.route('/')
def home():
    return "Placement Portal App - MAD I"


# ---------------- ADMIN ----------------
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


@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    return "Admin Dashboard"


# ---------------- COMPANY ----------------
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
        if company and company.approved:
            session['role'] = 'company'
            session['user_id'] = company.id
            return redirect(url_for('company_dashboard'))

    return render_template('login.html', role='Company')


@app.route('/company/dashboard')
def company_dashboard():
    if session.get('role') != 'company':
        return redirect(url_for('company_login'))
    return "Company Dashboard"


# ---------------- STUDENT ----------------
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
        if student:
            session['role'] = 'student'
            session['user_id'] = student.id
            return redirect(url_for('student_dashboard'))

    return render_template('login.html', role='Student')


@app.route('/student/dashboard')
def student_dashboard():
    if session.get('role') != 'student':
        return redirect(url_for('student_login'))
    return "Student Dashboard"


# ---------------- ADMIN APPROVAL --------------
@app.route('/admin/approve/<int:company_id>')
def approve_company(company_id):
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))

    company = Company.query.get(company_id)
    if company:
        company.approved = True
        db.session.commit()

    return "Company Approved"


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# ---------------- RUN ----------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # create admin ONCE
        if not Admin.query.filter_by(email="admin@iitm.ac.in").first():
            admin = Admin(email="admin@iitm.ac.in", password="admin123")
            db.session.add(admin)
            db.session.commit()

    app.run(debug=True)
