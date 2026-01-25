from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps
import os
import secrets

app = Flask(__name__)
PHOTOS_FOLDER = os.path.join(app.root_path, 'photos')

# Use environment variable for SECRET_KEY in production
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///rsvps.db')
db = SQLAlchemy(app)

# Admin credentials from environment variables
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'changeme')


def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username != ADMIN_USERNAME or auth.password != ADMIN_PASSWORD:
            return Response(
                'Login required to view RSVPs.',
                401,
                {'WWW-Authenticate': 'Basic realm="Admin Area"'}
            )
        return f(*args, **kwargs)
    return decorated


class RSVP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    attending = db.Column(db.Boolean, nullable=False)
    guest_count = db.Column(db.Integer, default=1)
    dietary_restrictions = db.Column(db.Text)
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


WEDDING_DETAILS = {
    'couple': 'Xuejuan & Evan',
    'person1': 'Xuejuan Ning',
    'person2': 'Evan Cudone',
    'date': 'June 6, 2026',
    'date_short': '06.06.2026',
    'venue': '4091 Wildwood Drive',
    'city': 'Allegan, Michigan',
}


@app.route('/')
def index():
    thumbnails_folder = os.path.join(PHOTOS_FOLDER, 'thumbnails')
    photos = sorted([f for f in os.listdir(thumbnails_folder)
                     if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))])
    return render_template('index.html', details=WEDDING_DETAILS, photos=photos)


@app.route('/photos/<filename>')
def serve_photo(filename):
    return send_from_directory(PHOTOS_FOLDER, filename)


@app.route('/photos/thumbnails/<filename>')
def serve_thumbnail(filename):
    return send_from_directory(os.path.join(PHOTOS_FOLDER, 'thumbnails'), filename)


@app.route('/photos/medium/<filename>')
def serve_medium(filename):
    return send_from_directory(os.path.join(PHOTOS_FOLDER, 'medium'), filename)


@app.route('/rsvp', methods=['POST'])
def rsvp():
    name = request.form.get('name')
    email = request.form.get('email')
    attending = request.form.get('attending') == 'yes'
    guest_count = int(request.form.get('guest_count', 1)) if attending else 0
    dietary_restrictions = request.form.get('dietary_restrictions', '')
    message = request.form.get('message', '')

    rsvp_entry = RSVP(
        name=name,
        email=email,
        attending=attending,
        guest_count=guest_count,
        dietary_restrictions=dietary_restrictions,
        message=message
    )
    db.session.add(rsvp_entry)
    db.session.commit()

    flash('Thank you for your RSVP!', 'success')
    return redirect(url_for('index'))


@app.route('/admin/rsvps')
@require_admin
def view_rsvps():
    rsvps = RSVP.query.order_by(RSVP.created_at.desc()).all()
    attending_count = sum(r.guest_count for r in rsvps if r.attending)
    not_attending_count = sum(1 for r in rsvps if not r.attending)
    return render_template('admin.html', rsvps=rsvps,
                         attending_count=attending_count,
                         not_attending_count=not_attending_count,
                         details=WEDDING_DETAILS)


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode)
