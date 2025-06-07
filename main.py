from functools import wraps

from flask import Flask, render_template, redirect, request, flash, url_for, abort
from flask_bootstrap import Bootstrap5 # if you see an error saying there's no Bootstrap5, use 'pip install bootstrap-flask' directly in the terminal
from database import db, Cafe, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from forms import CafeForm
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
Bootstrap5(app) # this is for WTForms otherwise have the type the bootstrap code out manually

# Database set-up
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Cafes_Database.db" # create 1 database but with 2 tables - a cafe and a user database
db.init_app(app)

# Set up Flask to use Flask-Login.
# This makes the 'current_user' object available in ALL templates automatically.
login_manager = LoginManager()
login_manager.init_app(app)

# Define the admin_only function
def admin_only(function):
    @wraps(function) # see notion for a short explanation on wraps
    def wrapper(*args, **kwargs): # these *args and **kwargs is to allow the wrapper to accommodate whatever inputs that is passed through in the original function.
        print(current_user.id)
        if current_user.id == 1:
            return function(*args, **kwargs)
        else:
            abort(403)
    return wrapper

# Define logged_in function
def logged_in(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            return function(*args, **kwargs)
        else:
            abort(403)
    return wrapper

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/add", methods=["POST", "GET"])
@admin_only
def add():
    form = CafeForm()
    if form.validate_on_submit():
        print("Form submitted")
        new_cafe = form.data
        print(new_cafe)
        print(new_cafe['has_sockets'])
        for key in ['has_sockets', 'has_toilet', 'has_wifi', 'can_take_calls']:
            if new_cafe[key] is True:
                new_cafe[key] = 1
            else:
                new_cafe[key] = 0
        cafe_added = Cafe(name=new_cafe['name'], map_url=new_cafe['map_url'], img_url=new_cafe['img_url'],
                          location=new_cafe['location'], has_sockets=new_cafe['has_sockets'], has_toilet=new_cafe['has_toilet'],
                          has_wifi=new_cafe['has_wifi'], can_take_calls=new_cafe['can_take_calls'], seats=new_cafe['seats'],
                          coffee_price=new_cafe['coffee_price'])
        db.session.add(cafe_added)
        db.session.commit()
        return redirect('/view')
    return render_template("add.html", form=form)

@app.route("/view")
def view():
    all_cafes = db.session.execute(db.select(Cafe)).scalars().all() # no need to use .order_by(Cafe.name) if order of the Cafes does not matter
    return render_template("view_cafes.html", cafes=all_cafes)

@app.route("/view/<int:cafe_id>")
# @logged_in -> this is not needed as i just want to display the error message
def view_each_cafe(cafe_id):
    if not current_user.is_authenticated:
        flash("Please log in to view cafe details!")
        return redirect("/login")
    else:
        cafe_chosen = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()
        return render_template("single_cafe.html", cafe=cafe_chosen)

@app.route("/delete/<int:cafe_id>")
@admin_only
def delete(cafe_id):
    print(cafe_id)
    cafe_to_delete = db.get_or_404(Cafe, cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()
    return redirect('/view')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        user_email = request.form.to_dict()["email"]
        user_password = request.form.to_dict()["password"]
        existing_user = db.session.execute(db.select(User).where(User.email == user_email)).scalar()
        if existing_user:
            if check_password_hash(pwhash=existing_user.password, password=user_password) is True:
                login_user(existing_user)
                return redirect("/view")
            else:
                flash("The password is incorrect. Please try again.")
        else:
            flash("That email does not exist. Please register.")
            return redirect("/register")

    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")

@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        user_email = request.form.to_dict()["email"]
        user_password = request.form.to_dict()["password"]
        print(user_password)
        if db.session.execute(db.select(User).where(User.email == user_email)).scalar():
            # scalar returns just ONE value, scalars can return MULTIPLE, its a list
            flash("You've already signed up with that email, log in instead!")
            # we must also include the flash message in our template so that the message will show.
            # the 'with' keyword in jinja just creates a temporary variable, 'messages' that exists only inside that code block, and will be gone once the end of the code block is reached
            return redirect(url_for('login'))
            # instead of using url_for can also use '/login' directly
        else:
            encrypted_password = generate_password_hash(user_password, method="pbkdf2:sha256", salt_length=8)
            new_user = User(email=user_email, password=encrypted_password)
            db.session.add(new_user)
            db.session.commit()
            flash("User created! Please sign in.")
            return redirect("/login")

    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)