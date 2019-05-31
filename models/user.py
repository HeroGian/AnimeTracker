from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.api.images import get_serving_url
from webapp2_extras.security import generate_password_hash
from webapp2_extras.security import check_password_hash


class Utente(ndb.Model):
    search_id = ndb.ComputedProperty(lambda self: self.key.id().lower())
    email = ndb.StringProperty(required=True)
    passw = ndb.StringProperty()
    associated_user = ndb.StringProperty()
    nome  = ndb.StringProperty(required=True)
    cognome = ndb.StringProperty(required=True)
    tipo  = ndb.StringProperty(required=True)
    avatar = ndb.BlobKeyProperty()
    avatar_url = ndb.StringProperty()
    created = ndb.DateProperty(auto_now_add=True)

    @classmethod
    def get_by_id(cls, user):
        record = Utente.query().filter(
            Utente.search_id == user.lower()
        ).fetch()
        if record:
            return record[0]
        return None

    @classmethod
    def get_or_insert(cls, username, email, nome, cognome, tipo, **kwargs):

        passw = kwargs.get('passw')
        avatar_url = kwargs.get('avatar_url')
        gplus_cred = kwargs.get('gplus_cred')
        associated_user = kwargs.get('associated_user')

        record = Utente.query().filter(
            Utente.search_id == username.lower()
        ).fetch()
        if record:
            # L'username esiste gia
            return 1

        if associated_user:
            record = Utente.get_from_associated(associated_user)
            if record:
                # L'username di terze parti e gia legato ad un account
                return 2

        record = Utente.query(Utente.email == email.lower()).fetch()
        if record:
            # L'indirizzo mail e gia legato ad un account
            return 3

        u = Utente(id=username)
        u.email = email.lower()
        u.nome  = nome
        u.cognome = cognome
        u.tipo = tipo

        if passw:
            u.passw = generate_password_hash(passw)

        if associated_user:
            if type(associated_user) == str:
                associated_user = associated_user.lower()
            u.associated_user = associated_user

        if avatar_url:
            u.avatar_url = avatar_url

        if gplus_cred:
            u.gpluscred = gplus_cred

        u.put()

        # Account creato
        return 0

    @classmethod
    def normal_login(cls, username, passw):
        user = Utente.query().filter(
            Utente.search_id == username.lower()
        ).fetch()
        if user and user[0].passw:
            if check_password_hash(pwhash=user[0].passw, password=passw):
                return user[0]
        return None

    @classmethod
    def get_from_associated(cls, associated):

        if type(associated) == str:
            associated = associated.lower()

        user = Utente.query(
            Utente.associated_user == associated
        ).fetch()

        if user:
            return user[0]
        return None

    @classmethod
    def get_avatar(cls, username):
        if username:
            user = Utente.get_by_id(username)
            if user.avatar:
                return get_serving_url(user.avatar)
            elif user.avatar_url:
                return user.avatar_url
            else:
                return '/static/unknown_avatar.jpg'

    @classmethod
    def insert_avatar(cls, username, blob_key):

        # Se e gia presente un avatar lo cancella dal blobstore
        user = Utente.get_by_id(username)
        if user.avatar:
            blobstore.delete(user.avatar)

        if user.avatar_url:
            user.avatar_url = None

        user.avatar = blob_key
        user.put()

    @classmethod
    def delete_avatar(cls, username):
        user = Utente.get_by_id(username)
        blobstore.delete(user.avatar)
        user.avatar = None
        user.put()

    @classmethod
    def get_user_from_name(cls, name):

        ret = Utente.query().filter(
            Utente.search_id >= name.lower()
        ).fetch()

        users = []
        for u in ret:
            if name.lower() in u.key.id().lower():
                if u.avatar:
                    avatar = get_serving_url(u.avatar)
                elif u.avatar_url:
                    avatar = u.avatar_url
                else:
                    avatar = '/static/unknown_avatar.jpg'
                users.append(
                    {
                        'username': u.key.id(),
                        'avatar': avatar
                    }
                )
        return users

    @classmethod
    def check_user(cls, user_name):
        return Utente.query().filter(
            Utente.search_id == user_name.lower()
        ).fetch()