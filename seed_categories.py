from app import app
from models import db, Category

default_categories = [
    "Workshop",
    "Seminar",
    "Cultural Event",
    "Sports",
    "Volunteering",
    "Networking",
    "Fundraiser",
    "Educational Talk",
    "Hackathon",
    "Club Meetup"
]

with app.app_context():
    for name in default_categories:
        if not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name))
    db.session.commit()
    print("Default categories added successfully!")
