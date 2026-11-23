
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from model import db, Bands, Members, Albums, Memberships, BandAlbums, admin
from flask_admin.contrib.sqla import ModelView
import os

load_dotenv()

# Create our Flask app object
app = Flask(__name__)

# Configure the flask app instance
CONFIG_TYPE = os.getenv(
    'CONFIG_TYPE',
    default='config.DevelopmentConfig'
)
app.config.from_object(CONFIG_TYPE)

# Initialize database
db.init_app(app)

# Create DB and tables if they don't exist
with app.app_context():
    db.create_all()

# Add tables to admin view
admin.init_app(app)
admin.add_view(ModelView(Bands, db.session, category="Bands"))
admin.add_view(ModelView(Members, db.session, category="Members"))
admin.add_view(ModelView(Memberships, db.session, category="Members"))
admin.add_view(ModelView(Albums, db.session, category="Albums"))
admin.add_view(ModelView(BandAlbums, db.session, category="Albums"))


# ==========================
# ROUTES
# ==========================

# Home page view
@app.route('/')
def index():
    return render_template('index.html')


# ==========================
# BANDS
# ==========================

@app.route('/bands/view')
def view_by_band():
    bands = Bands.query.all()
    memberships = Memberships.query.all()

    return render_template(
        'display_by_band.html',
        bands=bands,
        memberships=memberships
    )


@app.route('/bands/view/<int:id>')
def view_band(id):
    band = Bands.query.get_or_404(id)
    memberships = Memberships.query.all()

    return render_template(
        'view_band.html',
        band=band,
        memberships=memberships
    )


@app.route('/bands/add', methods=['GET', 'POST'])
def add_band():

    if request.method == 'POST':
        try:
            band_name = request.form['bandname']
            formed_year = request.form.get('formedyear') or None
            home_location = request.form.get('homelocation')

            new_band = Bands(
                BandName=band_name,
                FormedYear=formed_year,
                HomeLocation=home_location
            )

            db.session.add(new_band)
            db.session.commit()

            flash(f'Added band: {band_name}', 'success')
            return redirect(url_for('view_by_band'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error adding band: {e}', 'danger')

    return render_template('add_band.html')


@app.route('/bands/edit/<int:id>', methods=['GET', 'POST'])
def edit_band(id):
    band = Bands.query.get_or_404(id)

    if request.method == 'POST':
        try:
            band.BandName = request.form.get('bandname')
            band.FormedYear = request.form.get('formedyear') or None
            band.HomeLocation = request.form.get('homelocation')

            db.session.commit()

            flash(
                f'Updated info for band: {band.BandName}',
                'info'
            )

            return redirect(url_for('view_by_band'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating band: {e}', 'danger')

    return render_template('edit_band.html', band=band)


@app.route('/bands/delete/<int:id>', methods=['POST'])
def delete_band(id):
    band = Bands.query.get_or_404(id)
    band_name = band.BandName

    try:
        # Save IDs of albums connected to this band
        album_ids = [ba.AlbumID for ba in band.band_albums]

        # Memberships and album links are deleted
        # through the cascade relationships
        db.session.delete(band)
        db.session.flush()

        # Delete albums that no longer belong to any band
        for album_id in album_ids:
            album = db.session.get(Albums, album_id)

            if album and not album.band_albums:
                db.session.delete(album)

        db.session.commit()

        flash(f'Deleted band: {band_name}', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting band: {e}', 'danger')

    return redirect(url_for('view_by_band'))


# ==========================
# MEMBERS
# ==========================

@app.route('/members/view')
def view_by_member():
    members = Members.query.all()
    memberships = Memberships.query.all()

    return render_template(
        'display_by_member.html',
        members=members,
        memberships=memberships
    )


@app.route('/members/view/<int:id>')
def view_member(id):
    member = Members.query.get_or_404(id)
    memberships = Memberships.query.all()

    return render_template(
        'view_member.html',
        member=member,
        memberships=memberships
    )


@app.route('/members/add', methods=['GET', 'POST'])
def add_member():
    bands = Bands.query.all()

    if request.method == 'POST':
        try:
            new_member = Members(
                MemberName=request.form['membername'],
                MainPosition=request.form.get('mainposition')
            )

            db.session.add(new_member)
            db.session.commit()

            flash(
                f'Added member: {new_member.MemberName}',
                'success'
            )

            return redirect(url_for('view_by_member'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error adding member: {e}', 'danger')

    return render_template('add_member.html', bands=bands)


@app.route('/members/edit/<int:id>', methods=['GET', 'POST'])
def edit_member(id):
    member = Members.query.get_or_404(id)

    if request.method == 'POST':
        try:
            member_name = request.form.get('membername')
            main_position = request.form.get('mainposition')

            member.MemberName = member_name
            member.MainPosition = main_position

            db.session.commit()

            flash(
                f'Updated info for member: {member_name}',
                'info'
            )

            return redirect(url_for('view_by_member'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error editing member: {e}', 'danger')

    return render_template('edit_member.html', member=member)


@app.route('/members/delete/<int:id>', methods=['POST'])
def delete_member(id):
    member = Members.query.get_or_404(id)
    member_name = member.MemberName

    try:
        db.session.delete(member)
        db.session.commit()

        flash(f'Deleted member: {member_name}', 'info')

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting member: {e}', 'danger')

    return redirect(url_for('view_by_member'))


# ==========================
# MEMBERSHIPS
# ==========================

@app.route('/memberships/add', methods=['GET', 'POST'])
def add_membership():
    bands = Bands.query.all()
    members = Members.query.all()

    if request.method == 'POST':
        try:
            band_id = request.form.get('bandid')
            member_id = request.form.get('memberid')
            role = request.form.get('role')
            start_year = request.form.get('startyear') or None
            end_year = request.form.get('endyear') or None

            member = Members.query.get_or_404(member_id)
            band = Bands.query.get_or_404(band_id)

            membership = Memberships(
                BandID=band_id,
                MemberID=member_id,
                Role=role,
                StartYear=start_year,
                EndYear=end_year
            )

            db.session.add(membership)
            db.session.commit()

            flash(
                f'Added membership for {member.MemberName} '
                f'in {band.BandName}',
                'success'
            )

            return redirect(url_for('view_by_band'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error adding membership: {e}', 'danger')

    return render_template(
        'add_membership.html',
        bands=bands,
        members=members
    )


@app.route('/memberships/edit/<int:id>', methods=['GET', 'POST'])
def edit_membership(id):
    membership = Memberships.query.get_or_404(id)
    bands = Bands.query.all()
    members = Members.query.all()

    if request.method == 'POST':
        try:
            membership_band_id = request.form.get('bandid')
            membership_member_id = request.form.get('memberid')
            membership_role = request.form.get('role')
            membership_start_year = request.form.get('startyear') or None
            membership_end_year = request.form.get('endyear') or None

            band = Bands.query.get_or_404(membership_band_id)
            member = Members.query.get_or_404(membership_member_id)

            membership.BandID = membership_band_id
            membership.MemberID = membership_member_id
            membership.Role = membership_role
            membership.StartYear = membership_start_year
            membership.EndYear = membership_end_year

            db.session.commit()

            flash(
                f'Updated membership for member '
                f'{member.MemberName} in band {band.BandName}',
                'info'
            )

            return redirect(url_for('view_by_band'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error editing membership: {e}', 'danger')

    return render_template(
        'edit_membership.html',
        membership=membership,
        bands=bands,
        members=members
    )


@app.route('/memberships/delete/<int:id>', methods=['POST'])
def delete_membership(id):
    membership = Memberships.query.get_or_404(id)

    try:
        db.session.delete(membership)
        db.session.commit()
        flash('Membership removed', 'success')

    except Exception as e:
        db.session.rollback()
        flash('Error removing membership', 'danger')

    return redirect(url_for('view_by_band'))


# ==========================
# ALBUMS
# MANY-TO-MANY RELATIONSHIP
# ==========================

@app.route('/albums/add', methods=['GET', 'POST'])
def add_album():
    bands = Bands.query.all()

    if request.method == 'POST':
        try:
            album_title = request.form['albumtitle']
            release_year = request.form.get('releaseyear') or None

            # Get multiple bands from checkboxes
            band_ids = request.form.getlist('bandids')

            if not band_ids:
                flash(
                    'Please select at least one band.',
                    'danger'
                )
                return render_template(
                    'add_album.html',
                    bands=bands
                )

            new_album = Albums(
                AlbumTitle=album_title,
                ReleaseYear=release_year
            )

            db.session.add(new_album)
            db.session.flush()

            # Add a BandAlbums record for each band
            for band_id in set(band_ids):
                band = db.session.get(Bands, int(band_id))

                if band is None:
                    raise ValueError(
                        'One of the selected bands does not exist.'
                    )

                band_album = BandAlbums(
                    BandID=band.BandID,
                    AlbumID=new_album.AlbumID
                )

                db.session.add(band_album)

            db.session.commit()

            flash(
                f'Added album: {album_title}',
                'success'
            )

            return redirect(url_for('view_by_band'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error adding album: {e}', 'danger')

    return render_template('add_album.html', bands=bands)


# ==========================
# APP LAUNCH
# ==========================

if __name__ == '__main__':
    app.run(debug=True)
