
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

db = SQLAlchemy()
# Base = declarative_base()

class Songs(db.Model):
    """
    Song model
    """

    __tablename__ = "song"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    # data = db.Column(db.LargeBinary)
    # engine = create_engine('sqlite:///audio.db')
    #ADD audio

    def __init__(self, **kwargs):
        """
        Initializes a Song object
        """
        self.name = kwargs.get("name")
        self.description = kwargs.get("description")
        self.user_id = kwargs.get("user_id")
        #ADD audio
        
      
    def serialize(self):
        """
        Serialzies Song object
        """

        return{
            "id": self.id,
            "name": self.name, 
            "description": self.description,
            "user_id": self.user_id
            #ADD audio
        }
    
class User(db.Model):
    """
    User model
    """

    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    class_year = db.Column(db.String, nullable=False)
    songs = db.relationship("Songs", cascade="delete")

    def __init__(self, **kwargs):
        """
        Initializes a User object
        """
        self.name = kwargs.get("name")
        self.class_year = kwargs.get("class_year")
    
    def get_songs(self):
        """
        Returns the songs for this User
        """
        songs= []
        for s in self.songs:
            songs.append(s)
        return songs
    
    def serialize(self):
        """
        Serializes a User object
        """
        songs = self.get_songs()
        return{"id": self.id, "name": self.name, "class_year": self.class_year, 
               "songs": [s.serialize() for s in songs]}
