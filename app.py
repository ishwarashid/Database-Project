from flask import Flask, render_template, request, session, Response, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv


UPLOAD_FOLDER = os.path.join(os.path.curdir, 'static', 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:ishwado@localhost/db_project"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

load_dotenv()

app.secret_key = os.getenv('SECRET_KEY')

admin_username = os.getenv('ADMIN_USERNAME')
admin_email = os.getenv('ADMIN_EMAIL')
admin_password = os.getenv('ADMIN_PASSWORD')

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    isAdmin = db.Column(db.Boolean, default=False)

class Images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey(Users.id), nullable=False)
    image_url = db.Column(db.String, nullable=False)

with app.app_context():
    db.create_all()
    try:
        result = db.session.execute(db.select(Users).filter_by(username=admin_username, email=admin_email, password=admin_password))
        user = result.scalar_one()
    except:    
        user = Users(id=1, username=admin_username, email=admin_email, password=admin_password, isAdmin=True)
        db.session.add(user)
        db.session.commit()


@app.route("/")
def home():
    if('user' in session and session['user'] != None):
        result = db.session.execute(db.select(Images))
        images = result.scalars().all()
        return render_template("main.html", user=session, images=images)
        
    return render_template("sign_up_and_signin.html")

@app.route("/signup", methods=['GET', 'POST'])
def signup_view():
    if('user' in session and session['user'] != None):
        return redirect('/')

    if(request.method == "POST"):
        name = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        id = db.session.execute(db.select(Users).order_by(Users.id)).all()
        max_id = 0
        for id in id:
            max_id = max(id.Users.id, max_id)
        user = Users(id=max_id+1 ,username=name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
    return render_template("sign_up_and_signin.html")

@app.route("/signin", methods=['GET', 'POST'])
def signin_view():
    if('user' in session and session['user'] != None):
        return redirect('/')

    if(request.method == "POST"):
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            result = db.session.execute(db.select(Users).filter_by(email=email, password=password))
            user = result.scalar_one()
        except:
            return render_template("sign_up_and_signin.html", status_code=404)
        
        if(user.email == email and user.password == password):
            session['user'] = user.username
            session['userId'] = user.id
            session['isAdmin'] = user.isAdmin
            return redirect('/')

    return render_template("sign_up_and_signin.html")


@app.route("/logout", methods=['GET'])
def logout_view():
    if('user' in session):
        session['user'] = None
        return redirect('/')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'user' in session and session['user'] != None and session['isAdmin'] == True:
        if request.method == 'POST':
            if 'wallpaper' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['wallpaper']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                
                id = db.session.execute(db.select(Images).order_by(Images.id)).all()
                max_id = 0

                for id in id:
                    max_id = max(id.Images.id, max_id)

                image = Images(id=max_id+1, user_id=session['userId'], image_url=os.path.join(app.config['UPLOAD_FOLDER'], filename))
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], f"{filename[:-4]}_{image.id}.{filename[-3:]}"))
                db.session.add(image)
                db.session.commit()
                return redirect(request.url)
    return redirect('/')

@app.route('/delete/<int:pk>', methods=['GET', "POST"])
def delete_file(pk):
    if 'user' in session and session['user'] != None and session['isAdmin'] == True:
        try:
            result = db.session.execute(db.select(Images).filter_by(id=pk))
            image = result.scalar_one()
            os.remove(f"{image.image_url[:-4]}_{image.id}.{image.image_url[-3:]}")
            db.session.delete(image)
            db.session.commit()
        except:
            pass
    return redirect('/')