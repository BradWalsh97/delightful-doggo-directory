
# Delightful Doggo Directory
Welcome to the Delightful Doggo Directory, my implementation of [Shopify's Developer Challenge 2021](https://docs.google.com/document/d/1ZKRywXQLZWOqVOHC4JkF3LqdpO3Llpfk_CkZPR8bjak/edit).

## Introduction
The __Delightful-Doggo-Directory__ (aka DDD) is a flask based project which acts as an image repository where users can upload, search, and delete pictures of dogs. Users can interact with DDD through its REST API. Every time a user uploads a photo, they are given a credit which allows them to then either search for a random or specific doggo. DDD ensures that only Doggos are uploaded via Google's Vision API. If DDD is not 90% sure that an uploaded picture is a dog, the image will be rejected. 

## Instructions
1) Install Python (DDD was developed with `python 3.8.5`)
2) Create a virtual environment with `python3 -m venv /path/to/new/virtual/environment`
3) Active the venv with `source env/bin/activate`
4) Install project requirements with `pip install -r requirements.txt`
5) Start the Flask server with `python3 app.py`
   
Prior to running the app, you will need the following environment variables. A .env file can be created to avoid having to import them every time, it should be placed in the root of the project directory. 
```
MONGO_URI=<URI to mongoDB database>
MONGO_USER=<Mogo user username>
MONGO_PASS=<Password for mongo user>
MONGO_DB_NAME=<Name of Database>
GOOGLE_APPLICATION_CREDENTIALS=<path and filename of JSON file containing credentials for vision api>
```

## API Documentation

A premade Postman is included in the root of the project directory to simplify the DDD experience. It can be imported and the respective parameters can be tweaked for your liking. 

### /doggo/
   * `POST`: A post request to this route is to upload a document. The data must be contained in the body and passed as `form-data`
     * Request:
       * image: any supported file type,
       * username: string
     * Response:
       * String: Either an image acceptance message, rejection messiage, or an error message
   * `GET`: The get request is sent to this route to get a specified image. The data must be sent as querry parameters. 
     * Request:
       * filename: string of the name of the file you want
       * username: string of the user who will use a credit for the request
     * Response: (one of the two)
       * image: The requested image
       * string: An error message
   * `DELETE`: A delete request is sent to delete a specific photo from the Doggo Directory. The requested data must be sent as a querry parameter
     * Request:
       * filename: string of the filename to be deleted
     * Response:
       * string: either an error message or confirmation of deletion
  
  ### /doggo/random
  * `GET`: A get request at this route will return a random image of a doggo and remove one credit from the specified user. The requested data must be sent as querry parameters.
    * Request:
      * username: string
    * Response:
      * image
  
  ### /user/
   * `POST`: Making a POST request to this route will create a new user. The request data must be sent in the body of the request as `form-data`. 
     * Request:
       * username: string
       * email: string
       * passwor: string
       * credit_count: string
     * Response:
       * string: either error or success message
   * `GET`: A GET request at this route is used to get details of the specified user. The request data is to be sent as querry parameters
     * Request:
       * username: string
     * Response: 
       * string: either an error message or the json of the user details
   * `DELETE`: When a DELETE request is sent to this route, it will delete the specified user from the database. Data is to be passed in the querry params of the request. 
     * Request:
       * username: string
     * Response:
       * string: error or success message

  ### /user/credits
    * `POST`: A POST request is made to this route to add a specified amount of credits to the user's account. The requst data must be contained in the body of th request and be sent as `form-data`
      * Request:
        * username: string
        * credits: int
      * Response:
        * string: either success or error message
    * `GET`: A GET request on this route will return the amount of credits the specified user has. The data is to be passed as querry parameters. 
      * Request:
        * username, string
      * Response:
        * string: error message or the amount of credits the user has. 


## Future Improvements
Below is a list of improvements I'd like to make, features I'd like to add, and an aknowledgement of some of the flaws in the project. 

* Images should be tied to accounts
  * When a user uploads an image, a unique name should be assigned to it, which is referenced in the database. Only the owner of an image should be able to delete an image. 
* Login feature
  * Currently a user just needs to send a username, I'd like to implement a login feature where the user must have a valid username and password. 
* Password storage
  * Currently, the user's password is store as plain text. In the future, I'd like to make sure that the password is hashed before being stored. Then, login requests would require hasing the password and comparing it with what is stored in the database.
* Image tags
  * I'd also like to add a feature where a image would have tags, thus allowing users to not only search by filename but also tags including happy, running, smiling, etc. 
