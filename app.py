from flask import *
from flask import jsonify
#from pusher import Pusher
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired
from flask_login import LoginManager,UserMixin,login_user,logout_user,current_user
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app=Flask(__name__)
#pusher = Pusher(
      #app_id='1569706',
      #key='561801f5083917c15947',
      #secret='c4d06517d440881f831d',
      #cluster='ap1',
      #ssl=True
    #)
login_manager=LoginManager()
login_manager.init_app(app)
SECRET_KEY= "some secret key"
app.config['SECRET_KEY']=SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///C:\\Users\\user\\OneDrive\\Documents\\Python Scripts\\hello_flask\\Project\\ToDoApp\\todo.db.'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)

@login_manager.user_loader
def load_user(user_ID):
     return User.query.get(int(user_ID))
    


class User(db.Model,UserMixin):
    id= db.Column(db.Integer,primary_key=True)
    first_name= db.Column(db.String(255))
    last_name=db.Column(db.String(255))
    email=db.Column(db.String,unique=True)
    password=db.Column(db.String(255))
    
    
    def __repr__(self):
     return f'User{self.first_name}{self.email}'
       
class RegisterForm(FlaskForm):
    first_name= StringField('First Name',validators=[DataRequired()])
    last_name= StringField('Last Name',validators=[DataRequired()])
    email=EmailField('Email',validators=[DataRequired()])
    password=PasswordField('Password',validators=[DataRequired()])
    submit=SubmitField('Register')
    
class LoginForm(FlaskForm):
    email = EmailField('Email',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    submit= SubmitField('Sign In')
    
class EditTodoForm(FlaskForm):
    task_name = StringField('Name', validators=[DataRequired()])
    due_date = DateField('Due Date', validators=[DataRequired()])
    status = SelectField('Status', choices=[('COMPLETED', 'COMPLETED'), ('NOTSTARTED', 'NOTSTARTED')])
    submit = SubmitField('Edit Task')
    

class Todo(db.Model):
    task_id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    due_date = db.Column(db.DateTime,default=datetime.now)
    status = db.Column(db.String(255))
    todo_owner = db.Column(db.Integer,db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f'Task{self.task_name}{self.due_date}'
    
@app.route('/homepage')
def home_page():
    todo_list=Todo.query.all()
    return render_template('base.html')
    
@app.route('/register', methods = ['POST','GET'])
def register():
    form = RegisterForm()
    if request.method == 'GET':
        return render_template('register.html', form=form)

    if request.method == 'POST':
        if form.validate_on_submit:
            user = User(first_name =form.first_name.data,
                        last_name =form.last_name.data,
                        email =form.email.data,
                        password = generate_password_hash(form.password.data)
                        )
            db.session.add(user)
            db.session.commit()
            return redirect('/login')
    
    
@app.route('/login', methods = ['POST','GET'])
def login():
        form = LoginForm()
        if form.validate_on_submit:
            user = User.query.filter_by(email = form.email.data).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect('/home')
            flash("Invalid details")
               
        return render_template('login.html', form=form)

@app.route('/logout',methods=['GET','POST'])
def logout():
    logout_user()
    return render_template('base.html')
    
@app.route('/home')
def home():
    todo_list=Todo.query.all()
    return render_template('index.html',todo_list=todo_list)

@app.route('/add',methods=["POST"]) 
def add():
    if not request.form:
        abort(400)
        
    todo = Todo(
            name=request.form.get('name'),
            due_date=request.form.get('due_date'),
            status=request.form.get('status')
        )
    db.session.add(todo)
    db.session.commit()
    return redirect(url_for("home"))
   
     
 
#@app.route('/todos')
#def todos():
    #todos = Todo.query.filter_by(todo_owner = current_user.id)
    #return render_template('todos.html', todos = todos)   

@app.route('/update/<int:task_id>',methods=['GET','POST'])
def update(task_id):
    if not request.form:
        abort(400)
    todo=Todo.query.get(task_id)
    if todo is None:
        abort(404)
    
    todo.name = request.form.get('name',todo.name)
    todo.due_date= request.form.get('due_date',todo.due_date)
    todo.status= request.form.get('status',todo.status)
    db.session.commit()
    return redirect(url_for("home"))
    #todo = Todo.query.filter_by(id=int(task_id),todo_owner=current_user.id).first()
    #if form.validate_on_submit():
        #todo.title=form.title.data
        #todo.due_date=form.due_date.data
        #todo.status=form.status.data
        #todo.title=request.form.get('ntitle')
        #todo.due_date=request.form.get('ndate')
        #todo.status=request.form.getlist("chk")
        #db.session.commit()
        #return redirect('/home')
    #elif request.method=='GET':
        #form.task_name.data=form.task_name
        #form.due_date.data=form.due_date
        #form.status.data=form.status
    #return render_template('update.html',form=form)


@app.route('/delete/<int:task_id>',methods=["POST"])
def delete(task_id):
    todo= Todo.query.get(task_id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("home")) 


if __name__=='__main__':
    with app.app_context():
         db.create_all()
    app.run(debug=True)