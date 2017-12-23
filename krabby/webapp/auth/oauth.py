import json
import requests
from rauth import OAuth2Service
from flask import url_for
from flask import (
    current_app,
    request,
    redirect
)

from config import logger
# ==================================


class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return url_for('auth.oauth_callback', provider=self.provider_name,
                       _external=True)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]
# ==================================


class GoogleSignIn(OAuthSignIn):
    def __init__(self):
        super(GoogleSignIn, self).__init__('google')
        google_params = requests.get('https://accounts.google.com/.well-known/openid-configuration').json()
        self.service = OAuth2Service(
            name='google',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url=google_params.get('authorization_endpoint'),
            base_url=google_params.get('userinfo_endpoint'),
            access_token_url=google_params.get('token_endpoint')
        )
    # _____________________________________

    def authorize(self):
        return redirect(
            self.service.get_authorize_url(
                scope='profile email',
                response_type='code',
                redirect_uri=self.get_callback_url()
            )
        )
    # ______________________________________

    def callback(self):
        if 'code' not in request.args:
            return None, None, None

        code = request.args['code']
        data = {
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.get_callback_url()
        }

        oauth_session = self.service.get_auth_session(
            data=data,
            decoder=lambda b: json.loads(b.decode('utf-8'))
        )

        profile = oauth_session.get('').json()

        profile['social_id'] = 'google$' + str(profile.get('sub'))
        profile['username'] = profile['email'].split('@')[0]

        logger.info('===== USER PROFILE: %r', profile)
        return profile
    # ______________________________________
