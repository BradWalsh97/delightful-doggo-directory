import os
import random

import mongoengine as mongo
from flask import Blueprint, request, send_file
from werkzeug.utils import secure_filename

from delightful_doggo_directory.dbTools import User
from delightful_doggo_directory.doggoVision import checkIfIsDog

doggo = Blueprint("doggo", __name__)

# Declare some often used constants
BASEDIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.getcwd() + "/resources/daDoggoDirectory"
ALLOWED_EXTENSIONS = ["PNG", "JPG", "JPEG", "GIF"]

# Connec to MongoDB database
mongo.connect(
    db=os.getenv("MONGO_DB_NAME"),
    username=os.getenv("MONGO_USER"),
    password=os.getenv("MONGO_PASS"),
    host=os.getenv("MONGO_URI"),
)

# Main route which just returns html
@doggo.route("/")
def index():
    return "<h1>Welcome to the Digital Doggo Directory! \n Home of the goodest boys/gorls</h1>"


@doggo.route("/doggo/", methods=["POST"])
def upload():
    """This method will be called when a POST request is made to the /doggo/ route.
        It will attempt to save the provided image and credit the user who uploaded it

    Parameters
    ----------
    image and username in the body of the request (as form-data)

    Raises
    ------
    DoesNotExist
        If no user with the provided username is found

    Returns
    -------
        Returns a string that will either be an error message (dog already exists,
        user not found, etc) or a message indicating the doggo was succesfully stored
    """

    if request.method == "POST":
        try:
            user = User.objects(username=request.form["username"]).get()
        except DoesNotExist:
            return "That user does not exist"

        if request.files:
            filePath = verifyFile(request.files["image"])
            if filePath == "pic_already_exists":
                return "A picture with that name already exists"
            elif filePath == "pic_no_name":
                return "Please upload an image with a name!"
            elif filePath == "pic_invalid_type":
                return "Please provide a valid file type."
        else:
            return "Please provide a file with your doggo request"

    # now that we've processes the image, we want to ensure that its actually a dog
    isDog = checkIfIsDog(filePath, request.files["image"])

    # if the user has uploaded a new doggo, then we increase their credits and compliment the doggo
    if isDog:
        user.update(inc__credit_count=1)
        user.reload()
        return (
            "Wow, thats a good doggo! You now have "
            + str(user.credit_count)
            + " credits"
        )

    else:
        # I don't like that I need to remove it after saving it but for the
        # moment it needs to be done since the way GCP works I need to send it
        # the saved image. I'd like to find a better way to do this in the future
        os.remove(os.path.join(UPLOAD_FOLDER, filename))
        return "Hmmm, that ain't no doggo!"


def checkIfValidImageType(filename):
    """A function to check if the provided filename is valid

    Parameters
    ----------
    filename:
        the name of the file which we are trying to validate

    Returns
    -------
        True: the filetype is supported/valud
        False: the filetype is not supported or has no type
    """
    if not "." in filename:
        return False

    extension = filename.rsplit(".", 1)[1]

    if extension.upper() in ALLOWED_EXTENSIONS:
        return True
    else:
        return False


def verifyFile(image):
    """This method verifies that the file is valid. If will make sure the image
    has a name, has a valid file type, and will then sure the filename.

    Parameters
    ----------
        image: The image to verifty

    Returns
    -------
        String: either an error message or location where the file is saved
    """

    if image.filename == "":
        return "pic_no_name"
    if not checkIfValidImageType(image.filename):
        return "pic_invalid_type"
    # make sure no sneaky malicious code is in the filename (just use werkzeug)
    else:
        filename = secure_filename(image.filename)

    # now that we have a secured file name, lets save the total path
    filePath = os.path.join(UPLOAD_FOLDER, filename)

    # check if file with that name already exists
    if os.path.exists(filePath):
        return "pic_already_exists"  # TODO: what is the best way to do this?

    # if all checks are passed, save the image in the specified folder
    image.save(filePath)

    print("Image with name " + filename + " saved in" + UPLOAD_FOLDER)

    return filePath


@doggo.route("/doggo/", methods=["GET"])
def findDoggo():
    """This method will be called if a GET request is made to the /doggo/ route.
        It will return the requested file and remove a credit from the user

    Parameters
    ----------
    filename
        the filename of the doggo the user is looking for, sent in body of request
    username
        the username of the user who will have a credit removed for the request,
        sent in the body of the request

    Raises
    ------
    DoesNotExist
        Raised if the username provided does not exist in the database

    Returns
    -------
    String: An error message
    Picture: The requested image
    """

    filename = request.args["filename"]
    # when a user searches, they will use one of their credits.
    # thus, first check to make sure the user exists and has credits
    try:
        user = User.objects(username=request.args["username"]).get()
    except DoesNotExist:
        return "That user does not exist"
    if user.credit_count == 0:
        return "You do not have enough credits to find a doggo."

    # secure filename before looking for it
    secureFilename = secure_filename(filename)
    filePath = os.path.join(UPLOAD_FOLDER, secureFilename)

    # check to see if file exists, if it does send it to the user and decrement their credits.
    if os.path.isfile(filePath):
        user.update(dec__credit_count=1)
        return send_file(filePath)
    else:
        return "Unfortuntely that doggo has not yet been saved here."


@doggo.route("/doggo/", methods=["DELETE"])
def deleteDoggo():
    """This method will be called if a DELETE request is made to the /doogo/ route.
        It will attempt to delete a specified file (a doggo) :(

    Parameters
    ----------
    filename
        the name of the file the user wishes to delete

    Returns
    -------
    String: either an error message or a success message
        (Technically a success message, although its sad to see a delightful doggo leave the directory)
    """

    filename = secure_filename(request.args["filename"])
    filePath = os.path.join(UPLOAD_FOLDER, filename)

    if os.path.isfile(filePath):
        os.remove(filePath)
        return "The doggo has been removed, we're sad to see them go :("
    else:
        return "The doggo could not be found."


@doggo.route("/doggo/random", methods=["GET"])
def findRandomDoggo():
    """This method will be called if a GET request is made to the /doggo/random route
        It will return a random image and will remove one credit from the user

    Parameters
    ----------
    username
        the username of the user who will have a credit removed for the request,
        sent in the body of the request

    Raises
    -----
    DoesNotExist
        Raised if the username prvided does not exist in the database

    Returns
    -------
        String
            Error message, if one occurs
        Image
            A random image if no errors occur
    """

    randomFile = random.choice(os.listdir("resources/daDoggoDirectory"))

    try:
        user = User.objects(username=request.args["username"]).get()
    except DoesNotExist:
        return "That user does not exist"

    user.update(dec__credit_count=1)
    return send_file("resources/daDoggoDirectory/" + randomFile)


@doggo.route("/user/", methods=["POST"])
def createUser():
    """This metho is called when a POST request is made to the /user/ route.
        It will attempt to create a new user in the database

    Parameters
    ----------
    username
        the username the new user is the be given
    email
        the email of the new user
    password
        the password of the new user
    credit_count
        the amount of credits the user is to have upon creation

    Raises
    ------
    NotUniqueError
        Raised if the provided username already exists

    Returns
    -------
    String: Either an error message or a success message
    """

    if request.method == "POST":
        # create the user and return any issues that might occur to the user
        try:
            User(  # change to request.data
                username=request.forms["username"],
                email=request.forms["email"],
                password=request.forms["password"],
                credit_count=request.forms["credit_count"],
            ).save()
        except NotUniqueError:
            return "This user already exists! Please create a new one :)"

    return "The new user as been added!"


@doggo.route("/user/", methods=["GET"])
def getUser():
    """This method will be called if a GET request is made to the /user/ route
        It will get the details of a specified user

    Parameters
    ----------
    username
        the name of the user to get info about

    Raises
    ------
    DoesNotExist
        Raised if the username provided does not match a user in the database

    Returns
    -------
    String: Either the json of the user, or an error message saying the user doesn't exists
    """

    try:
        user = User.objects(username=request.args["username"]).get()
        return str(user.json())
    except DoesNotExist:
        return "That user does not exist, please try again :)"


@doggo.route("/user/", methods=["DELETE"])
def deleteUser():
    """This method will be called if a DELETE request is made to the /user/ route.
        It will attempt to delete the user of the provided username

    Parameters
    ----------
    username
        the username of the user to be deleted

    Raises
    ------
    DoesNotExist
        Raised if the provided username does not match an entry in the database
    """

    if request.method == "DELETE":
        try:
            user = User.objects(username=request.args["username"]).get()
            user.delete()
            return "Succesfully deleted " + request.args["username"]
        except DoesNotExist:
            return "That user does not exist, please try again :)"


@doggo.route("/user/credits", methods=["POST"])
def addCredits():
    """This method will be called if a POST request is made to the /user/credits route
        It will add the provided amount of credits to the speicified user

    Parameters
    ----------
    username
        the name of the user who is to have the credits added to
    credits
        the amount of credits to be added

    Raises
    ------
    DoesNotExist
        Raised of the username does not match a user in the database
    ValueError
        Raised of the credits provided isn't an integer value

    Returns
    -------
        String: Either an error message or how many credits have been added
                to the account along with how many credits the user now has
    """

    try:
        user = User.objects(username=request.form["username"]).get()
    except DoesNotExist:
        return "That user does not exist"

    try:
        newCredits = int(request.form["credits"])
    except ValueError:
        return "Please enter an number for the amount of credits"
    if newCredits <= 0:
        return "Please enter a value larger than 0 :)"
    user.update(inc__credit_count=newCredits)
    user.reload()

    return (
        str(newCredits)
        + " credits have been added to your account. You now have "
        + str(user.credit_count)
    )


@doggo.route("/user/credits", methods=["GET"])
def getCredits():
    """This method is called when a GET request is made to the /user/credits route.
        It will return the amount of credits a specified user has

    Parameters
    ----------
        username
            the name of the user whos credits are to be returned

    Raises
    ------
        DoesNotExist
            Raised if the username does not correspond to a user in the database

    Returns:
        String: Either an error message or the amount of credits the specified user has
    """

    try:
        user = User.objects(username=request.args["username"]).get()
    except DoesNotExist:
        return "That user does not exist"

    return user.username + " has " + str(user.credit_count) + " credits"


# TODO: get credit count


# TODO:
# full test and documentation
# delete user
# buy more credits?
# store what pictures are associated to that user?
# optimize imports
# verify arguments for doggoVision
# make sure alll requests have the if.request == check
# state that the username are case sensitive in documentation
# add delete doggo
# in documentation, say that doggos should be tied to users and that I'd like
#   to make is so only a user who uploaded the pic can remove it, etc.
