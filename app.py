from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import bcrypt
from urllib.parse import quote as url_quote

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['MONGO_URI'] = "mongodb://localhost:27017/blog_platform"
mongo = PyMongo(app)

@app.route('/')
def index():
    if 'username' in session:
        posts = mongo.db.posts.find()
        return render_template('index.html', username=session['username'], posts=posts)
    return redirect(url_for('login'))

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'username': request.form['username']})
        
        if login_user:
            if bcrypt.checkpw(request.form['password'].encode('utf-8'), login_user['password']):
                session['username'] = request.form['username']
                return redirect(url_for('index'))
        
        return 'Invalid username/password combination'
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'username': request.form['username']})
        
        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert_one({'username': request.form['username'], 'password': hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        
        return 'That username already exists!'
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/create', methods=['POST', 'GET'])
def create_post():
    if 'username' in session:
        if request.method == 'POST':
            posts = mongo.db.posts
            posts.insert_one({'title': request.form['title'], 'content': request.form['content'], 'author': session['username']})
            return redirect(url_for('index'))
        return render_template('create_post.html')
    return redirect(url_for('login'))

@app.route('/edit/<post_id>', methods=['POST', 'GET'])
def edit_post(post_id):
    if 'username' in session:
        post = mongo.db.posts.find_one({'_id': ObjectId(post_id)})
        if request.method == 'POST':
            mongo.db.posts.update_one({'_id': ObjectId(post_id)}, {'$set': {'title': request.form['title'], 'content': request.form['content']}})
            return redirect(url_for('index'))
        return render_template('edit_post.html', post=post)
    return redirect(url_for('login'))

@app.route('/delete/<post_id>')
def delete_post(post_id):
    if 'username' in session:
        mongo.db.posts.delete_one({'_id': ObjectId(post_id)})
        return redirect(url_for('index'))
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
