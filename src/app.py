import json
from flask import Flask, request
from db import db
from db import Songs
from db import User
db_filename = "cms.db"
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_filename}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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

@app.route("/create/user/", methods=["POST"])
def create_user():
    """
    Creates a user
    """
    body = json.loads(request.data)
    name = body.get("name")
    class_year = body.get("class_year")
    if name is None or class_year is None:
        return failure_response("missing a field")
    new_user = User(name=name,class_year=class_year)
    db.session.add(new_user)
    db.session.commit()
    return success_response(new_user.serialize())

@app.route("/delete/user/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    """
    Deletes a user
    """
    user = User.query.filter_by(id = user_id).first()
    if user is None:
        return failure_response("user not found")
    db.session.delete(user)
    db.session.commit()
    return success_response(user.serialize())
  
@app.route("/create/song/<int:user_id>/", methods = ["POST"])
def create_song(user_id):
    """
    Creates a song
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("user not found")
    body = json.loads(request.data)
    new_song = Songs(
        name = body.get("name"),
        description = body.get("description"),
        song_link = body.get("song_link"),
        user_id = user_id
    )
    db.session.add(new_song)
    db.session.commit()
    return success_response(new_song.serialize())
    

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
