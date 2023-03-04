from flask import Flask, request, render_template
from .backend import Backend

def make_endpoints(app):

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        # TODO(Checkpoint Requirement 2 of 3): Change this to use render_template
        # to render main.html on the home page.
        return render_template("main.html")

    # TODO(Project 1): Implement additional routes according to the project requirements.
    
    @app.route("/about")    
    def about():
        b = Backend("contentwiki")
        b_pic = b.get_image('bethany')
        g_pic = b.get_image("gabriel")
        # r_pic = b.get_image("")
        return render_template("about.html", b_pic = b_pic, g_pic = g_pic)
    
    @app.route("/upload", methods=['GET', 'POST'])
    def upload_file():
        allowed_ext = {'txt', 'pdf', 'png', 'jpg', 'jpeg'}
        if request.method == 'POST':
            if 'file' not in request.files:
                return "File was not uploaded correctly. Please try again."
            file = request.files['file']
            if file.filename == "":
                return "Please upload a file"
            elif file and file.filename.split('.')[1] in allowed_ext:
                b = Backend("contentwiki")
                f = b.upload(request.form.get("filename"), file)
                # return redirect(url_for('download_file', name=filename))
        return '''
        <!doctype html>
        <title>Upload</title>
        <h3> Upload a doc to the wiki! </h3>
        <form method=post enctype=multipart/form-data>
            <input type='text' name='filename' placeholder="wikiname">
            <input type='file' name='file'> 
            <input type='submit' value='Upload'>
        </form>
        '''
    @app.route('/login', methods=['POST','GET'])
    def sign_in():
        if request.method == "POST":
            username = request.form['name']
            password = request.form['psw']
            b = Backend('userspasswords')
            info = b.sign_in(username, password)

            if info == 'Invalid User' or info == 'Invalid Password':
                return render_template('login.html', info=info)

            else:
                return render_template('main.html', info=info)
        return render_template('login.html')

    @app.route('/signup', methods=['POST','GET'])
    def sign_up():
        if request.method == "POST":
            username = request.form['name']
            password = request.form['psw']
            b = Backend('userspasswords')
            b.sign_up(username, password)
        return render_template('signup.html')        