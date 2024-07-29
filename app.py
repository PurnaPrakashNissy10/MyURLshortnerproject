from flask import Flask, request, redirect, render_template, url_for
import string
import random
import sqlite3

app = Flask(__name__)

# Database setup
conn = sqlite3.connect('url_shortener.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS urls
             (id INTEGER PRIMARY KEY AUTOINCREMENT, short TEXT, original TEXT)''')
conn.commit()


# Generate a random string of 6 characters
def generate_short_id():
    characters = string.ascii_letters + string.digits
    short_id = ''.join(random.choice(characters) for _ in range(6))
    return short_id


# Home page
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        original_url = request.form['original_url']
        short_id = generate_short_id()

        # Ensure the short ID is unique
        c.execute('SELECT short FROM urls WHERE short = ?', (short_id,))
        while c.fetchone() is not None:
            short_id = generate_short_id()

        c.execute('INSERT INTO urls (short, original) VALUES (?, ?)', (short_id, original_url))
        conn.commit()

        short_url = request.host_url + short_id
        return render_template('home.html', short_url=short_url)

    return render_template('home.html')


# Redirect to original URL
@app.route('/<short_id>')
def redirect_to_url(short_id):
    c.execute('SELECT original FROM urls WHERE short = ?', (short_id,))
    result = c.fetchone()
    if result:
        return redirect(result[0])
    else:
        return 'URL not found', 404


if __name__ == '__main__':
    app.run(debug=True)
