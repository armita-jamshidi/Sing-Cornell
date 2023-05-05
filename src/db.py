from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import base64
import boto3
import datetime
import io
from io import BytesIO
from mimetypes import guess_extension, guess_type
import os
from PIL import Image
import random
import re
import string


db = SQLAlchemy()
EXTENSIONS = ["png", "gif", "jpg", "jpeg"]
BASE_DIR = os.getcwd()
S3_BUCKET_NAME= os.environ.get("S3_BUCKET_NAME")
S3_BASE_URL = f"https://{S3_BUCKET_NAME}.s3.us-east-1.amazonaws.com"

class Asset(db.Model):
    """
    Image Model
    """
    __tablename__="assets"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    base_url = db.Column(db.String, nullable=True)
    salt = db.Column(db.String, nullable=False)
    extension = db.Column(db.String, nullable=False)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey("song.id"), nullable=False)
    def __init__(self, **kwargs):
        self.song_id=kwargs.get("song_id")
        self.create(kwargs.get("image_data"))
    def create(self, image_data):
        """
        Given an image in base64 form:
        1. Rejects the image is it is not a file type that's supported
        2. Generates a random string for the image filename
        3. Decode the image and attempt to upload it to AWS
        """

        try:
            #gets extension of image - png, jpg
            ext = guess_extension(guess_type(image_data)[0])[1:]
            #only accepted if supported filetype
            if ext not in EXTENSIONS:
                raise Exception(("Unsupported file type: {ext}"))

            #generate random string for image securely
            salt = "".join(
                random.SystemRandom().choice(
                    string.ascii_uppercase + string.digits
                )
                for _ in range(16)
            )

            #remove header of base64 string
            #substitute the first quote with the second quote
            img_str = re.sub("^data:image/.+;base64,", "", image_data)
            img_data = base64.b64decode(img_str)
            img = Image.open(BytesIO(img_data))

            self.base_url = S3_BASE_URL
            self.salt = salt
            self.extension = ext
            self.width = img.width
            self.height = img.height
            self.created_at = datetime.datetime.now()

            img_filename = f"{self.salt}.{self.extension}"
            self.upload(img, img_filename)
        except Exception as e:
            print(f"Error when creating the image: {e}")
            
    def upload(self, img, img_filename):
        """
        Attempt to upload the image to the specified S3 bucket
        """
        try:
            #save image temporarily on server
            img_temp_loc = f"{BASE_DIR}/{img_filename}"
            img.save(img_temp_loc)

            #upload the image to S3
            s3_client = boto3.client("s3")
            s3_client.upload_file(img_temp_loc, S3_BUCKET_NAME, img_filename)

            #make S3 image url public
            s3_resource = boto3.resource("s3")
            object_acl = s3_resource.ObjectAcl(S3_BUCKET_NAME, img_filename)
            object_acl.put(ACL="public-read")

            #delete image from server
            os.remove(img_temp_loc)
            
        except Exception as e:
            print(f"Error when uploading the image: {e}")
    def serialize(self):
        return{
            "url": f"{self.base_url}/{self.salt}.{self.extension}",
            "created_at": str(self.created_at)
        }
class Songs(db.Model):
    """
    Song model
    """

    __tablename__ = "song"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    artistname =db.Column(db.String, nullable=False)
    song_link = db.Column(db.String, nullable = False)
    image = db.relationship("Asset", cascade ="delete")


    def __init__(self, **kwargs):
        """
        Initializes a Song object
        """
        self.name = kwargs.get("name")
        self.description = kwargs.get("description")
        self.artistname = kwargs.get("artistname")
        self.song_link = kwargs.get("song_link")
        

    def serialize(self):
        """
        Serialzies Song object
        """

        return{
            "id": self.id,
            "name": self.name, 
            "description": self.description,
            "artistname":self.artistname,
            "song_link":self.song_link,
            "image": [s.serialize() for s in self.image]
            
        }
    
