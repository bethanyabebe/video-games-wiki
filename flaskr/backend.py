# TODO(Project 1): Implement Backend according to the requirements.
from flask import Blueprint, request, Flask, render_template, session
from flask import request, Flask
from google.cloud import storage
import hashlib
from io import BytesIO
import urllib, base64

client = storage.Client()


class Backend:
    # class Backend holds the method to interact with the GSC, thus we initialize the bucket & storage client needed to access the correct blobs
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(bucket_name)

    def get_wiki_page(self, name):
        blob = self.bucket.blob(name)  #search for th page with the given name
        if blob.exists():
            return blob.download_as_string(
            )  #if the page exists return the string
        else:
            return None  #else, return None

    def get_all_page_names(self):
        blobs = self.storage_client.list_blobs(
            self.bucket_name)  #list all pages
        pages = {}  #empty dict
        for blob in blobs:  #read each blob
            if blob.content_type != 'image':  #if is not an image
                pages[blob.name] = blob  #save it in a dictionary
        return pages  #return all the pages

    def upload(self, page_name, page):
        blob = self.bucket.blob(page_name)  # get blob based on page_name
        img = ["image/jpeg", "image/jpg", "image/png"]  # valid image types
        if page.content_type in img:  # set content type to image if the page is an image
            blob.content_type = "image"
        with blob.open("wb") as f:  # write page contents to blob in cloud
            f.write(page.read())

    def sign_up(self, user_name, pwd, email):
        # get username, password from user, salt for hashing
        name = user_name
        password = pwd
        salt = "5gz"

        # Adding salt at the last of the password
        dataBase_password = password + salt
        # Encoding the password
        hashed_password = hashlib.md5(dataBase_password.encode())

        bucket = client.bucket('userspasswords')
        bucket2 = client.bucket('bio_and_gamepreferences')
        blob2 = bucket2.blob(name)
        blob = bucket.blob(name)

        if blob.exists():
            return 'Username already exsists'

        else:
            #Adds the encoded passsword to the created user blob
            with blob.open("w") as f:
                f.write(f"{hashed_password.hexdigest()}|{email}")
            with blob2.open("w") as f:
                f.write(
                    f"{name} hasn't added a bio|{name} hasn't added any favorite games|{name} hasn't added any favorite genres|{name} hasn't added any favorite developers|default_pic"
                )
                return None

    def sign_in(self, user_name, pwd):
        # get username, password from user, salt for hashing
        username = user_name
        password = pwd
        salt = "5gz"

        # Adding salt at the last of the password
        dataBase_password = password + salt
        # encoding the password
        hashed_password = hashlib.md5(dataBase_password.encode())

        bucket = client.bucket('userspasswords')
        blob = bucket.blob(username)

        #checks if the entered username exsists in the bucket
        if not blob.exists():
            return 'Invalid User'
        else:
            with blob.open("r") as f:
                psw = f.read().split(
                    '|')  # reads the stored password from the blob
            if hashed_password.hexdigest() != psw[0]:
                return 'Invalid Password'
            else:
                return username

    def get_image(self, image_name, blob_param=None):
        # get blob based on image name
        blobs = self.storage_client.list_blobs(self.bucket_name)

        # function decodes image to readable version to display on html page
        def decode_img(image):
            img_string = base64.b64encode(image.read())
            img = 'data:image/png;base64,' + urllib.parse.quote(img_string)
            return img

        # if (optional) blob supplied, decode image directly
        if blob_param:
            return decode_img(blob_param)

        # if not, find blob that matches image name and return decoded image
        for blob in blobs:
            if blob.name == image_name:
                with blob.open("rb") as b:
                    return decode_img(b)

    def profile(self, user_name):
        bucket = client.bucket('userspasswords')
        bucket2 = client.bucket('bio_and_gamepreferences')
        blob2 = bucket2.blob(user_name)
        blob = bucket.blob(user_name)

        with blob.open("r") as f:
            account_details = f.read().split('|')

        with blob2.open("r") as f:
            bio_details = f.read().split('|')

        profile_details = account_details + bio_details

        return profile_details

    def editprofile(self, user_name, profile_details):
        bucket = client.bucket('userspasswords')
        bucket2 = client.bucket('bio_and_gamepreferences')
        blob2 = bucket2.blob(user_name)
        blob = bucket.blob(user_name)
        edited_details = []

        if profile_details[0]:
            with blob.open("r") as f:
                psw = f.read().split('|')
            with blob.open("w") as f:
                f.write(f"{psw[0]}|{profile_details[0]}")

        with blob2.open("r") as f:
            bio_details = f.read().split('|')
        print(bio_details)
        for i in range(1, len(profile_details)):
            print(profile_details[i], "hey")
            if profile_details[i] != '':
                edited_details.append(profile_details[i])

            else:
                edited_details.append(bio_details[i - 1])

        edited_details.append(bio_details[-1])
        with blob2.open("w") as f:
            f.write(
                f'{edited_details[0]}|{edited_details[1]}|{edited_details[2]}|{edited_details[3]}|{edited_details[4]}'
            )

    def editprofilepic(self, user_name, avatar):
        bucket2 = client.bucket('bio_and_gamepreferences')
        blob2 = bucket2.blob(user_name)

        with blob2.open("r") as f:
            bio_details = f.read().split('|')

        bio_details[-1] = avatar

        with blob2.open("w") as f:
            f.write(
                f'{bio_details[0]}|{bio_details[1]}|{bio_details[2]}|{bio_details[3]}|{bio_details[4]}'
            )
