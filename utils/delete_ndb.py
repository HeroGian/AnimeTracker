from models.anime import Anime
from models.user import Utente
from models.list import Like, Watching
from models.recens import Recensione


def delete():
    a = Anime.query().fetch()
    for a in a:
        a.key.delete()

    r = Recensione.query().fetch()
    for r in r:
        r.key.delete()

    l = Like.query().fetch()
    for l in l:
        l.key.delete()

    w = Watching.query().fetch()
    for w in w:
        w.key.delete()

    u = Utente.query().fetch()
    for u in u:
        u.key.delete()