"""
movie_recommendations commands
"""

import click

from csv import DictReader
from random import randint
from zipfile import ZipFile
from io import TextIOWrapper

from sqlalchemy.sql.expression import func

from movie_recommendations import app, db, factories, models, user_datastore


@app.cli.command('init_db')
def init_db_command():
    """Initializes the database"""
    click.echo("Initializing database...")
    db.create_all()


@app.cli.command('destroy_db')
def destroy_db_command():
    """Drops all tables from the database"""
    click.echo("Destroying database...")
    db.drop_all()


@app.cli.command('import_movie_dataset')
@click.argument('movie_dataset_path')
def import_movie_dataset(movie_dataset_path):
    """
    Imports the IMDB 5000 movie dataset from
    https://www.kaggle.com/deepmatrix/imdb-5000-movie-dataset
    """
    click.echo("Dropping existing movie entries...")
    models.Movie.query.delete()

    click.echo("Importing IMDB 5000 movie dataset...")
    with ZipFile(movie_dataset_path) as movie_dataset_zipfile:
        with movie_dataset_zipfile.open('movie_metadata.csv') as csv_file:
            reader = DictReader(TextIOWrapper(csv_file))
            movies = [ models.Movie(row['movie_title'], duration=row['duration'],
                                    director_name=row['director_name'],
                                    actor_1_name=row['actor_1_name'],
                                    actor_2_name=row['actor_2_name'], actor_3_name=row['actor_3_name'],
                                    genres=row['genres'], movie_imdb_link=row['movie_imdb_link'],
                                    language=row['language'], country=row['country'],
                                    title_year=row['title_year'], imdb_score=row['imdb_score'],
                                    movie_facebook_likes=row['movie_facebook_likes'])
                       for row in reader ]
            db.session.bulk_save_objects(movies)
            db.session.commit()


@app.cli.command('generate_user_network')
def generate_user_network():
    """Generates a random set of users and its connections"""
    click.echo('Dropping existing user entries...')
    models.User.query.delete()

    click.echo('Generating user1, user2, user3, and user4 accounts...')
    for i in range(1, 5):
        user_datastore.create_user(name='User {}'.format(i), username='user{}'.format(i),
                                   email='user{}@movie-recommendations.local'.format(i),
                                   password='user{}'.format(i))
    db.session.commit()

    click.echo("Generating additional fake user accounts...")

    for _ in range(25):
        user_datastore.create_user(**factories.get_fake_user_data())
    db.session.commit()

    click.echo("Population fake user connections...")

    for _ in range(10):
        user = (models.User.query
                .filter(models.User.follows == None)
                .filter(~models.User.username.like('user%'))
                .order_by(func.random()).limit(1).one())
        follows = (models.User.query
                   .filter(models.User.id != user.id)
                   .order_by(func.random()).limit(randint(1,5)).all())
        user.follows = follows
        db.session.merge(user)

    db.session.commit()
