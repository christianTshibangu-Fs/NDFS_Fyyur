from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database



#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# TODO: implement any missing fields, as a database migration using Flask-Migrate


 # TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.




class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(250))
    state = db.Column(db.String(250))
    address = db.Column(db.String(250))
    phone = db.Column(db.String(250), unique=True)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(250))
    web_link = db.Column(db.String(250))
    genres = db.Column(db.ARRAY(db.String(250)))
    search_talent = db.Column(db.Boolean(), default=True)
    search_description = db.Column(db.Text())
    shows = db.relationship('Show', backref='venue', lazy=True)

class Artiste(db.Model):
    __tablename__ = 'artistes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(250))
    state = db.Column(db.String(250))
    phone = db.Column(db.String(250), unique=True)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(250))
    web_link = db.Column(db.String(250))
    genres = db.Column(db.ARRAY(db.String(250)))
    search_venue = db.Column(db.Boolean(), default=True)
    search_description = db.Column(db.Text())
    shows = db.relationship('Show', backref='artist', lazy=True)

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.String, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artistes.id'), nullable=False)
