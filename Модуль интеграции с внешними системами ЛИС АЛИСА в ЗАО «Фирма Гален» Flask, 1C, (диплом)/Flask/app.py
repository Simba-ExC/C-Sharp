import os
from flask import Flask, render_template, url_for, request, flash, session, redirect, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

# Конфигурция
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://wklimsufivrqke:7e7474d7c022d70a411b0d63e355001ee3db24b5efaf41fb257c3fbdc93067d5@ec2-34-247-172-149.eu-west-1.compute.amazonaws.com:5432/d64g6vrvf7ohk8'

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'Galen2022!'
db = SQLAlchemy(app)
manager = LoginManager(app)


# Обратная связь
class Feedback(db.Model):
    id_feedback = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String(300), nullable=False)
    Date_feedback = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name, email, phone, message):
        self.name = name
        self.email = email
        self.phone = phone
        self.message = message


# Запись ко врачу
class patient_record (db.Model):
    id_record = db.Column(db.Integer, primary_key=True)
    polis = db.Column(db.String)
    name_doc = db.Column(db.String)
    name_patient = db.Column(db.String)
    message = db.Column(db.String)
    Date_priem = db.Column(db.DateTime)
    Date_feedback = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, polis, name_doc, name_patient, message, Date_priem):
        self.polis = polis
        self.name_doc = name_doc
        self.name_patient = name_patient
        self.message = message
        self.Date_priem = Date_priem



# Профиль
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(30), nullable=False)
    Fam = db.Column(db.String(30), nullable=False)
    birthdayDate = db.Column(db.DateTime, nullable=False)
    POL = db.Column(db.String(2), nullable=False)
    emailAddress = db.Column(db.String(100), nullable=False)
    phoneNumber = db.Column(db.String(15), nullable=False)
    POLIS = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    Date_reg = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, Name, Fam, birthdayDate, POL, emailAddress, phoneNumber, POLIS, password):
        self.Name = Name
        self.Fam = Fam
        self.birthdayDate = birthdayDate
        self.POL = POL
        self.emailAddress = emailAddress
        self.phoneNumber = phoneNumber
        self.POLIS = POLIS
        self.password = password


class results(db.Model):
    sample_id = db.Column(db.Integer, primary_key=True)  # надо
    fam = db.Column(db.String(50))  # надо
    im = db.Column(db.String(50))  # надо
    polis = db.Column(db.String(20))  # надо
    order_date = db.Column(db.DateTime)  # надо
    tst_abbr = db.Column(db.String(20))
    tst_name = db.Column(db.String(100))  # надо
    res = db.Column(db.String(50))  # надо
    rem = db.Column(db.String(80))
    unit_name = db.Column(db.String(30))  # надо
    ref = db.Column(db.String(4000))  # надо
    norma = db.Column(db.String(50))  # надо
    tst_date = db.Column(db.DateTime)  # надо
    analyzer = db.Column(db.String(20))  # надо
    diagn = db.Column(db.String(40))  # надо
    dep_name = db.Column(db.String(100))  # надо
    biomatherial = db.Column(db.String(50))  # надо
    otdel = db.Column(db.String(50))  # надо
    wdate = db.Column(db.DateTime)  # надо
    doctors = db.Column(db.String(100))
    strahcompany = db.Column(db.String(200))


@manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


# Форма авторизации
@app.route('/', methods=["POST", "GET"])
@app.route('/index', methods=["POST", "GET"])
@app.route('/login', methods=["POST", "GET"])
def index():
    if request.method == "POST":
        POLIS = request.form.get('POLIS')
        password = request.form.get('password')
        if POLIS and password:
            user = Users.query.filter_by(POLIS=POLIS).first()

            if user and check_password_hash(user.password, password):
                login_user(user)
                manager.login_view = user.POLIS
                return redirect(url_for('main'))
            else:
                flash("ошибка в связке логин/пароль", "error")
        else:
            flash("Проверьте правильность заполнения полей", "error")
    return render_template("index.html")


@app.route('/logout', methods=["POST", "GET"])
@login_required
def logout():
    print("Вы разлогинились")
    logout_user()
    flash("Вы разлогинились", "success")
    return redirect(url_for('index'))


@app.route('/Profile', methods=["POST", "GET"])
@login_required
def Profile():
    profile = Users.query.filter_by(POLIS=manager.login_view).all()
    return render_template("Profile.html", profile=profile)


@app.route('/main')
@login_required
def main():
    snils = manager.login_view
    #print(snils)
    profile = Users.query.filter_by(POLIS=manager.login_view).all()
    #samples = results.query.filter_by(polis=snils).group_by(results.sample_id).order_by(results.order_date.desc()).all()
    samples = results.query.filter_by(polis=snils).order_by(results.order_date.desc()).all()
    #print(samples)
    return render_template("main.html", samples=samples, profile=profile)


@app.route('/MyRecord')
@login_required
def MyRecord():
    snils = manager.login_view
    profile = Users.query.filter_by(POLIS=manager.login_view).all()
    records = patient_record.query.filter_by(polis=snils).order_by(patient_record.Date_priem.desc()).all()
    return render_template("MyRecord.html", records=records, profile=profile)


@app.route('/sample/<int:sample_id>')
@login_required
def sample(sample_id):
    probe = results.query.filter_by(sample_id=sample_id).all()
    #print(probe)
    return render_template("sample.html", probe=probe)


# Форма регистрации
@app.route('/registration', methods=["POST", "GET"])
def registration():
    if request.method == "POST":
        if len(Users.query.filter(Users.POLIS == (request.form['POLIS'])).all()) < 1:
            if len(Users.query.filter(Users.POLIS == (request.form['emailAddress'])).all()) < 1:
                if len(Users.query.filter(Users.POLIS == (request.form['phoneNumber'])).all()) < 1:
                    if request.form['password'] == request.form['Rpassword']:
                        try:
                            hash = generate_password_hash((request.form['password']))
                            Name = request.form["Name"]
                            Fam = request.form["Fam"]
                            birthdayDate = request.form["birthdayDate"]
                            POL = request.form["POL"]
                            emailAddress = request.form["emailAddress"]
                            phoneNumber = request.form["phoneNumber"]
                            POLIS = request.form["POLIS"]
                            entry_Users = Users(Name=Name, Fam=Fam, birthdayDate=birthdayDate, POL=POL,
                                                emailAddress=emailAddress,
                                                phoneNumber=phoneNumber, POLIS=POLIS, password=hash)
                            db.session.add(entry_Users)
                            db.session.commit()
                            flash("Аккаунт создан", "success")
                            return redirect(url_for('index'))
                        except:
                            db.session.rollback()
                            flash("Ошибка создания аккаунта, обратитесь в поддержку", "error")
                    else:
                        flash("Пароли не совпадают", "error")
                else:
                    flash("Такой Адрес электронной почты уже зарегистрирован", "error")
            else:
                flash("Такой номер телефона уже зарегистрирован", "error")
        else:
            flash("Такой полис уже зарегистрирован", "error")
    return render_template("registration.html")


# Форма обратной связи
@app.route('/contact', methods=["POST", "GET"])
def contact():
    if request.method == "POST":
        try:
            name = request.form["name"]
            email = request.form["email"]
            phone = request.form["phone"]
            message = request.form["message"]
            entry_feedback = Feedback(name=name, email=email, phone=phone, message=message)

            db.session.add(entry_feedback)
            db.session.commit()
        except:
            db.session.rollback()
            print("Ошибка добавления в БД")
    return render_template("contact.html")


# Форма записи на прием
@app.route('/record', methods=["POST", "GET"])
def record():
    if request.method == "POST":
        try:
            polis = manager.login_view
            name_doc = request.form["name_doc"]
            name_patient = request.form["name_patient"]
            message = request.form["message"]
            Date_priem = request.form["Date_priem"]
            print (polis)
            print(name_doc)
            print(name_patient)
            print(message)
            print(Date_priem)

            entry_patient_record = patient_record(polis=polis, name_doc=name_doc, name_patient=name_patient, message=message, Date_priem=Date_priem)

            db.session.add(entry_patient_record)
            db.session.commit()
            return redirect(url_for('MyRecord'))
        except:
            db.session.rollback()
            print("Ошибка добавления в БД")
    return render_template("record.html")


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('index'))
    return response


# Если ошибки
@app.errorhandler(404)
def pageNotFount(error):
    return render_template('page404.html', )


if __name__ == '__main__':
    # db.create_all()
    app.run(debug=True)
