from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'some_secret_key'  # needed for flashing messages

# Replace with your MySQL credentials and database name
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mySQL%401611@localhost/ticket_booking'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Theatre model
class Theatre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

# Define the Movie model
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

# Define the Booking model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    theatre_id = db.Column(db.Integer, db.ForeignKey('theatre.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    tickets = db.Column(db.Integer, nullable=False)
    
    theatre = db.relationship('Theatre', backref=db.backref('bookings', lazy=True))
    movie = db.relationship('Movie', backref=db.backref('bookings', lazy=True))

@app.route('/', methods=['GET', 'POST'])
def book_ticket():
    theatres = Theatre.query.all()
    movies = Movie.query.all()
    
    if request.method == 'POST':
        theatre_id = request.form.get('theatre')
        movie_id = request.form.get('movie')
        tickets = request.form.get('tickets')

        # Basic validation
        if not theatre_id or not movie_id or not tickets:
            flash("Please fill in all fields")
            return redirect(url_for('book_ticket'))
        try:
            tickets = int(tickets)
        except ValueError:
            flash("Number of tickets must be an integer")
            return redirect(url_for('book_ticket'))

        # Save the booking to the database
        booking = Booking(theatre_id=theatre_id, movie_id=movie_id, tickets=tickets)
        db.session.add(booking)
        db.session.commit()
        flash("Booking successful!")
        return redirect(url_for('book_ticket'))

    return render_template('booking.html', theatres=theatres, movies=movies)

if __name__ == '__main__':
    # Initialize the database and pre-populate data within the application context.
    with app.app_context():
        db.create_all()
        # Hardcode theatre names if not already in the database
        if Theatre.query.count() == 0:
            theatres = ['Theatre 1', 'Theatre 2', 'Theatre 3']
            for name in theatres:
                db.session.add(Theatre(name=name))
        # Hardcode movie names if not already in the database
        if Movie.query.count() == 0:
            movies = ['Movie A', 'Movie B', 'Movie C']
            for name in movies:
                db.session.add(Movie(name=name))
        db.session.commit()

    app.run(debug=True)
