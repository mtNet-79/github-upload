#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from pprint import pprint
import datetime
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# shows = db.Table('shows',
#   db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'), primary_key=True),
#   db.Column('venue_id', db.Integer, db.ForeignKey('venues.id'), primary_key=True)  
# )

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String(120))
    website = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venues = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(1000))
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'))
    shows = db.relationship('Show', backref='artists', lazy=True)

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

    def __repr__(self):
      return f'<Venue records for {self.name}>'



genre_artist = db.Table('artist_genres',
  db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'), primary_key=True),
  db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)

genre_venue = db.Table('venue_genres',
  db.Column('venue_id', db.Integer, db.ForeignKey('venues.id'), primary_key=True),
  db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)

class Genre(db.Model):
  __tablename__ = 'genres'
  id=db.Column(db.Integer, primary_key=True)
  name=db.Column(db.String, nullable=False)
  artists = db.relationship('Artist', secondary=genre_artist, backref=db.backref('genres', lazy=True))
  venues = db.relationship('Venue', secondary=genre_venue, backref=db.backref('genres', lazy=True))

    
   
    

#     # TODO: implement any missing fields, as a database migration using Flask-Migrate
class Show(db.Model):
  __tablename__ = 'shows'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
  start_time = db.Column(db.DateTime)
 

  

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class City(db.Model):
  __tablename__='cities'
  id=db.Column(db.Integer, primary_key=True)
  name=db.Column(db.String(120), nullable=False)
  state=db.Column(db.String(120), nullable=False)
  venues = db.relationship('Venue', backref='city', lazy=True)
  artist = db.relationship('Artist', backref='city', lazy=True)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  
  date = ''
  if isinstance(value, datetime):
    date = value
  else:
    date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  
  cities = City.query.all()
  data=[]
  for city in cities:
    dict = {}
    dict['city']  = city.name
    dict['state']  = city.state
    venues = Venue.query.filter_by(city_id=city.id).all()
    dict['venues'] = []
    if venues:
      for venue in venues:
        inr_dict = {}
        inr_dict['id'] = venue.id
        inr_dict['name'] = venue.name
        dict['venues'] .append(inr_dict)
      data.append(dict)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form['search_term']
  search_term = "%{}%".format(search_term)
  result = Venue.query.filter(Venue.name.ilike(search_term)).all()
  returns = {}
  returns['count'] = 0
  if result:
    returns['data'] = []
    for rcrd in result:
      returns['count'] +=1
      dict ={}
      dict['id']=rcrd.id
      dict['name']=rcrd.name 
      shows = Show.query.filter_by(venue_id=rcrd.id).all()
      dict['num_upcoming_shows'] = len(shows)
      returns['data'].append(dict)
  return render_template('pages/search_venues.html', results=returns, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # get record with pk id
  result = Venue.query.get(venue_id)
  data = request.get_json()

  # get genres 
  genres = result.genres
  garr = []
  for genre in genres:
    garr.append(genre.name)
  shows = result.shows
  pastshows = []
  pscount = 0
  futureshows= []
  fscount = 0
  for show in shows:
    artist = Artist.query.get(show.artist_id)
    artist_name = artist.name
    artist_image_link = artist.image_link
    start_time = show.start_time
    ct = datetime.now()
    if start_time < ct:
      pscount += 1
      pastshows.append({
        "artist_id": artist.id,
        "artist_name": artist_name,
        "artist_image_link": artist_image_link,
        "start_time": show.start_time
      })
    else:
      fscount += 1
      futureshows.append({
        "artist_id": artist.id,
        "artist_name": artist_name,
        "artist_image_link": artist_image_link,
        "start_time": show.start_time
      })

  data = {
    "id": result.id,
    "name":result.name,
    "genres": garr,
    "address": result.address,
    "city": result.city.name,
    "state": result.city.state,
    "phone": result.phone,
    "website": result.website,
    "facebook_link": result.facebook_link,
    "seeking_talent": result.seeking_talent,
    "seeking_description": result.seeking_description,
    "image_link": result.image_link,
    "past_shows": pastshows,
    "upcoming_shows": futureshows,
    "past_shows_count": pscount,
    "upcoming_shows_count": fscount,
  
  }


  # get number of shows in the db
  # get number of future shows only
  # build obj to pass to html
  
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  
  return render_template('pages/show_venue.html', venue=data)
  # return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------
genres = Genre.query.all()
choicesArr=[]
for genre in genres:      
    choicesArr.append((str(genre.id), genre.name))
# sort choices by alpha and 'other' as last choice
choicesArr.sort(key=lambda g : (g[1] == 'Other', g[1]))
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  
  # form = VenueForm(genres_choices=choices)
  form = VenueForm()
  form.genres.choices = choicesArr
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  body = {}
  form = VenueForm()
  form.genres.choices = choicesArr 
  if form.validate_on_submit():
    try:
      name = form.name.data
      city = form.city.data
      state = form.state.data
      address = form.address.data
      phone = form.phone.data
      genre_ids = form.genres.data
      facebook_link = form.facebook_link.data
      image_link = form.image_link.data
      website_link = form.website_link.data
      seeking_talent = form.seeking_talent.data
      seeking_description= form.seeking_description.data    
      city_id = None
      city_exists = City.query.filter_by(name=city).first()
      body['name'] = name
      body['city'] = city
      body['state'] = state
      body['address'] = address
      body['phone'] = phone

      genres=[]
      for gid in genre_ids:
        gname = Genre.query.get(gid).name
        genres.append(gname)

      body['genres'] = genres
      body['facebook_link'] = facebook_link
      body['image_link'] = image_link
      body['website_link'] = website_link
      body['seeking_talent'] = seeking_talent
      body['seeking_description'] = seeking_description
      body['seeking_talent'] = seeking_talent

      if city_exists is None:      
        try:
          new_city= City(name=city, state=state)
          db.session.add(new_city)
          db.session.commit()          
        except:
          db.session.rollback()
          error = True
          flash('Error on city insert.')
        finally:
          db.session.close()
        if error:
          abort(500)
        else:
          city_id = City.query.filter_by(name=city).first().id          
      else:
        city_id = city_exists.id
     
      venue = Venue(name=name, city_id=city_id, address=address, phone=phone, image_link=image_link, facebook_link=facebook_link,seeking_talent=seeking_talent,seeking_description=seeking_description,website=website_link)
      gModelArr=[]
      for g_id in genre_ids:
        genr=Genre.query.get(g_id)
        genr.venues=[venue]
        gModelArr.append(genr)
      venue.genres=gModelArr
      db.session.add(venue)
      db.session.flush()
      db.session.refresh(venue, attribute_names=['id'])
      body['id'] = venue.id
      db.session.commit()
    except:
      db.session.rollback()
      error = True
      flash('Error on insert.')
    finally:
        db.session.close()
    if error:
      abort(500)      
    else:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      # jsonres = jsonify(body)
      # response = Response(jsonres, mimetype='application/json')
      venue_id= body["id"]
      return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
    flash('An error occurred. Venue ' + request.form['name']  + ' could not be listed.')
  
    form = VenueForm()
    form.genres.choices = choicesArr
    return render_template('forms/new_venue.html', form=form)

  # # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    v = Venue.query.get(venue_id)
    db.session.delete(v)
    db.session.commit()
  except: 
    db.rollback()
    error=True
  finally:
    db.session.close()
  if error:
    abort(500)
  else:
    return jsonify({'success': True})
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
 

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  
  data = []
  artists = Artist.query.all()
  for artist in artists:
    data.append({
      'id': artist.id,
      "name": artist.name
    })
 
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form['search_term']
  search_term = "%{}%".format(search_term)
  result = Artist.query.filter(Artist.name.ilike(search_term)).all()
  returns = {}
  returns['count'] = 0
  if result:
    returns['data'] = []
    for rcrd in result:
      returns['count'] +=1
      dict ={}
      dict['id']=rcrd.id
      dict['name']=rcrd.name 
      shows = Show.query.filter_by(venue_id=rcrd.id).all()
      dict['num_upcoming_shows'] = len(shows)
      returns['data'].append(dict)
  return render_template('pages/search_artists.html', results=returns, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  result = Artist.query.get(artist_id)
  # get genres 
  genres = result.genres
  garr = []
  for genre in genres: 
    garr.append(genre.name)
  shows = result.shows
  pastshows = []
  pscount = 0
  futureshows= []
  fscount = 0
  for show in shows:
    venue = Venue.query.get(show.venue_id)
    venue_name = venue.name
    venue_image_link = venue.image_link
    start_time = show.start_time
    ct = datetime.now()
    if start_time < ct:
      pscount += 1
      pastshows.append({
        "venue_id": venue.id,
        "venue_name": venue_name,
        "venue_image_link": venue_image_link,
        "start_time": show.start_time
      })
    else:
      fscount += 1
      futureshows.append({
        "venue_id": venue.id,
        "venue_name": venue_name,
        "venue_image_link": venue_image_link,
        "start_time": show.start_time
      })
  data = {
    "id": result.id,
    "name":result.name,
    "genres": garr,
    "city": result.city.name,
    "state": result.city.state,
    "phone": result.phone,
    "website": result.website,
    "facebook_link": result.facebook_link,
    "seeking_venue": result.seeking_venues,
    "seeking_description": result.seeking_description,
    "image_link": result.image_link,
    "past_shows": pastshows,
    "upcoming_shows": futureshows,
    "past_shows_count": pscount,
    "upcoming_shows_count": fscount,
  
  }

  
 
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  city = City.query.get(artist.city_id)
  genres = artist.genres

  garr = []
  for g in genres:
    garr.append(g.id)

  formdata = {"name":artist.name, "city": city.name,"state": city.state, "phone": artist.phone, "website_link": artist.website, "facebook_link": artist.facebook_link, "seeking_venue": artist.seeking_venues, "seeking_description": artist.seeking_description, "image_link": artist.image_link, "genres": garr}
  form = ArtistForm(data=formdata)
  form.genres.choices = choicesArr
  form.genres.default = garr

  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()
  form.genres.choices = choicesArr
  body = {}
  error = False
 
  if form.validate_on_submit():
    try:
      body['genre_ids'] = form.genres.data
      artist = Artist.query.get(artist_id)
      artist.name = form.name.data
      artist.genres.clear()
      gModelArr = [] 
      for g_id in form.genres.data:
        gModelArr.append(Genre.query.get(g_id))
      artist.genres = gModelArr  
      city = City.query.filter_by(name=form.city.data).first()  
      if city:
        artist.city_id = city.id
      else:
        city = City(name=form.city.data, state=form.state.data)
        db.session.add(city)
        db.session.flush()
        db.session.refresh(city, attribute_names=['id'])
        artist.city_id = city.id
      artist.phone = form.phone.data
      artist.website = form.website_link.data
      artist.facebook_link = form.facebook_link.data
      artist.seeking_venues = form.seeking_venue.data
      artist.seeking_description = form.seeking_description.data
      artist.image_link = form.image_link.data
      db.session.flush()
      db.session.commit()
      db.session.close()
    except:
      db.session.rollback()
      error = True
    finally:
      db.session.close()
    if error:
      abort(500)
    else:
      return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
    flash('An error occurred. Artist ' + request.form['name']  + ' could not be listed.')
    return redirect(request.url)

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  venue = Venue.query.get(venue_id)
  city = City.query.get(venue.city_id)
  genres = venue.genres
  
  garr = []
  for g in genres:
    garr.append(g.id)
  formdata = {"name":venue.name, "city": city.name,"state": city.state,"address": venue.address, "phone": venue.phone, "website_link": venue.website, "facebook_link": venue.facebook_link, "seeking_talent": venue.seeking_talent, "seeking_description": venue.seeking_description, "image_link": venue.image_link, "genres": garr}
  form = VenueForm(data=formdata)
  form.genres.choices = choicesArr
  form.genres.default = garr
  


  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  form = VenueForm()
  form.genres.choices = choicesArr
  body = {}
  error = False
  if form.validate_on_submit():
    try:
      body['genre_ids'] = form.genres.data
      venue = Venue.query.get(venue_id)
      venue.name = form.name.data
      venue.genres.clear()
      gModelArr = []
      for g_id in form.genres.data:
        gModelArr.append(Genre.query.get(g_id))
      venue.genres = gModelArr  
      city_id = City.query.filter_by(name=form.city.data).first().id    
      if city_id:
        venue.city_id = city_id
      else:
        city = City(name=form.city.data, state=form.state.data)
        db.session.add(city)
        db.session.flush()
        db.session.refresh(city, attribute_names=['id'])
        venue.city_id = city.id
      venue.address = form.address.data
      venue.phone = form.phone.data
      venue.website = form.website_link.data
      venue.facebook_link = form.facebook_link.data
      venue.seeking_talent = form.seeking_talent.data
      venue.seeking_description = form.seeking_description.data
      venue.image_link = form.image_link.data
      db.session.flush()
      db.session.commit()
      db.session.close()
    except:
      db.session.rollback()
      error = True
    finally:
      db.session.close()
    if error:
      abort(500)
    else:
      return redirect(url_for('show_venue', venue_id=venue_id))
  # venue record with ID <venue_id> using the new attributes
  # return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  form.genres.choices = choicesArr
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  body = {}
  form = ArtistForm()
  form.genres.choices = choicesArr 
  if form.validate_on_submit():
    try:
      name = form.name.data
      city = form.city.data
      state = form.state.data
      phone = form.phone.data
      genre_ids = form.genres.data
      facebook_link = form.facebook_link.data
      image_link = form.image_link.data
      website_link = form.website_link.data
      seeking_venue = form.seeking_venue.data
      seeking_description= form.seeking_description.data    
      city_id = None
      city_exists = City.query.filter_by(name=city).first()
      body['name'] = name
      body['city'] = city
      body['state'] = state
      body['phone'] = phone

      genres=[]
      for gid in genre_ids:
        gname = Genre.query.get(gid).name
        genres.append(gname)

      body['genres'] = genres      
      body['facebook_link'] = facebook_link
      body['image_link'] = image_link
      body['website_link'] = website_link
      body['seeking_venue'] = seeking_venue
      body['seeking_description'] = seeking_description

      if city_exists is None:      
        try:
          new_city= City(name=city, state=state)
          db.session.add(new_city)
          db.session.commit()
          
        except:
          db.session.rollback()
          error = True
          flash('Error on city insert.')
        finally:
          db.session.close()
        if error:
          abort(500)
        else:
          city_id = City.query.filter_by(name=city).first().id          
      else:
        city_id = city_exists.id
      
      artist = Artist(name=name, city_id=city_id, phone=phone, image_link=image_link, facebook_link=facebook_link,seeking_description=seeking_description,seeking_venues=seeking_venue,website=website_link)
      gModelArr=[]
      for g_id in genre_ids:
        genr=Genre.query.get(g_id)
        genr.artists=[artist]
        gModelArr.append(genr)
      artist.genres=gModelArr
      db.session.add(artist)
      db.session.flush()
      db.session.refresh(artist, attribute_names=['id'])
      body['id'] = artist.id
      db.session.commit()
    except:
      db.session.rollback()
      error = True
      flash('Error on insert.')
    finally:
        db.session.close()
    if error:
      abort(500)      
    else:
      db.session.close()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      return redirect(url_for('show_artist', artist_id=body["id"]))
  
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
    flash('An error occurred. Artist ' + request.form['name']  + ' could not be listed.')
  
    form = ArtistForm()
    form.genres.choices = choicesArr
    return render_template('forms/new_artist.html', form=form)

  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  # return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
 
  ct = datetime.now()  
  shows = Show.query.all() 
  pastshows= []
  futureshows=[]
  
  for show in shows:
    venue_name = Venue.query.get(show.venue_id).name
    artist_name = Artist.query.get(show.artist_id).name
    artist_image_link = Artist.query.get(show.artist_id).image_link
    start_time = show.start_time
    ct = datetime.now()
    if start_time < ct:
       pastshows.append({
        "venue_id": show.venue_id,
        "venue_name": venue_name,
        "artist_id": show.artist_id,
        "artist_name": artist_name,
        "artist_image_link": artist_image_link,
        "start_time": show.start_time
      })
    else:
      futureshows.append({
        "venue_id": show.venue_id,
        "venue_name": venue_name,
        "artist_id": show.artist_id,
        "artist_name": artist_name,
        "artist_image_link": artist_image_link,
        "start_time": show.start_time
      })
  data = {"pastshows": pastshows, "futureshows": futureshows}
  return render_template('pages/shows.html', shows=data)
 
  

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  form = ShowForm()
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  artist_id = request.form['artist_id']
  venue_id = request.form['venue_id']  
  start_time = request.form['start_time'] 
  flash(f'start time: {start_time}')
  if form.validate_on_submit():   
    try:
      
       # show = Show(artist_id=form.artist_id.data, venue_id=form.venue_id.data, start_time=form.start_time.data)
      show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
      db.session.add(show)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Show could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      flash('Show Not submitted. server error.')
    finally:
      db.session.close()
    if error:
      abort(500)
    else:
      # on successful db insert, flash success
      flash('Show was successfully listed!')
      return render_template('pages/home.html')
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
    # flash('An error occurred. Artist ' + request.form['name']  + ' could not be listed.')
  
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)
  

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
