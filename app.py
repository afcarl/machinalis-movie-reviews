import click

from csv import DictReader

from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy

import settings

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE
db = SQLAlchemy(app)


#
# Models
#


class User(db.Model):
    """A user of the machinalis-movie-reviews site"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(255))

    def __init__(self, username, email, password=None):
        self.username = username
        self.email = email
        self.password = password

    def __str__(self):
        return 'User[id={id}, username={username}, email={email}]'.format(id=self.id,
                                                                          username=self.username,
                                                                          email=self.email)


class Movie(db.Model):
    """An IMDB listed movie"""
    id = db.Column(db.Integer, primary_key=True)
    movie_title = db.Column(db.String(255), nullable=False)
    duration = db.Column(db.SmallInteger)
    director_name = db.Column(db.String(255))
    actor_1_name = db.Column(db.String(255))
    actor_2_name = db.Column(db.String(255))
    actor_3_name = db.Column(db.String(255))
    genres = db.Column(db.String(255))
    movie_imdb_link = db.Column(db.String(255))
    language = db.Column(db.String(63))
    country = db.Column(db.String(63))
    content_rating = db.Column(db.String(15))
    title_year = db.Column(db.String(4))
    imdb_score = db.Column(db.Float)
    movie_facebook_likes = db.Column(db.BigInteger)

    def __init__(self, movie_title, duration=None, director_name=None, actor_1_name=None,
                 actor_2_name=None, actor_3_name=None, genres=None, movie_imdb_link=None,
                 language=None, country=None, content_rating=None, title_year=None,
                 imdb_score=None, movie_facebook_likes=None):
        self.movie_title = movie_title
        self.duration = duration
        self.director_name = director_name
        self.actor_1_name = actor_1_name
        self.actor_2_name = actor_2_name
        self.actor_3_name = actor_3_name
        self.genres = genres
        self.movie_imdb_link = movie_imdb_link
        self.language = language
        self.country = country
        self.content_rating = content_rating
        self.title_year = title_year
        self.imdb_score = imdb_score
        self.movie_facebook_likes = movie_facebook_likes

    def __str__(self):
        return ('Movie['
                'id={id}, '
                'movie_title={movie_title}, '
                'duration={duration}, '
                'director_name={director_name}, '
                'actor_1_name={actor_1_name}, '
                'actor_2_name={actor_2_name}, '
                'actor_3_name={actor_3_name}, '
                'genres={genres}, '
                'movie_imdb_link={movie_imdb_link}, '
                'language={language}, '
                'country={country}, '
                'title_year={title_year}, '
                'imdb_score={imdb_score}, '
                'movie_facebook_likes={movie_facebook_likes}'
                ']').format(id=self.id, movie_title=self.movie_title, duration=self.duration,
                            director_name=self.director_name, actor_1_name=self.actor_1_name,
                            actor_2_name=self.actor_2_name, actor_3_name=self.actor_3_name,
                            genres=self.genres, movie_imdb_link=self.movie_imdb_link,
                            language=self.language, country=self.country,
                            title_year=self.title_year, imdb_score=self.imdb_score,
                            movie_facebook_likes=self.movie_facebook_likes)

#
# Database
#


@app.cli.command('init_db')
def init_db_command():
    """Initializes the database"""
    click.echo("Initializing database...")
    db.create_all()


@app.cli.command('destroy_db')
def destroy_db_command():
    """Drops all tables from the database"""
    click.echo("Destroyig database...")
    db.drop_all()


@app.cli.command('import_movie_dataset')
@click.argument('movie_dataset_path')
def import_movie_dataset(movie_dataset_path):
    """
    Imports the IMDB 5000 movie dataset from
    https://www.kaggle.com/deepmatrix/imdb-5000-movie-dataset
    """
    click.echo("Dropping existing movie entries...")
    Movie.query.delete()

    click.echo("Importing IMDB 5000 movie dataset...")
    with open(movie_dataset_path) as csv_file:
        reader = DictReader(csv_file)
        movies = [ Movie(row['movie_title'], duration=row['duration'],
                         director_name=row['director_name'], actor_1_name=row['actor_1_name'],
                         actor_2_name=row['actor_2_name'], actor_3_name=row['actor_3_name'],
                         genres=row['genres'], movie_imdb_link=row['movie_imdb_link'],
                         language=row['language'], country=row['country'],
                         title_year=row['title_year'], imdb_score=row['imdb_score'],
                         movie_facebook_likes=row['movie_facebook_likes'])
                   for row in reader ]
        db.session.bulk_save_objects(movies)
        db.session.commit()


#
# Endpoints
#


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')
