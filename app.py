from flask import Flask, flash, url_for, render_template, abort, session, request, redirect
from markupsafe import escape
from flask_bcrypt import Bcrypt
from pymongo import MongoClient

from scrappers import all_scrappers

app = Flask(__name__)
app.secret_key = 'SOMETHING_VERY_SECRET'
# put your mongodb connexion string
client = MongoClient(r"mongodb+srv://[username]:[password]@cluster0-lggkw.mongodb.net/users?authSource=admin&replicaSet=Cluster0-shard-0&w=majority&readPreference=primary&appname=MongoDB%20Compass&retryWrites=true&ssl=true")
sample_scrapping_app = client.sample_scrapping_app
users = sample_scrapping_app.users

bcrypt = Bcrypt(app)


def requires_auth(func):
    def aux_function(*args, **kwargs):
        if 'user_name' in session:
            return func(*args, **kwargs)
        else:
            abort(401)
    return aux_function


@app.route('/')
def index():
    if 'user_name' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/sign-in', methods=['GET', 'POST'])
def signin():
    if 'user_name' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form["Email"]
        password = request.form["password"]
        # password = bcrypt.generate_password_hash(password)

        if(email and password):
            is_existing = users.find_one({"email": email})
            if bool(is_existing):
                pw_hash = is_existing["password"]
                user_name = is_existing["user_name"]
                if(bcrypt.check_password_hash(pw_hash, password)):  # returns True
                    session['user_name'] = user_name
                    session['email'] = email
                    return redirect(url_for('dashboard'))
                else:
                    flash('Email/Password missmatch')
                    return redirect(url_for('signin'))
            else:
                flash('Email non-existing')
                return redirect(url_for('signin'))
        else:
            flash('Email/Password missing')
            return redirect(url_for('singin'))
    return render_template('sign-in/index.html', isSignIn=True)


@app.route('/sign-up', methods=['GET', 'POST'])
def signup():
    if 'user_name' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        print(request.form)
        email = request.form["Email"]
        user_name = request.form["user_name"]
        password = request.form["password"]
        password = bcrypt.generate_password_hash(password)

        if(email and user_name and password):
            is_existing = bool(users.find_one({"email": email}))
            if is_existing:
                flash('Email already in use! Sign-in instead')
                return redirect(url_for('signin'))
            else:
                users.insert_one({
                    "email": email,
                    "user_name": user_name,
                    "password": password,
                })
                session['user_name'] = user_name
                session['email'] = email
                return redirect(url_for('dashboard'))
        else:
            flash('Email/Password missmatch')
            return redirect(url_for('signup'))

    return render_template('sign-in/index.html', isSignIn=False)


@app.route('/sign-out')
def signout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    if 'user_name' not in session:
        abort(401)
    all_regions_data = []
    for reg in all_scrappers.keys():
        all_regions_data.append({
            "region": reg,
            "title": all_scrappers[reg]["title"],
            "description": all_scrappers[reg]["description"]
        })
    return render_template('dashboard/index.html', regions=all_regions_data)


# MODIFY THIS !
@app.route('/scrap/<scrapped_region>')
def scrap(scrapped_region="sa"):
    scrap_start = request.args.get('scrap_start')
    scrap_end = request.args.get('scrap_end')

    scrapped_region_details = all_scrappers[scrapped_region]

    scrap_function = scrapped_region_details["scrap_function"]
    
    scrap_database = scrapped_region_details["scrap_database"]

    scrap_collection = scrapped_region_details["scrap_collection"]
    scrap_collection = scrap_database[scrap_collection]

    scrap_document = scrapped_region_details["scrap_document"]
    scrap_document = scrap_collection[scrap_document]

    scrap_result = scrap_function(scrap_start=scrap_start, scrap_end=scrap_end)

    scrap_result_data = scrap_result["data"]

    # print(scrap_result)
    scrap_document.insert_many(scrap_result_data)

    return "scrap_result: \n"+str(scrap_result)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(401)
def page_not_found(error):
    return render_template('401.html'), 404


@app.errorhandler(Exception)
def handle_500(e):
    original = getattr(e, "original_exception", None)
    app.logger.error('An error occurred', e)
    # wrapped unhandled error
    return render_template("500.html"), 500

