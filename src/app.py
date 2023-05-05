import json
from flask import Flask, request
from db import db
from db import Songs
from db import Asset
from db import db
import os

db_filename = "song.db"
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()

#success and failure responses
def success_response(data, code=200):
    """
    Success response, 
    """
    return json.dumps(data), code

def failure_response(message, code=400):
    """
    Failure response
    """
    return json.dumps({"error": message}), code

@app.route("/")
@app.route("/music/")
def get_all_music():
    """
    Gets all Cornell music
    """
    songs = [song.serialize() for song in Songs.query.all()]
    return success_response({"songs": songs})
  
@app.route("/create/song/", methods = ["POST"])
def create_song():
    """
    Creates a song
    """
    body = json.loads(request.data)
    if body.get("name") is None:
        return failure_response("name not included")

    
    new_song = Songs(
        name = body.get("name"),
        description = body.get("description"),
        artistname = body.get("artistname"),
        song_link = body.get("song_link")
        
    )
    db.session.add(new_song)
    db.session.commit()
    return success_response(new_song.serialize(), 201)

@app.route("/image/<int:song_id>/song/", methods = ["POST"])
def upload(song_id):
    """
    Creates an image that is connected to the song id and returns the image url
    """
    song = Songs.query.filter_by(id=song_id).first()
    if song is None:
        return failure_response("Song not found!")
    body = json.loads(request.data)
    if body.get("image_data") is None:
        return failure_response("No base64 image to be found")
    image_data = body.get("image_data")
    asset = Asset(
        image_data=image_data,
        song_id=song_id
        )
    db.session.add(asset)
    db.session.commit()
    return success_response(asset.serialize(),201)
    
@app.route("/get/song/<int:song_id>/", methods=["GET"])
def get_song(song_id):
    """
    Gets a song
    """
    song = Songs.query.filter_by(id = song_id).first()
    if song is None:
        return failure_response("song not found")
    return success_response(song.serialize())


@app.route("/delete/song/<int:song_id>/", methods=["DELETE"])
def delete_song(song_id):
    """
    Deletes a song
    """
    song = Songs.query.filter_by(id = song_id).first()
    if song is None:
        return failure_response("song not found")
    db.session.delete(song)
    db.session.commit()
    return success_response(song.serialize())
  
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
