from flask import Flask, request, render_template, Response, session, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from main import checking, checking_outside, generate_frames,pts,fun_imgG, fun_imgGray, contour, retrytoggle

app = Flask(__name__)
app.secret_key = "skdjgljheroiu@#$@3533@#$4eg3#"

# Replace 'username', 'password', and 'your_cluster_url' with your actual credentials and cluster URL
username = 'Evil'
password = '123'
cluster_url = 'cluster0.n69njhi.mongodb.net'

# Create the connection URI
connection_uri = f"mongodb+srv://{username}:{password}@{cluster_url}/?retryWrites=true&w=majority"

# Connect to the MongoDB cluster
client = MongoClient(connection_uri)

# Replace 'your_database_name' with the actual name of your database
db = client['Viz']

@app.route('/create_user', methods=['POST'])
def create_user():

    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")
    hashed_password = generate_password_hash(password)
    user = {"username": username, "password": hashed_password,"email" : email, "levels_passed": {"0":[5]}}

    try:
        db.users.insert_one(user)
        flash('User created successfully! Please log in.', 'success')
        return render_template("Login.html")
    except Exception as e:
        print(f"Error inserting user into database: {e}")
        flash('Error creating user.', 'danger')
        return redirect(url_for('register'))

def find_user(username):
    if db is None:
        print("Database connection failed.")
        return None

    user = db.users.find_one({"username": username})
    return user

def check_user_password(username, password):
    user = find_user(username)
    if user and check_password_hash(user['password'], password):
        return True
    return False

def update_user_level(username, section, level):
    try:
        # Ensure the section exists, and if not, create it with an empty list only if it doesn't exist
        db.users.update_one(
            {"username": username, f"levels_passed.{section}": {"$exists": False}},
            {"$set": {f"levels_passed.{section}": []}}
        )
        
        # Add the level to the list for the section in the levels_passed dictionary
        db.users.update_one(
            {"username": username},
            {"$addToSet": {f"levels_passed.{section}": int(level)}}
        )
        return True
    except Exception as e:
        print(f"Error updating user level: {e}")
        return False

@app.route('/')
def index():
    return render_template("Login.html")


@app.route('/study')
def study():
    return render_template("Study.html")

@app.route('/contact')
def contact():
    return render_template("Contact.html")

@app.route('/about')
def about():
    return render_template("About.html")



@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        print("Recieved",username,password)

        if check_user_password(username, password):
            session['user'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            print("NOOOOOO")
    return render_template('Login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('Home.html')
    else:
        flash('You need to login first', 'danger')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out', 'success')
    return render_template("Login.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        return create_user()
    return render_template('register.html')


@app.route('/dashboard/levels')
def levels():
    return render_template('Levels.html')


@app.route('/CapturingPage/<level>')
def CapturingPage(level):
    if 'user' not in session:
        flash('You need to log in first', 'danger')
        return redirect(url_for('login'))

    username = session['user']
    user = find_user(username)
    
    section = level[0]
    current_level = int(level[-1])
    print("worked")
    print(user)
    # Check if the previous level has been completed
    if section in user["levels_passed"] and current_level - 1 in user['levels_passed'].get(section, []):
        print("done")
        return render_template("Capturing.html", levels=level)
    else:
        print("OOPS!!")
        flash('You need to complete the previous level before accessing this one.', 'danger')
        return redirect(url_for('levels'))


@app.route('/test/<level>')
def test(level):
    if 'user' not in session:
        flash('You need to log in first', 'danger')
        return redirect(url_for('login'))

    username = session['user']
    user = find_user(username)

    section = level[0]
    current_level = int(level[-1])

    # Check if the previous level has been completed
    if section in user["levels_passed"] and current_level - 1 in user['levels_passed'].get(section, []):
        print("done")
        return render_template("testv.html",levels=level)
        # (Add your test handling code here)  
        pass
    else:
        flash('You need to complete the previous level before accessing this one.', 'danger')
        return redirect(url_for('levels'))
@app.route('/retry', methods=['POST'])
def retry():
    print("hello")
    retrytoggle()

@app.route('/test/<levels>')
def rtest(levels):
    render_template("Test.html",levels=levels)
# OpenCV and HandDetector functions

@app.route('/video/<picture>')
def video(picture):
    return Response(generate_frames(picture), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/submit_check/<levels>', methods=['POST'])
def submit_check(levels):
    contours=contour()
    imgG=fun_imgG()
    imgGray=fun_imgGray()
    coverage = checking(imgG, contours[1], imgGray)
    coverage_Outside = checking_outside(imgG, contours[1], imgGray)
    cover = coverage - coverage_Outside
    section = levels[0]
    level = levels[-1]
    username = session['user']
    if cover > 4.0:
        result = "Passed"
        update_success = update_user_level(username,section,level)
        if update_success:
            flash(f'Level {levels} passed and updated!', 'success')
            print("Worked")
        else:
            flash(f'Level {levels} passed but could not update in database.', 'danger')
    else:
        result = "not completed"
    return render_template('Result.html', coverage_percentage=cover, result=result)


if __name__ == "__main__":
    app.run(debug=True)