from flask import Flask,render_template,redirect,url_for,request,flash,session
import mysql.connector
from werkzeug.utils import secure_filename
mydb=mysql.connector.connect(
    host="localhost",
    user="root",
    password="admin",
    database="our_users"
)
app=Flask(__name__)
UPLOAD_FOLDER='static/images/'
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
import os
import uuid
app.config['SECRET_KEY']="my super secret key is too secret"
mycursor=mydb.cursor()
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        username=request.form['username']
        name=request.form['name']
        email=request.form['email']
        password=request.form['password']
        favorite_color=request.form['favorite_color']
        about_author=request.form['about_author']

        #check if the username or email already exists in the db
        cursor=mydb.cursor()
        cursor.execute("SELECT * FROM users where username=%s OR email=%s",(username,email))
        existing_user=cursor.fetchone()

        if existing_user:
            flash("Username or email already exists.please choose a different one.")
            return redirect(url_for('register'))
        cursor.execute("INSERT INTO users (username,name,email,favorite_color,about_author,password)values(%s,%s,%s,%s,%s,%s)",
        (username,name,email,favorite_color,about_author,password))
        mydb.commit()
        flash("Registration succesful! Please login to continue")
        return redirect(url_for('login'))

    return render_template("register.html")
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        query="SELECT * FROM users WHERE username=%s"
        values=(username,)
        mycursor.execute(query,values)
        user=mycursor.fetchone()
        if user:
            user_id=user[0]
            if password==user[7]:
                session['user_id']=user_id
                flash("Login Sucessful!")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password-Try Again!")
        else:
            flash("that User Doesn't Exist! Try Again...")
    return render_template('login.html')
@app.route('/logout')
def logout():
    session.pop('user_id',None)
    flash("You Have Been Logged Out! Thanks For Stopping By ... ")
    return redirect(url_for('login')) 

@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    if 'user_id' in session:
        user_id=session['user_id']
        query="SELECT * FROM users WHERE id =%s"
        values=(user_id,)
        mycursor.execute(query,values)
        user=mycursor.fetchone()
        if request.method=="POST":
            name=request.form['name']
            email=request.form['email']
            fovorite_color=request.form['favorite_color']
            username=request.form['username']
            about_author=request.form['about_author']

            #chech for profile pic
            if 'profile_pic' in request.files and request.files['profile_pic']:
                profile_pic=request.files[profile_pic]
                #grab image name
                pic_filename=secure_filename(profile_pic.filename)
                #set uuid
                pic_name=str(uuid.uuid1())+"_"+pic_filename
                #save the image
                profic_pic.save(os.path.join(app.config['UPLOAD_FOLDER'],pic_name))

                #change it to string to save to db
                profile_pic=pic_name
            else:
                profile_pic=user[profile_pic]
            
            #Update user data in the database
            query="UPDATE users SET name=%s,email=%s,favorite_color=%s,username=%s,about_author=%s,profile_pic=%s WHERE id=%s"
            values=(name,email,favorite_color,username,about_author,profile_pic,user_id)
            mycursor.execute(query,values)
            mydb.commit()

            flash("User Updated Successfuly!")
            return render_template("dashboard.html",user=user)
        else:
            return render_template("dashboard.html",user=user)
    else:
        flash("please login to access the Dashboard...")
        return redirect(url_for('login'))   
@app.route("/update/<int:id>",methods=['GET','POST'])
def update(id):
    if 'user_id' in session:
        user_id=session['user_id']
        query="SELECT * FROM users WHERE id=%s"
        values=(id,)
        mycursor.execute(query,values)
        name_to_update=mycursor.fetchone()

        if name_to_update:
            if request.method=="POST":
                name=request.form['name']
                email=request.form['email']
                favorite_color=request.form['favorite_color']
                username=request.form['username']
                about_author=request.form['about_author']

                #cHECK IF A NEW PROFILE PIUCTURE IS UPLOADED
                if 'profile_pic' in request.files:
                    profile_pic=request.files['profile_pic']
                    if profile_pic.filename!='':
                        filename=secure_filename(profile_pic.filename)
                        profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        #save the filename in the db or update the existing filename filename
                
                query="UPDATE users SET name=%s,email=%s,favorite_color=%s,username=%s,about_author=%s WHERE id=%s"
                values=(name,email,favorite_color,username,about_author,id)
                mycursor.execute(query,values)
                mydb.commit()

                flash("User Updated Successfully!")
                return redirect(url_for('update',id=id))
                
            return render_template("update.html",name_to_update=name_to_update,id=id)
        else:
            flash("User Not Found!")
    else:
        flash("Please login to update a user...")
        return redirect(url_for('login'))

@app.route('/delete/<int:id>')
def delete(id):
    if 'user_id' in session:
        user_id=session['user_id']

        #Check if the logged in user is authorized to database the user
        if user_id==id:
            name_to_update=None
            query="SELECT * FROM users WHERE id=%s"
            values=(id,)
            mycursor.execute(query,values)
            name_to_delete=mycursor.fetchone()

            if name_to_delete:
                try:
                    query="DELETE FROM users WHERE id=%s"
                    values=(id,)
                    mycursor.execute(query,values)
                    mydb.commit()
                    flash("User Deleted Successfully!!")
                    return redirect(url_for('register'))
                
                except:
                    flash("Whoops! There was a problem deleting the user , try again")
                    return redirect(url_for('register'))
            else:
                flash("User Not Found!")
                return redirect(url_for('register'))
        else:
            flash("Sorry, you can't delte that user!")
            return redirect(url_for('dashboard'))
    else:
        flash("Please log in to delte a user...")
        return redirect(url_for('login'))
@app.route('/add-post',methods=['GET','POST'])
def add_post():
    if request.method=='POST':
        title=request.form['title']
        content=request.form['content']
        slug=request.form['slug']
        poster_id=session['user_id']
        
        #Insert the new post into the datase
        query="INSERT INTO posts(title,content,slug,poster_id)VALUES(%s,%s,%s,%s)"
        values=(title,content,slug,poster_id)
        mycursor.execute(query,values)
        mydb.commit()

        #Return a message
        flash("Blog Post Submitted Successfully!")

        #Redirect to the Webpage
        return redirect(url_for('posts'))
    return render_template("add_post.html")
@app.route('/posts')
def posts():
    query="SELECT * FROM posts"
    mycursor.execute(query)
    posts=mycursor.fetchall()
    print(posts)
    return render_template("posts.html",posts=posts)
@app.route('/posts/<int:id>')
def post(id):
    post_query="SELECT * FROM posts WHERE id=%s"
    post_values=(id,)
    mycursor.execute(post_query,post_values)
    post=mycursor.fetchone()


    if post:
        user_query="SELECT * from USERS where id=%s"
        user_values=(post[5],)#Assuming 'userid is the column name in the posts table
        mycursor.execute(user_query,user_values)
        user=mycursor.fetchone()

        if user:
            return render_template('posts.html',post=post,user=user)
        else:
            flash("User Not Found!")
    else:
        flash("Post Not Found!")
        return redirect(url_for('posts'))
@app.route('/posts/edit/<int:id>',methods=['GET','POST'])
def edit_post(id):
    if 'user_id' in session:
        user_id=session['user_id']
        query="SELECT * FROM posts WHERE id=%s"
        values=(id,)
        mycursor.execute(query,values)
        post=mycursor.fetchone()
        print(post)
        if post:
            if user_id==post[5] or user_id==14:
                if request.method=="POST":
                    title=request.form['title']
                    content=request.form['content']
                    slug=request.form['slug']
                    query="update posts set title=%s,slug=%s,content=%s where id=%s"
                    values=(title,slug,content,id)
                    mycursor.execute(query,values)
                    mydb.commit()
                    flash("Blog Post Was Updated!") 
                    return redirect(url_for('posts'))
                else:
                    return render_template('edit_post.html',post=post)
            else:
                flash("Your not Authorized To Edit that Post!")
        else:
            flash("Post Not Found!")
    else:
        flash("Please login to edit post...")
    return redirect(url_for('posts'))   
@app.route('/posts/delete/<int:id>')
def delete_post(id):
    if 'user_id' in session:
        user_id=session['user_id']
        query="SELECT * FROM posts WHERE id=%s"
        values=(id,)
        mycursor.execute(query,values)
        post=mycursor.fetchone()
        if post:
            if user_id==post[5] or user_id==14:
                query="DELETE FROM posts WHERE id=%s"
                values=(id,)
                mycursor.execute(query,values)
                mydb.commit()
                flash("Blog Post Was Deleted!")
            else:
                flash("You Aren1t Authorized To Delete That Post!")
        else:
            flash("Post Not Found!")
    else:
        flash("Please login to delete a post...")
    return redirect(url_for('posts'))

@app.route('/search',methods=["POST"])
def search():
    if request.method=="POST":
        searched=request.form['searched']
        if searched:
            query="SELECT * FROM posts WHERE title LIKE %s"
            values=('%' + searched + '%',)
            mycursor.execute(query,values)
            posts=mycursor.fetchall()
            print(posts)
            return render_template("search.html",searched=searched,posts=posts)
    return redirect(url_for('posts'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

    


if __name__ == '__main__':
    app.run(debug=True)               
