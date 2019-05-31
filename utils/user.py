def get_user_by_session(obj):
    """
    Ritorna l'utente salvato all'interno della sessione
    :param obj: riferimento all'handler
    :return:
    """
    if 'user_name' in obj.session:
        user = obj.session['user_name']
        return user
    return None
