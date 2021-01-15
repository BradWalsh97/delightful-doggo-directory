import os
import json
from flask import Blueprint, request, send_file
from dotenv import load_dotenv, find_dotenv
from bson import json_util
from werkzeug.utils import secure_filename
from delightful_doggo_directory.doggoVision import checkIfIsDog
from delightful_doggo_directory.dbTools import User
from mongoengine import *

main = Blueprint("main", __name__)
BASEDIR = os.path.abspath(os.path.dirname(__file__))
# load_dotenv(dotenv_path=os.path.join(BASEDIR, ".env"))
load_dotenv()

# Create some often used vars
UPLOAD_FOLDER = os.getcwd() + "/delightful-doggo-directory/daDoggoDirectory"
ALLOWED_EXTENSIONS = ["PNG", "JPG", "JPEG", "GIF"]

# connect to the database
connect(
    db="Users",
    username=os.getenv("MONGO_USER"),
    password=os.getenv("MONGO_PASS"),
    host=os.getenv("MONGO_URI"),
)


@main.route("/")
def index():
    return "<h1>Welcome to the Digital Doggo Directory! \n Home of the goodest boys/gorls</h1>"


@main.route("/newdog/", methods=["GET", "POST"])
def upload():
    # if its a post, check to ensure user exists. If they do, process the file
    if request.method == "POST":
        # start by checking to see if the user exists
        try:
            user = User.objects(username=request.args["username"]).get()
        except DoesNotExist:
            return "That user does not exist"

        if request.files:
            # check that file has a name, is supported file type, and has a secure file name (no malicious code or whatever else)
            image = request.files["image"]
            # print(image) #uncomment for debugging

            # check if file has a name
            if image.filename == "":
                print("Provided image has no name")
                return "Please upload an image with a name!"
            # check if filetype is supportedfilename
            if not checkIfValidImageType(image.filename):
                return "Please provide a valid file type."
            # make sure no sneaky malicious code is in the filename (just use werkzeug)
            else:
                filename = secure_filename(image.filename)

            # now that we have a secured file name, lets save the total path
            filePath = os.path.join(UPLOAD_FOLDER, filename)

            # check if file with that name already exists
            if os.path.exists(filePath):
                return "A picture with that name already exists"

            # if all checks are passed, save the image in the specified folder
            image.save(filePath)

            print("Image with name " + filename + " saved in" + UPLOAD_FOLDER)
        else:
            return "Please provide a file with your doggo request"

    # now that we've processes the image, we want to ensure that its actually a dog
    isDog = checkIfIsDog(filePath, image)

    # if the user has uploaded a new doggo, then we increase their credits and compliment the doggo
    if isDog:
        user.update_one(inc__credit_count=1)
        return "Wow, thats a good doggo!"

    else:
        # I don't like that I need to remove it after saving it but for the
        # moment it need to be done since the way GCP works I need to send it
        # the saved image. I'd like to find a better way to do this in the future
        os.remove(os.path.join(UPLOAD_FOLDER, filename))
        return "Hmmm, that ain't no doggo!"


def checkIfValidImageType(filename):
    if not "." in filename:
        return False

    extension = filename.rsplit(".", 1)[1]

    if extension.upper() in ALLOWED_EXTENSIONS:
        return True
    else:
        return False


@main.route("/search/<path:filename>", methods=["GET"])
def findDoggo(filename):
    # when a user searches, they will use one of their credits.
    # thus, first check to make sure the user exists and has credits
    try:
        user = User.objects(username=request.args["username"]).get()
        print(user.credit_count)
    except DoesNotExist:
        return "That user does not exist"

    if user.credit_count == 0:
        return "You do not have enough credits to find a doggo."
    print("credits: " + str(user.credit_count))
    print(user.json())

    # before looking for the file, we want to secure the filename first, like we did with
    # the upload. The other's aren't needed since if the filename is empty or doesn't exist,
    # the os.path.isfile() will return false.
    secureFilename = secure_filename(filename)
    filePath = os.path.join(UPLOAD_FOLDER, secureFilename)

    # check to see if file exists, if it does send it to the user and decrement their credits. Otherwise say it doesn't exist
    if os.path.isfile(filePath):
        user.update(dec__credit_count=1)
        return send_file(filePath)
    else:
        return "Unfortuntely that doggo has not yet been saved here."


@main.route("/user/", methods=["POST"])
def createUser():
    if request.method == "POST":
        # create the user and return any issues that might occur to the user
        try:
            User(
                username=request.args["username"],
                email=request.args["email"],
                password=request.args["password"],
                credit_count=request.args["credit_count"],
            ).save()
        except NotUniqueError:
            return "This user already exists! Please create a new one :)"

    return "The new user as been added!"


@main.route("/user/", methods=["GET"])
def getUser():
    try:
        user = User.objects(username=request.args["username"]).get()
        return str(user.json())
    except DoesNotExist:
        return "That user does not exist, please try again :)"


@main.route("/user", methods=["DELETE"])
def deleteUser():
    if request.method == "DELETE":
        try:
            user = User.objects(username=request.args["username"]).get()
            user.delete()
        except DoesNotExist:
            return "That user does not exist, please try again :)"


# todo: when a user adds a pic, increment credit
# when user gets a pic, remove one credit
# delete user
# buy more credits?
# store what pictures are associated to that user?
