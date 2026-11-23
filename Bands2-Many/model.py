
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin

db = SQLAlchemy()
admin = Admin(name='Bands 2 Admin')


class Bands(db.Model):
    BandID = db.Column(db.Integer, primary_key=True)
    BandName = db.Column(db.String(80), nullable=False)
    FormedYear = db.Column(db.Integer)
    HomeLocation = db.Column(db.String(80))

    memberships = db.relationship(
        'Memberships',
        backref='band',
        lazy=True,
        cascade='all, delete-orphan'
    )

    band_albums = db.relationship(
        'BandAlbums',
        backref='band',
        lazy=True,
        cascade='all, delete-orphan'
    )


class Members(db.Model):
    MemberID = db.Column(db.Integer, primary_key=True)
    MemberName = db.Column(db.String(80), nullable=False)
    MainPosition = db.Column(db.String(80))

    memberships = db.relationship(
        'Memberships',
        backref='member',
        lazy=True,
        cascade='all, delete-orphan'
    )


class Memberships(db.Model):
    MembershipID = db.Column(db.Integer, primary_key=True)

    BandID = db.Column(
        db.Integer,
        db.ForeignKey('bands.BandID'),
        nullable=False
    )

    MemberID = db.Column(
        db.Integer,
        db.ForeignKey('members.MemberID'),
        nullable=False
    )

    Role = db.Column(db.String(80))
    StartYear = db.Column(db.Integer)
    EndYear = db.Column(db.Integer)


class Albums(db.Model):
    AlbumID = db.Column(db.Integer, primary_key=True)
    AlbumTitle = db.Column(db.String(80), nullable=False)
    ReleaseYear = db.Column(db.Integer)

    band_albums = db.relationship(
        'BandAlbums',
        backref='album',
        lazy=True,
        cascade='all, delete-orphan'
    )


# Junction table for many-to-many relationship
class BandAlbums(db.Model):
    BandAlbumID = db.Column(db.Integer, primary_key=True)

    BandID = db.Column(
        db.Integer,
        db.ForeignKey('bands.BandID'),
        nullable=False
    )

    AlbumID = db.Column(
        db.Integer,
        db.ForeignKey('albums.AlbumID'),
        nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint(
            'BandID',
            'AlbumID',
            name='unique_band_album'
        ),
    )
