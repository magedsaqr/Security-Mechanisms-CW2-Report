from flask import Flask,render_template,request,flash, session,redirect,url_for
import mysql.connector
from io import BytesIO
from flask_wtf.file import FileField
from wtforms import SubmitField
from flask_wtf import FlaskForm
from flask_bcrypt import Bcrypt  # Import the Bcrypt module
from flask_bcrypt import check_password_hash
from flask import escape


app = Flask(__name__)
app.secret_key = "super secret key"
bcrypt = Bcrypt(app)



def sql_connector():
    connection = mysql.connector.connect(host = 'localhost' , user='root' , password='Magedsaqr@1' , db="ereading")
    cursor= connection.cursor()
    return connection,cursor

app = Flask(__name__)
app.secret_key="super secret key"

@app.route("/")          
def index():
    return render_template ("index.html")

@app.route('/read')
def read():
    return render_template("read.html")


@app.route('/read2')
def read2():
    return render_template("read2.html")


@app.route('/read3')
def read3():
    return render_template("read3.html")


@app.route('/read4')
def read4():
    return render_template("read4.html")


@app.route('/read5')
def read5():
    return render_template("read5.html")

@app.route('/purchase')
def purchase():
    return render_template("purchase.html")

@app.route("/schedule", methods=['GET', 'POST'])
def schedule():
    if request.method == "POST":
        BookName = request.form.get("BookName")
        Time = request.form.get("Time")
        pages = request.form.get("pages")
        connection,cursor=sql_connector()
        cursor.execute("INSERT INTO schedule (BookName,Time,pages) VALUES (%s,%s,%s)",(BookName,Time,pages))
        connection.commit()
        cursor.close()
        connection.close()
        
       
    return render_template ("schedule.html")

@app.route("/schedule_detail")
def schedule_detail():
    connection,cursor=sql_connector()
    cursor= connection.cursor()
    cursor.execute("SELECT * FROM schedule")
    data = cursor.fetchall()
    return render_template('schedule_detail.html', data=data)


@app.route("/home", methods=["GET", "POST"])
def up():

    form = UploadForm()
    if request.method == "POST":
         if form.validate_on_submit():
            file_name = form.file.data
            name, data =file_name.filename,file_name.read()
            database(name, data)
            return render_template("home.html", form=form, object = {name, data})
            

    return render_template("home.html", form=form)



class UploadForm(FlaskForm):
    file = FileField()
    submit = SubmitField("submit")


def database(name,data):
    connection,cursor=sql_connector()
    cursor.execute("INSERT INTO my_table2 (name,data) VALUES (%s,%s)",(name,data))
    connection.commit()
    cursor.close()
    connection.close()




@app.route("/book")         
def book(): 
    fetched_rows = None
    return render_template ("book.html", fetched_rows= fetched_rows)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("pass")

        connection, cursor = sql_connector()
        cursor.execute("SELECT * FROM accountsss WHERE username=%s", (username,))
        record = cursor.fetchone()
        cursor.close()

        if record and check_password_hash(record[3], password):
            session["loggedin"] = True
            session["username"] = escape(record[2])
            
            if username == "teacher":
                flash("Login Successful as Teacher", "success")
                return redirect(url_for('teacher'))
            else:
                flash("Login Successful", "success")
                return redirect(url_for('book'))
        else:
            flash("Username or password is incorrect", "warning")

    return render_template("login.html")

@app.route("/teacher")
def teacher():
    return render_template("teacher.html")


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('login'))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == 'POST':
        connection, cursor = sql_connector()
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("pass")

        # Enforce strong password policy
        if (
            len(password) < 8
            or not any(char.isupper() for char in password)
            or not any(char.islower() for char in password)
            or not any(char.isdigit() for char in password)
            or not any(char.isalnum() for char in password)
        ):
            flash("Password must meet the specified criteria (min. 8 characters:at least one upper-case letter, one lowercase letter, one digit, not all digits).", "warning")
            return redirect(request.url)

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    

        cursor.execute("SELECT * FROM accountsss WHERE username=%s", (username,))
        record = cursor.fetchone()

        if record:
            session["loggedin"] = True
            session["username"] = record[1]
            flash("Use a different username.", "warning")
        else:
            connection, cursor = sql_connector()
            cursor.execute("INSERT INTO accountsss (email, username, pass) VALUES (%s, %s, %s)", (email, username, hashed_password))
            flash("Account created successfully.", "success")
            connection.commit()
            connection.close()
            cursor.close()
            return redirect(url_for('login'))

    return render_template("signup.html")

@app.route("/forget",methods=["GET","POST"])
def forget():
    if request.method == 'POST':
        email = request.form.get("email")
        pass1 = request.form.get("pass1")
        pass2 = request.form.get("pass2")
        if len(pass1)<8:
            flash("Password must have at least 8 characters" , "warning")
            return redirect(request.url)
        
        connection,cursor=sql_connector()
        cursor.execute("SELECT * FROM accountsss WHERE email=%s",(email,))
        record=cursor.fetchone()
        
        if pass1 != pass2:
            flash("Passwords do not match","warning") 
            return redirect(request.url)

        if record:
            session["email"] = record[0]
            flash("Password changed Succesfully", "success")
            cursor.execute ("UPDATE accountsss SET pass =  %s WHERE account_id = (select account_id from (SELECT * FROM accountsss) as anyname where email = %s)",(pass1,email))
            connection.commit()
            connection.close()
            cursor.close()
            

        else:
            flash("Wrong Credentials entered" ,"warning") 
            return redirect(request.url)
            
    return render_template("forget.html")

    
if __name__ == "__main__":
    app.run(debug = True)