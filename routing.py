#!/usr/bin/env python

import webapp2
from apis.list import UserListAPI
from apis.rece import AnimeReceAPI
from apis.auth import LoginAPI
from apis.add import AddAPI
from handlers.anime import AnimeInfoHandler
from handlers.oauth2 import SignUpPlusHandler, LoginPlusHandler
from handlers.auth import SignUpHandler, LoginHandler, LogoutHandler, LoginMalHandler, SignUpMalHandler
from handlers.home import MainHandler
from handlers.insert import InsertHandler
from handlers.search import SearchHandler
from handlers.profile import ProfileHandler
from handlers.oauth2 import Oauth2Handler, CalendarHandler
from handlers.error_handlers import *


config = {
  'webapp2_extras.sessions': {
    'secret_key': 'ppb52adekdhD25dqpbKu39dDKsd'
  },
  'webapp2_extras.auth': {
    'session_backend': 'memcache'
  }
}

app = webapp2.WSGIApplication([
    (r'^/$', MainHandler),
    (r'^/login$', LoginHandler),
    (r'^/logout$', LogoutHandler),
    (r'^/signup$', SignUpHandler),
    (r'^/search$', SearchHandler),
    (r'^/insert$', InsertHandler),
    (r'^/anime$', AnimeInfoHandler),
    (r'^/profile$', ProfileHandler),
    (r'^/login_mal$', LoginMalHandler),
    (r'^/signup_mal$', SignUpMalHandler),
    (r'^/signup_plus$', SignUpPlusHandler),
    (r'^/login_plus$', LoginPlusHandler),
    (r'^/oauth2callback$', Oauth2Handler),
    (r'^/calendar$', CalendarHandler),
    (r'^/api/list$', UserListAPI),
    (r'^/api/rece$', AnimeReceAPI),
    (r'^/api/sign$', LoginAPI),
    (r'^/api/add$', AddAPI)
],
    debug=True,
    config=config
)

app.error_handlers[404] = handle_404
app.error_handlers[503] = handle_503
app.error_handlers[401] = handle_401