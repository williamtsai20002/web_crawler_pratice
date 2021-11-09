from flask import Flask, url_for, request, redirect
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
import mysql.connector
import os


mydb = mysql.connector.connect(
    host = "192.168.223.144",
    user = "root",
    passwd = "root",
    database = "hw_database", 
    auth_plugin = 'mysql_native_password'
)
mycursor = mydb.cursor()

app = Flask(__name__)
app.secret_key = 'agsdasfasdgasdfasdfasdf'  
login_manager = LoginManager(app)  

class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
    sql = "SELECT id, username FROM user WHERE username = %s"
    args = (username, )
    mycursor.execute(sql, args)
    data = mycursor.fetchall()
    
    if len(data) > 0:
        user_id = data[0][0]
        username = data[0][1]
        user = User()
        user.id = user_id
        user.user_name = username
        return user
    else:
        return

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return '''
                    <div> Register </div>
                    <form action='register' method='POST'>
                    <input type='text' name='username' id='username' placeholder='username'/>
                    <input type='password' name='password' id='password' placeholder='password'/>
                    <input type='submit' name='submit'/>
                    </form>
                '''
    
    username = request.form['username']
    password = request.form['password']
    
    sql = "SELECT username FROM user WHERE username = %s"
    args = (username, )
    mycursor.execute(sql, args)
    data = mycursor.fetchall()

    if len(data) > 0:
        return "Username already exist !!!"
    else:
        sql = "INSERT INTO user (username, password) VALUES (%s, %s)"
        args = (username, password)
        mycursor.execute(sql, args)
        mydb.commit()

        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return '''
                    <div> Login </div>
                    <form action='login' method='POST'>
                    <input type='text' name='username' id='username' placeholder='username'/>
                    <input type='password' name='password' id='password' placeholder='password'/>
                    <input type='submit' name='submit'/>
                    </form>
                '''

    username = request.form['username']
    # check password
    sql = "SELECT password FROM user WHERE username = %s"
    args = (username, )
    mycursor.execute(sql, args)
    data = mycursor.fetchall()
    
    if len(data) > 0:
        correct_password = data[0][0]
        if request.form['password'] == correct_password:
            user = User()
            user.id = username
            login_user(user)
            return redirect(url_for('index'))
    
    return 'Login Failed'

@app.route('/index')
@login_required
def index():
    if current_user.is_active:
        create_class_html =  '''
                                <div> Create Class </div>
                                <form action='create_class' method='POST'>
                                <input type='text' name='class_name' id='class_name' placeholder='class_name'/>
                                <input type='submit' name='submit'/>
                                </form>
                                <div></div>
                            '''
        
        sql = "SELECT * FROM class"
        mycursor.execute(sql)
        data = mycursor.fetchall()

        tr_html_str = ""
        for ele in data:
            tr_html_str += "<tr><td>" + str(ele[1]) + "</td><td>" + str(ele[2]) + "</td><td>" + "<a href='/api/class/" + str(ele[0]) + "'>Enter</a>" + "</td></tr>"


        class_list_html = "<table><thead><tr><th> Class List </th></tr></thead><tbody>" + tr_html_str + "</tbody></table>"

        return create_class_html + class_list_html

@app.route('/create_class', methods=['POST'])
@login_required
def create_class():
    if current_user.is_active:
        user_id = current_user.id
        class_name = request.form['class_name']

        sql = "INSERT INTO class (user_id, class_name) VALUES (%s, %s)"
        args = (user_id, class_name)
        mycursor.execute(sql, args)
        mydb.commit()

        return redirect(url_for('index'))

@app.route('/api/class/<class_id>')
@login_required
def in_class(class_id):
    if current_user.is_active:
        create_group_html =  '''
                                <div> Create Group </div>
                                <form action='/create_group' method='POST'>
                                <input type='text' name='group_name' id='group_name' placeholder='group_name'/>
                                <input type='hidden' name='class_id' id='class_id' value=''' + class_id + '''>
                                <input type='submit' name='submit'/>
                                </form>
                                <div></div>
                            '''
        
        sql = "SELECT * FROM organize WHERE class_id = %s"
        args = (str(class_id), )
        mycursor.execute(sql, args)
        data = mycursor.fetchall()

        tr_html_str = ""
        for ele in data:
            tr_html_str += "<tr><td>" + str(ele[0]) + "</td><td>" + str(ele[2]) + "</td><td>" + "<a href='/api/group/" + str(ele[0]) + "'>Join</a>" + "</td></tr>"


        group_list_html = "<table><thead><tr><th> Class List </th></tr></thead><tbody>" + tr_html_str + "</tbody></table>"

        return create_group_html + group_list_html

@app.route('/create_group', methods=['POST'])
@login_required
def create_group():
    if current_user.is_active:
        class_id = request.form['class_id']
        user_id = current_user.id
        group_name = request.form['group_name']

        sql = "INSERT INTO organize (class_id, organize_name, users) VALUES (%s, %s, %s)"
        args = (int(class_id), group_name, str(user_id))
        mycursor.execute(sql, args)
        mydb.commit()

        return redirect(url_for('in_class', class_id = str(class_id)))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
    # return 'Logged out'
  
if __name__ == '__main__':  
    app.debug = True  
    app.run()
