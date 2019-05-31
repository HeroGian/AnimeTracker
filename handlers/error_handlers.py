import logging
from jinja_setup import JENV


def handle_404(request, response, exception):
    logging.exception(exception)
    template = JENV.get_template('error.html')
    response.headers['Content-Type'] = 'text/html'
    params = {
        'error': 404,
        'error_message': 'La pagina richiesta non esiste :('
    }
    response.write(template.render(params))
    response.set_status(404)


def handle_401(request, response, exception):
    logging.exception(exception)
    template = JENV.get_template('error.html')
    response.headers['Content-Type'] = 'text/html'
    params = {
        'error': 401,
        'error_message': 'Non hai i permessi necessari per visualizzare la pagina :('
    }
    response.write(template.render(params))
    response.set_status(401)


def handle_500(request, response, exception):
    logging.exception(exception)
    template = JENV.get_template('error.html')
    response.headers['Content-Type'] = 'text/html'
    params = {
        'error': 500,
        'error_message': 'Il server non e stato in grado di gestire la richiesta :('
    }
    response.write(template.render(params))
    response.set_status(500)


def handle_503(request, response, exception):
    logging.exception(exception)
    template = JENV.get_template('error.html')
    response.headers['Content-Type'] = 'text/html'
    params = {
        'error': 503,
        'error_message': 'Errore di comunicazione col server :('
    }
    response.write(template.render(params))
    response.set_status(503)

