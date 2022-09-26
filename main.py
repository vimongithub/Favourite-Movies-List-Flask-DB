from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,FloatField,validators
from wtforms.validators import DataRequired
import requests

end_url = "https://api.themoviedb.org/3/search/movie?"
url_path = "https://image.tmdb.org/t/p/w600_and_h900_bestv2"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie-list.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
db = SQLAlchemy(app)


class EditRating(FlaskForm):
    rating = FloatField(label='Enter Your rating(eg- 7.5', validators=[DataRequired()])
    review = StringField(label="Your review", validators=[DataRequired(),validators.Length(max=300)])
    submit = SubmitField(label='Done')

class AddMovie(FlaskForm):
    title = StringField(label='Movie Title\n', validators=[DataRequired()])
    submit = SubmitField(label='Add Movie')


class Movie(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(300))
    img_url = db.Column(db.String(300), nullable=False, unique=True)

    def __repr__(self):
        return self.id
db.create_all()

#Comment out this code after adding movies

# new_movie = Movie(
#     title="Jai Bhim",
#     year=2021,
#     description="A pregnant woman from a primitive tribal community, searches desperately for her husband, who is missing from police custody. So as to find her husband and seek justice for them, as their voice, a High Court advocate rises in support. Will their battle for justice succeed?",
#     rating=9,
#     ranking=2,
#     review="Oscar deserved movie of 2021",
#     img_url="https://www.themoviedb.org/t/p/w600_and_h900_bestv2/mPMQl3voLNlZQt3STGV5KAcLN4h.jpg"
# )
#

@app.route("/")
def home():
    increment = 0
    # Sort table data in ascending order.
    all_movies = db.session.query(Movie).order_by(Movie.rating.asc()).all()

    for num in range(len(all_movies)):
        all_movies[num].ranking = len(all_movies) - increment
        increment += 1
    db.session.commit()

    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=['GET', 'POST'])
def edit():
    edit_data = EditRating()
    movie_id = request.args.get('id')
    movie_selected = Movie.query.get(movie_id)

    if edit_data.validate_on_submit() and request.method =='POST':
        movie_selected.rating = request.form["rating"]
        movie_selected.review = request.form["review"]
        db.session.commit()
        return redirect (url_for('home'))

    return render_template("edit.html", form=edit_data, movie=movie_selected)

@app.route("/delete", methods=['GET','POST'])
def remove_movie():
    movie_id = request.args.get('id')
    movie_selected = Movie.query.get(movie_id)
    db.session.delete(movie_selected)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/add", methods=['GET', 'POST'])
def add_movie():
    new_movie = AddMovie()
    if new_movie.validate_on_submit():
        movie_title = request.form["title"]
        response = requests.get(end_url, params={f'api_key':'dd38301a9d19bf8e75c76d23824358b6','query': {movie_title}}).json()
        data = response["results"]
        return render_template('select.html', options=data)

    return render_template('add.html', form=new_movie)

@app.route("/select", methods=['GET', 'POST'])
def select_movie():
    movie_id = request.args.get("id")
    response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=dd38301a9d19bf8e75c76d23824358b6').json()
    new_movie = Movie(
        title= response["title"],
        year=response["release_date"][0:4],
        description=response["overview"],
        img_url=url_path + response["poster_path"]
    )
    db.session.add(new_movie)

    db.session.commit()
    id = new_movie.__repr__()
    print(id)
    return redirect(url_for('edit', id=id))

if __name__ == '__main__':
    app.run(debug=True)
