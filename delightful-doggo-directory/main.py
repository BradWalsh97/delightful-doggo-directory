from flask import Blueprint, request, send_file

from .extensions import mongo

import os

from werkzeug.utils import secure_filename
from .doggoVision import checkIfIsDog

main = Blueprint("main", __name__)

# todo: add to env vars
UPLOAD_FOLDER = os.getcwd() + "/delightful-doggo-directory/daDoggoDirectory"
ALLOWED_EXTENSIONS = ["PNG", "JPG", "JPEG", "GIF"]


@main.route("/")
def index():
    return "<h1>Welcome to the Digital Doggo Directory! \n Home of the goodest boys/gorls</h1>"


@main.route("/newdog/", methods=["GET", "POST"])
def upload():
    print("Current dir: " + os.getcwd())

    # if its a post, and then if the request contains a file -> get the image
    if request.method == "POST":
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

    isDog = checkIfIsDog(filePath, image)

    if isDog:
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


# def createDbEntryForNewDoggo(filename):
# here we're going to want to create an entry in the atlas db


@main.route("/search/<path:filename>", methods=["GET"])
def findDoggo(filename):
    # before looking for the file, we want to secure the filename first, like we did with
    # the upload. The other's aren't needed since if the filename is empty or doesn't exist,
    # the os.path.isfile() will return false.
    secureFilename = secure_filename(filename)
    filePath = os.path.join(UPLOAD_FOLDER, secureFilename)

    # check to see if file exists, if it does send it to the user. Otherwise say it doesn't exist
    if os.path.isfile(filePath):
        return send_file(filePath)
    else:
        return "Unfortuntely that doggo has not yet been saved here."
