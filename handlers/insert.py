import urllib
import webapp2
from datetime import datetime
from utils.user import get_user_by_session
from models.anime import Anime
from models.user import Utente
from jinja_setup import JENV
from google.appengine.ext import blobstore
from handlers.base import BaseHandler
from google.appengine.ext.webapp import blobstore_handlers


class InsertHandler(BaseHandler, blobstore_handlers.BlobstoreUploadHandler):
    def get(self, template = JENV.get_template('insert.html')):

        self.session['current_page'] = '/insert'

        user = get_user_by_session(self)

        if not user:
            webapp2.abort(code=401)

        upload_url = blobstore.create_upload_url('/insert')
        params = {
            'upload_url': upload_url,
            'avatar_header': Utente.get_avatar(user),
            'user': user,
        }
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(template.render(params))

    def post(self):
        titolo = self.request.get('titolo')
        num_ep = self.request.get('num_ep')
        status = self.request.get('status')
        descr  = self.request.get('descr')
        data_inizio = self.request.get('start_date')
        data_fine   = self.request.get('end_date')

        img_c = self.get_uploads()

        errors = {}

        if not titolo:
            errors['titolo'] = True

        if not img_c:
            errors['cover'] = True

        if data_inizio != '':
            data_inizio = datetime.strptime(
                str(data_inizio),
                '%Y-%m-%d'
            ).date()
        else:
            data_inizio = None

        if data_fine != '':
            data_fine = datetime.strptime(
                str(data_fine),
                '%Y-%m-%d'
            ).date()
        else:
            data_fine = None

        if num_ep == '':
            num_ep = 0

        if not errors:
            ani_key = Anime.insert(
                titolo=titolo,
                num_ep=int(num_ep),
                descr=descr,
                status=str(status),
                start_date=data_inizio,
                end_date=data_fine,
                blob_key=img_c[0].key()
            )

            self.redirect('/anime?' + urllib.urlencode({'id': ani_key.id()}))
        else:
            t = JENV.get_template('insert.html')
            self.response.write(t.render(errors))
