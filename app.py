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
    

    company_id = session.get('user_id')
    jobs = Job.query.filter_by(company_id=company_id).all()

    return render_template('company_dashboard.html', jobs=jobs)



@app.route('/company/job/create', methods=['GET', 'POST'])
def create_job():
    if session.get('role') != 'company':
        return redirect(url_for('company_login'))
    
    if request.method == 'POST':
        job = Job(
            title = request.form['title'],
            description = request.form['description'],
            salary = request.form['salary'],
            company_id = session.get('user_id'),
            status='Active'
        ) 
        db.session.add(job)
        db.session.commit()

        return redirect(url_for('company_dashboard'))
    return render_template('create_job.html')

@app.route('/company/job/<int:job_id>/applications')
def job_applications(job_id):
    if session.get('role') != 'company':
        return redirect(url_for('company_login'))
    
    applications = Application.query.filter_by(job_id=job_id).all()

    return render_template(
        'company_applications.html',
        applications=applications
    )

# Update the Application Status
@app.route('/company/application/<int:id>/shortlist')
def shortlist_application(id):
    app_obj = Application.query.get(id)
    app_obj.status = "Shortlisted"
    db.session.commit()
    return redirect(request.referrer)


@app.route('/company/application/<int:id>/reject')
def reject_application(id):
    app_obj = Application.query.get(id)
    app_obj.status = "Rejected"
    db.session.commit()
    return redirect(request.referrer)

@app.route('/company/application/<int:id>/select')
def select_application(id):
    app_obj = Application.query.get(id)
    app_obj.status = "Selected"
    db.session.commit()
    return redirect(request.referrer)


# Close the job posting
@app.route('/company/job/<int:id>/close')
def close_job(id):
    job = Job.query.get(id)
    job.status = "Closed"
    db.session.commit()
    return redirect(url_for('company_dashboard'))



# ----------------------- STUDENT AUTH --------------------
@app.route('/student/register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        existing = Student.query.filter_by(
            email = request.form['email']
        ).first()

        if existing:
            return "Email already registered."


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
    
    jobs = Job.query.filter_by(approved=True, status="Active").all()

    applications = Application.query.filter_by(
        student_id=session.get('user_id')
    ).all()

    return render_template(
        'student_dashboard.html',
        jobs=jobs,
        applications=applications
    )

# Apply for Job (Core Feature)
@app.route('/student/apply/<int:job_id>')
def apply_job(job_id):
    if session.get('role') != 'student':
        return redirect(url_for('student_login'))
    
    student_id = session.get('user_id')

    existing = Application.query.filter_by(
        student_id=student_id,
        job_id=job_id
    ).first()

    if not existing:
        app_obj = Application(
            student_id=student_id,
            job_id=job_id
        )
        db.session.add(app_obj)
        db.session.commit()

    return redirect(url_for('student_dashboard'))


# Student_Profile_Update
@app.route('/student/profile', methods=['GET', 'POST'])
def student_profile():
    if session.get('role') != 'student':
        return redirect(url_for('student_login'))
    
    student = Student.query.get(session.get('user_id'))

    if request.method == 'POST':
        student.education = request.form['education']
        student.skills = request.form['skills']
        student.resume = request.form['resume']
        db.session.commit()

        return redirect(url_for('student_dashboard'))
    
    return render_template('student_profile.html', student=student)




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
