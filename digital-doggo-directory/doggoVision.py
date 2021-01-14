# Written with the help of the documentation here

import io
import os

from google.cloud import vision


def checkIfIsDog(pathToMaybeDoggo, mayBeDoggoImage):
    # Instantiate client
    client = vision.ImageAnnotatorClient()

    # load image into memory
    with io.open(pathToMaybeDoggo, "rb") as image_file:
        content = image_file.read()
    # content = maybeDoggoImage.read()

    image = vision.Image(content=content)

    # get the response from GCP and get the labels
    response = client.label_detection(image=image)
    labels = response.label_annotations

    # now we're going to look at the first two labels (two to
    # not only reduce processing time but also because all of my
    # tests have returned more than 2 labels) and see
    # what they are. If it is "Dog" with over 90% certainty, we assume
    # that the picture infact features a dog as its main subject.
    for i, label in zip(range(1), labels):
        # print(label) #uncomment for debuggin
        if label.description == "Dog" and label.score >= 0.9:
            return True

    return False

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )
