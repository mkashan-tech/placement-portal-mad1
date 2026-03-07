from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# -------------------
# Admin Model
# -----------------
class Admin(db.Model):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


# -----------------
# Company Model
# -------------------
class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    approved = db.Column(db.Boolean, default=False)
    industry = db.Column(db.String(100))

    password = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)


    jobs = db.relationship('Job', backref='company', lazy=True)


# ---------------------
# Student Model
# -------------------
class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    applications = db.relationship('Application', backref='student', lazy=True)

    education = db.Column(db.String(200))
    resume_text = db.Column(db.Text)
    resume_link = db.Column(db.String(300))
    skills = db.Column(db.String(300))
    cgpa = db.Column(db.Float)
    linkedin = db.Column(db.String(300))
    github = db.Column(db.String(300))
    location = db.Column(db.String(200))

    

    is_active = db.Column(db.Boolean, default=True)
    contact = db.Column(db.String(15))


# ------------------
# Job / Placement Drive
# -------------------
class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='Pending')
    salary = db.Column(db.Integer)
    deadline = db.Column(db.Date)
    skills = db.Column(db.String(200))
    location = db.Column(db.String(200))
    cgpa_cutoff = db.Column(db.Float)

    approved = db.Column(db.Boolean, default=False)


    company_id = db.Column(
        db.Integer,
        db.ForeignKey('companies.id'),
        nullable=False
    )

    applications = db.relationship('Application', backref='job', lazy=True)


# -------------------
# Application (Bridge Table)
# ------------------
class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='Applied')

    student_id = db.Column(
        db.Integer,
        db.ForeignKey('students.id'),
        nullable=False
    )

    job_id = db.Column(
        db.Integer,
        db.ForeignKey('jobs.id'),
        nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint('student_id', 'job_id', name='unique_student_job'),
    )
