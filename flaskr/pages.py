from flask import Flask, request, render_template, session, redirect, url_for
from .backend import Backend
import re
import requests


def make_endpoints(app):

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        games = Backend("contentwiki").get_image(
            "games")  # get background image
        return render_template(
            "main.html", games=games)  # render main page with background image

    # TODO(Project 1): Implement additional routes according to the project requirements.

    @app.route("/about")
    def about():
        # gets background image along with about images for the three authors, then returns it to about page on render
        games = Backend("contentwiki").get_image("games")
        b = Backend("contentwiki")
        b_pic = b.get_image('bethany')
        g_pic = b.get_image("gabriel")
        r_pic = b.get_image('rakshith')
        return render_template("about.html",
                               b_pic=b_pic,
                               g_pic=g_pic,
                               r_pic=r_pic,
                               games=games)

    @app.route("/upload", methods=['GET', 'POST'])
    def upload_file():
        """ Retrieve the file and wikipage name the user supplied in the form. Ensures the file was successfully retrieved and of valid
        type, then uses the wikipage name (representing the game's title) to search for valid genres associated with the game. For each
        valid genre, adds the genre along with the wikipage name to the Genres bucket, then adds the game to the contentwiki Bucket
        Args: None
        Returns:
            - "File was not uploaded correctly. Please try again." if no file is found in request/request made incorrectly
            - "Please upload a file." if no file found in request + wiki page name was supplied
            - "Uploaded successfully." if file and wiki page name was uploaded to the cloud successfully.

        """
        games = Backend("contentwiki").get_image("games")
        allowed_ext = {'txt', 'png', 'jpg', 'jpeg'}
        message = [
            "File was not uploaded correctly. Please try again.",
            "Please upload a file.", "File type not supported.",
            "Uploaded successfully.",
            "Your file was uploaded successfully but it has no genres attached to it."
        ]

        if request.method == 'POST':
            if 'file' not in request.files:
                return render_template("upload.html",
                                       message=message[0],
                                       games=games)
            file = request.files['file']

            if file.filename == "":
                return render_template("upload.html",
                                       message=message[1],
                                       games=games)
            elif file.filename.split('.')[1] not in allowed_ext:
                return render_template("upload.html",
                                       message=message[2],
                                       games=games)

            elif file:
                game_title = request.form.get("filename")
                b = Backend("contentwiki")
                genres = b.get_genre(game_title)
                g = Backend("game-genres")
                if type(genres) is list:
                    for genre in genres:
                        g.upload_genre(genre, game_title)
                else:
                    return render_template("altupload.html",
                                           message=message[4],
                                           games=games)

                g.upload_genre("*All*", game_title)
                b.upload(game_title, file)
                return render_template("upload.html",
                                       message=message[3],
                                       games=games)
                # genre has either returned "Could not find genres for title." (title is correct, however no genres on database)
                # or "Title not found." (title not in database)
                # add functionality to communicate this to the user via popup, and allow them to either continue the upload
                # as-is (no genre) or to edit the title and upload
        return render_template("upload.html", games=games)

    @app.route("/altupload", methods=['GET', 'POST'])
    def altupload():
        games = Backend("contentwiki").get_image("games")
        allowed_ext = {'txt', 'png', 'jpg', 'jpeg'}
        message = [
            "File was not uploaded correctly. Please try again.",
            "Please upload a file.", "File type not supported.",
            "Uploaded successfully."
        ]

        if request.method == 'POST':
            if 'file' not in request.files:
                return render_template("altupload.html",
                                       message=message[0],
                                       games=games)
            file = request.files['file']

            if file.filename == "":
                return render_template("altupload.html",
                                       message=message[1],
                                       games=games)

            elif file.filename.split('.')[1] not in allowed_ext:
                return render_template("altupload.html",
                                       message=message[2],
                                       games=games)

            elif file:
                game_title = request.form.get("filename")
                b = Backend("contentwiki")
                genres = b.get_genre(game_title)
                g = Backend("game-genres")
                if type(genres) is list:
                    for genre in genres:
                        g.upload_genre(genre, game_title)
                else:
                    g.upload_genre("*All*", game_title)
                    b.upload(game_title, file)
                    return render_template("upload.html",
                                           message=message[3],
                                           games=games)

                g.upload_genre("*All*", game_title)
                b.upload(game_title, file)
                return render_template("upload.html",
                                       message=message[3],
                                       games=games)
                # genre has either returned "Could not find genres for title." (title is correct, however no genres on database)
                # or "Title not found." (title not in database)
                # add functionality to communicate this to the user via popup, and allow them to either continue the upload
                # as-is (no genre) or to edit the title and upload
        return render_template("altupload.html", games=games)

    @app.route('/login', methods=['POST', 'GET'])
    def sign_in():
        games = Backend("contentwiki").get_image("games")
        if request.method == "POST":
            username = request.form['name']
            password = request.form['psw']
            b = Backend(
                'userspasswords'
            )  #passes the unsername and password entered to the login function in Backend class
            info = b.sign_in(username, password)

            if info == 'Invalid User' or info == 'Invalid Password':  #if the passward or username is invalid it renders back to the login page and displays the error message
                return render_template('login.html', info=info, games=games)

            else:
                session[
                    'username'] = username  #adds the username to the session
                return redirect('/')
        return render_template('login.html', games=games)

    @app.route('/signup', methods=['POST', 'GET'])
    def sign_up():
        games = Backend("contentwiki").get_image("games")
        if request.method == "POST":
            username = request.form['name']
            password = request.form['psw']
            email = request.form['email_add']
            b = Backend('userspasswords')

            info = b.sign_up(
                username, password, email
            )  #passes the unsername and password entered to the signup function in Backend class

            if info == 'Username already exsists':
                return render_template('signup.html', info=info, games=games)
            else:
                session[
                    'username'] = username  #adds the username to the session
                return redirect('/')
        return render_template('signup.html', games=games)

    @app.route('/pages', methods=['GET', 'POST'])
    def pages():
        """ Get a list of all the genres to display via dropdown on the page upon render. If the user selects a genre, retrieve selected
        genre and find the games that match the genre from the Genre bucket, then return them hyperlinked (when clicked -> page)  
        Args: None
        Returns:
            - GET: Redirect to Pages page with a dropdown of all possible genres and a list of all game titles
            - POST: Redirect to Pages page with a dropdown of all possible genres and a list of all game titles matching the selected
            genre
        """
        #
        backend = Backend("game-genres")
        genres = backend.get_all_page_names()
        if request.method == 'GET':
            genre = "*All*"
        if request.method == 'POST':
            genre = request.form.get('genre')
        pages = backend.bucket.blob(genre).download_as_string().decode('utf-8')
        games = Backend("contentwiki").get_image("games")
        return render_template('pages.html',
                               section=genre,
                               pages=pages,
                               genres=genres,
                               games=games)

    @app.route('/pages/<name>')
    def show_page(name):
        """ Call the backend with the page's name to retrieve its contents, then decoded it via UTF-8 and render the page.   
        Args:
            name: String representing the name of the desired page
        Returns:
            Redirect to page with decoded page content
        """
        backend = Backend("contentwiki")
        content = backend.get_wiki_page(name)
        games = Backend("contentwiki").get_image("games")
        if content is not None:
            decoded_content = content.decode('utf-8')
            return render_template('pages.html',
                                   page_title=name,
                                   page_content=decoded_content,
                                   games=games)
        else:
            return f'Page {name} not found'

    @app.route("/logout")
    def logout():
        # when user logs out, set session username to None, then redirect to home page
        session['username'] = None
        return redirect('/')

    @app.route('/profile', methods=['POST', 'GET'])
    def profile():
        """
        Call the backend to retrieve the user's profile details and the path to their profile picture.
        Render the profile page with the user's details and profile picture.

        Returns:
            Rendered template of the user's profile page with the decoded details and picture.
        """
        user_name = session['username']
        games = Backend("contentwiki").get_image("games")
        b1 = Backend('userspasswords')
        b2 = Backend('contentwiki')
        profile_details = b1.profile(user_name)
        profile_pic = b2.get_image(profile_details[-1])
        return render_template('profile.html',
                               username=user_name,
                               email=profile_details[1],
                               bio=profile_details[2],
                               favorite_games=profile_details[3],
                               favorite_genres=profile_details[4],
                               favorite_developers=profile_details[-2],
                               profile_pic_path=profile_pic,
                               games=games)

    @app.route('/editprofile', methods=['GET', 'POST'])
    def edit_profile():
        """
        Call the backend to get image 'games' from 'contentwiki' and to retrieve profile information from 'bio_and_gamepreferences'. 
        If a POST request is received, update the user's profile information and redirect to the profile page.
        Args:
            None
        Returns:
            Redirect to /profile template with updated profile information.
        """
        games = Backend("contentwiki").get_image("games")
        b = Backend('userspasswords')
        user_name = session['username']
        if request.method == 'POST':
            email = request.form.get('email')
            bio = request.form.get('bio')
            favorite_games = request.form.get('favorite_games')
            favorite_genres = request.form.get('favorite_genres')
            favorite_developers = request.form.get('favorite_developers')
            # process the form data and save the changes to the database
            profile_details = []
            profile_details.append(email)
            profile_details.append(bio)
            profile_details.append(favorite_games)
            profile_details.append(favorite_genres)
            profile_details.append(favorite_developers)

            b.editprofile(user_name, profile_details)
            return redirect('/profile')

        return render_template('editprofile.html',
                               email='',
                               bio='',
                               favorite_games='',
                               favorite_genres='',
                               favorite_developers='',
                               games=games)

    @app.route('/editprofilepic', methods=['GET', 'POST'])
    def avatar_selection():
        """
        Call the backend to get image 'games' from 'contentwiki' and to retrieve the user's profile information and avatar
        selection from 'userspasswords' and 'contentwiki' respectively. If a POST request is received, update the user's 
        avatar selection and redirect to the profile page.
        Args:
            None
        Returns:
            Render the editprofilepic.html template with images for avatar selection and image 'games'.
        """
        games = Backend("contentwiki").get_image("games")
        b1 = Backend('userspasswords')
        user_name = session['username']
        b2 = Backend('contentwiki')

        avatar1 = b2.get_image('avatar1')
        avatar2 = b2.get_image('avatar2')
        avatar3 = b2.get_image('avatar3')
        avatar4 = b2.get_image('avatar4')
        avatar5 = b2.get_image('avatar5')
        avatar6 = b2.get_image('avatar6')
        avatar7 = b2.get_image('avatar7')
        avatar8 = b2.get_image('avatar8')
        avatar9 = b2.get_image('avatar9')
        avatar10 = b2.get_image('avatar10')

        if request.method == "POST":
            if request.form.get('avatar1', None) == 'on':
                selected_avatar = 'avatar1'
                b1.editprofilepic(user_name, selected_avatar)

            if request.form.get('avatar2', None) == 'on':
                selected_avatar = 'avatar2'
                b1.editprofilepic(user_name, selected_avatar)

            if request.form.get('avatar3', None) == 'on':
                selected_avatar = 'avatar3'
                b1.editprofilepic(user_name, selected_avatar)

            if request.form.get('avatar4', None) == 'on':
                selected_avatar = 'avatar4'
                b1.editprofilepic(user_name, selected_avatar)

            if request.form.get('avatar5', None) == 'on':
                selected_avatar = 'avatar5'
                b1.editprofilepic(user_name, selected_avatar)

            if request.form.get('avatar6', None) == 'on':
                selected_avatar = 'avatar6'
                b1.editprofilepic(user_name, selected_avatar)

            if request.form.get('avatar7', None) == 'on':
                selected_avatar = 'avatar7'
                b1.editprofilepic(user_name, selected_avatar)

            if request.form.get('avatar8', None) == 'on':
                selected_avatar = 'avatar8'
                b1.editprofilepic(user_name, selected_avatar)

            if request.form.get('avatar9', None) == 'on':
                selected_avatar = 'avatar9'
                b1.editprofilepic(user_name, selected_avatar)

            if request.form.get('avatar10', None) == 'on':
                selected_avatar = 'avatar10'
                b1.editprofilepic(user_name, selected_avatar)
            return redirect('/profile')

        return render_template('editprofilepic.html',
                               Avatar1=avatar1,
                               Avatar2=avatar2,
                               Avatar3=avatar3,
                               Avatar4=avatar4,
                               Avatar5=avatar5,
                               Avatar6=avatar6,
                               Avatar7=avatar7,
                               Avatar8=avatar8,
                               Avatar9=avatar9,
                               Avatar10=avatar10,
                               games=games)
