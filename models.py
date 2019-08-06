from flask_login import UserMixin
from __init__ import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    year = db.Column(db.String(63))
    major = db.Column(db.String(63))
    
    def __init__(self, name, email, password, year, major):
        self.name = name
        self.email = email
        self.year = year
        self.major = major
        self.password = password
        
class CurrentQuestion(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key = True)
    question_id = db.Column(db.Integer)
    
    def __init__(self, user, question):
        self.user_id = user
        self.question_id = question
