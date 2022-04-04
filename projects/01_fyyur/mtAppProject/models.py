from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


genre_artist = db.Table('artist_genres',
  db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'), primary_key=True),
  db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)

genre_venue = db.Table('venue_genres',
  db.Column('venue_id', db.Integer, db.ForeignKey('venues.id'), primary_key=True),
  db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(1000))
    website = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venues', lazy=True)
    # artists = db.relationship('Artist', secondary=shows, backref=db.backref('venues', lazy=True))

    def __repr__(self):
      return f'<Venue records for {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String(120))
    website = db.Column(db.String(500))
    # genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venues = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(1000))
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'))
    shows = db.relationship('Show', backref='artists', lazy=True)
    
   
    

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
class Show(db.Model):
  __tablename__ = 'shows'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
  start_time = db.Column(db.DateTime)

class Genre(db.Model):
  __tablename__ = 'genres'
  id=db.Column(db.Integer, primary_key=True)
  name=db.Column(db.String, nullable=False)
  artists = db.relationship('Artist', secondary=genre_artist, backref=db.backref('genres', lazy=True))
  venues = db.relationship('Venue', secondary=genre_venue, backref=db.backref('genres', lazy=True))

class City(db.Model):
  __tablename__='cities'
  id=db.Column(db.Integer, primary_key=True)
  city=db.Column(db.String(120), nullable=False)
  state=db.Column(db.String(120), nullable=False)
  venues = db.relationship('Venue', backref='city', lazy=True)
  artist = db.relationship('Artist', backref='city', lazy=True)