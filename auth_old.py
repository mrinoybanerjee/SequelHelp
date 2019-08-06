from flask import Flask
from flask import Blueprint
from flask import render_template
from flask import Flask

from flask import Flask, Response, redirect, url_for, request, session, abort
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

app = Flask(__name__)

auth = Blueprint('auth', __name__, template_folder='templates')

# # config
# app.config.update(
#     DEBUG = True,
#     SECRET_KEY = 'secret_xxx'
# )

# flask-login
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


# silly user model
class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.name = "user" + str(id)
        self.password = self.name + "_secret"
        
    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)


# create some users with ids 1 to 20       
users = [User(id) for id in range(1, 21)]


# some protected url
@auth.route('/home')
@login_required
def home():
    return Response("Hello World!")

 
# somewhere to login
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']        
        if password == username + "_secret":
            id = username.split('user')[1]
            user = User(id)
            login_user(user)
            return redirect(request.args.get("next"))
        else:
            return abort(401)
    else:
        return Response('''
        <form action="" method="post">
            <p>username: <input type=text name=username>
            <p>password: <input type=password name=password>
            <p><input type=submit value=Login>
        </form>
        ''')


# somewhere to logout
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return Response('<p>Logged out</p>')


# handle login failed
@auth.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')
    
    
# callback to reload the user object        
@login_manager.user_loader
def load_user(userid):
    return User(userid)
    

@auth.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)




if __name__ == "__main__":
    auth.run()