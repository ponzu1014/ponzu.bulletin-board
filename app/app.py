from flask import Flask, render_template, request, redirect, session
from datetime import datetime
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config['SESSION_PERMANENT'] = False

def clear_table():
    conn = sqlite3.connect('database.db')
    conn.execute("DELETE FROM post")
    conn.commit()
    conn.close()



def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn



#テーブル作成
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS post (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            created_at TEXT,
            body TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

#登録
@app.route('/register', methods = ["GET", "POST"])
def register():
    if 'username' in session:
        return redirect('/')
    
    if request.method == "POST":
        username = request.form["username"]
        pw = request.form["password"]
        hashed_pw = generate_password_hash(pw)
        try:
            conn = get_db_connection()
            conn.execute("INSERT INTO user ( username, password ) VALUES (?, ?)",
                        (username, hashed_pw))
            conn.commit()
            conn.close()
            return redirect('/login')
        except sqlite3.IntegrityError:
            return "このユーザー名は既に使用されています"
        except Exception as e:
            return f"エラーが発生しました: {str(e)}"
    return render_template('register.html')



#ログイン
@app.route('/login', methods = ["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        pw = request.form["password"]

        conn = get_db_connection() 
        user = conn.execute("SELECT * FROM user WHERE username=?", 
                            (username,)).fetchone() 
        conn.close() 
        if user is not None and check_password_hash(user['password'], pw): 
            session['username'] = username 
            return redirect('/') 
        else:
            return "ログイン失敗"

    return render_template('login.html')



#ログアウト
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')



#掲示板
@app.route('/') #homeの表示＋コメントの表示
def index(): 
    if 'username' not in session:
        return render_template('home_public.html')
    
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM post ORDER BY rowid DESC').fetchall()
    conn.close()
    return render_template('home.html', posts = posts)


@app.route('/button', methods = ["POST"])   #書き込む　のボタン
def button():
    return render_template("forme.html")


@app.route('/comment', methods = ["POST"])  #コメントを書くとhomeに戻る＋コメントを表示させる
def write(): 
    name = session["username"]
    conn = get_db_connection()
    
    body = request.form["comment"]
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = get_db_connection()
    conn.execute("INSERT INTO post (name, body, created_at ) VALUES (?, ?, ?)",
                (name, body, created_at))
    conn.commit()
    conn.close()
    return redirect('/')


if __name__ == '__main__':
    #init_db()
    #clear_table()
    app.run(debug=True)