import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, date
from models import db, User, Event, Category, Feedback, EventRegistration

app = Flask(__name__)

# --- FIX: Use absolute path for DB ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'cemp.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-very-secret-key'

CEMP_FULL_NAME = "Campus Event Management Portal"

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_app_name():
    return dict(app_name=CEMP_FULL_NAME)

@app.route('/')
@login_required
def home():
    search = request.args.get("search", "")
    category_id = request.args.get("category")
    events_query = Event.query

    if search:
        events_query = events_query.filter(Event.title.ilike(f"%{search}%") | Event.description.ilike(f"%{search}%"))
    if category_id:
        events_query = events_query.filter_by(category_id=category_id)

    events = events_query.order_by(Event.event_date).all()
    categories = Category.query.all()
    return render_template('home.html', events=events, categories=categories, search=search, selected_category=category_id)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_obj = User.query.filter_by(username=username).first()
        if user_obj and user_obj.check_password(password):
            login_user(user_obj)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_event():
    categories = Category.query.order_by(Category.name).all()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']
        event_date = request.form['event_date']
        event_time = request.form['event_time']
        category_id = request.form.get('category_id')

        try:
            event_date_obj = datetime.strptime(event_date, '%Y-%m-%d').date()
            event_time_obj = datetime.strptime(event_time, '%H:%M').time()
        except ValueError:
            flash("Invalid date or time format.", "danger")
            return redirect(url_for('add_event'))

        new_event = Event(
            title=title,
            description=description,
            location=location,
            event_date=event_date_obj,
            event_time=event_time_obj,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            organizer_id=current_user.id,
            category_id=category_id if category_id else None
        )
        db.session.add(new_event)
        db.session.commit()
        flash('Event added successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('add_event.html', categories=categories)

@app.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.organizer_id != current_user.id:
        flash("Access denied. You are not the organizer of this event.", "danger")
        return redirect(url_for('home'))

    categories = Category.query.order_by(Category.name).all()

    if request.method == 'POST':
        event.title = request.form['title']
        event.description = request.form['description']
        event.location = request.form['location']
        event.event_date = datetime.strptime(request.form['event_date'], '%Y-%m-%d').date()
        event.event_time = datetime.strptime(request.form['event_time'], '%H:%M').time()
        event.category_id = request.form.get('category_id') or None
        event.updated_at = datetime.now()

        db.session.commit()
        flash("Event updated successfully.", "success")
        return redirect(url_for('home'))

    return render_template('edit_event.html', event=event, categories=categories)

@app.route('/event/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.organizer_id != current_user.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for('home'))
    db.session.delete(event)
    db.session.commit()
    flash("Event deleted successfully.", "info")
    return redirect(url_for('home'))

@app.route('/event/<int:event_id>/register', methods=['POST'])
@login_required
def register_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.is_past:
        flash("Cannot register for a past event.", "warning")
    elif not EventRegistration.query.filter_by(event_id=event_id, user_id=current_user.id).first():
        db.session.add(EventRegistration(event_id=event_id, user_id=current_user.id))
        db.session.commit()
        flash("Successfully registered for the event.", "success")
    else:
        flash("You are already registered for this event.", "info")
    return redirect(url_for('home'))

@app.route('/event/<int:event_id>/feedback', methods=['GET', 'POST'])
@login_required
def give_feedback(event_id):
    registration = EventRegistration.query.filter_by(event_id=event_id, user_id=current_user.id).first()
    if not registration:
        flash("You must register for the event before leaving feedback.", "warning")
        return redirect(url_for('home'))

    if request.method == 'POST':
        comment = request.form['comment']
        rating = int(request.form['rating'])
        feedback = Feedback(event_id=event_id, user_id=current_user.id, comment=comment, rating=rating, submitted_at=datetime.now())
        db.session.add(feedback)
        db.session.commit()
        flash("Feedback submitted.", "success")
        return redirect(url_for('home'))

    return render_template('feedback.html', event_id=event_id)

@app.route('/my_events')
@login_required
def my_events():
    events = Event.query.filter_by(organizer_id=current_user.id).order_by(Event.event_date).all()
    event_data = []
    for event in events:
        registrants = EventRegistration.query.filter_by(event_id=event.id).count()
        feedbacks = Feedback.query.filter_by(event_id=event.id).all()
        event_data.append({'event': event, 'registrants': registrants, 'feedbacks': feedbacks})
    return render_template('my_events.html', event_data=event_data, current_date=date.today())

@app.route('/event/<int:event_id>/registrants')
@login_required
def view_registrants(event_id):
    event = Event.query.get_or_404(event_id)
    if event.organizer_id != current_user.id:
        flash("Access denied.", "danger")
        return redirect(url_for('home'))
    registrations = EventRegistration.query.filter_by(event_id=event_id).all()
    return render_template('view_registrants.html', registrations=registrations, event=event)

@app.route('/event/<int:event_id>/view_feedback')
@login_required
def view_feedback(event_id):
    event = Event.query.get_or_404(event_id)
    if event.organizer_id != current_user.id:
        flash("Access denied.", "danger")
        return redirect(url_for('home'))
    feedbacks = Feedback.query.filter_by(event_id=event_id).all()
    return render_template('view_feedback.html', feedbacks=feedbacks, event=event)

@app.route('/dashboard')
@login_required
def dashboard():
    categories = Category.query.all()
    chart_data = []
    for category in categories:
        count = Event.query.filter_by(category_id=category.id).count()
        chart_data.append({'category': category.name, 'count': count})
    return render_template('dashboard.html', chart_data=chart_data)

@app.route('/moderate_feedback')
@login_required
def moderate_feedback():
    if current_user.role != 'admin':
        flash("Admins only.", "danger")
        return redirect(url_for('home'))
    feedbacks = Feedback.query.all()
    return render_template("moderate_feedback.html", feedbacks=feedbacks)

@app.route('/feedback/delete/<int:feedback_id>', methods=['POST'])
@login_required
def delete_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    if current_user.role != 'admin':
        flash("Unauthorized", "danger")
        return redirect(url_for('home'))
    db.session.delete(feedback)
    db.session.commit()
    flash("Feedback deleted.", "info")
    return redirect(url_for('moderate_feedback'))

# NEW: Admin-only route to initialize DB
@app.route('/initdb')
@login_required
def init_db():
    if current_user.role == 'admin':
        db.create_all()
        flash("Database initialized successfully!", "success")
    else:
        flash("Access denied. Admin only.", "danger")
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # ensures tables are created without wiping old data
    app.run(debug=True)
