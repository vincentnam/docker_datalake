import flask
from keystoneauth1 import session as keystone_session
from keystoneauth1.identity import v3

def login_token(url_keystone, token):
    auth = v3.token.Token(auth_url=url_keystone,token=token)
    sess = keystone_session.Session(auth=auth)
    if sess.get_user_id() == None:
        return False
    else:
        return True
