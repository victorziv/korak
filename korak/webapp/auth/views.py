from flask import (
    redirect,
    url_for,
    flash,
    render_template,
    request
)
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)
from config import logger
from . import auth
from .oauth import OAuthSignIn
from webapp.models import Usermod
# __________________________________________


# @auth.before_app_request
# def before_request():
#     if current_user.is_authenticated:
#         current_user.update_last_seen()
# __________________________________________


@auth.route('/authorize/<provider>')
def oauth_authorize(provider):
    logger.debug("PROVIDER: %r", provider)
    logger.debug("Current user: %r", current_user)
    if not current_user.is_anonymous:
        redirect(url_for('main.dashboard'))

    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()
# __________________________________________


@auth.route('/callback/<provider>')
def oauth_callback(provider):

    if not current_user.is_anonymous:
        return redirect(url_for('main.dashboard'))

    oauth = OAuthSignIn.get_provider(provider)
    profile = oauth.callback()

    # TODO: Temporarily, till email CHECK constraint is fully implemented
    if 'hd' not in profile or profile['hd'] != 'infinidat.com':
#     if 'hd' not in profile:
        logger.error("Not Infinidat user: %s", profile['email'])
        flash('Only Infinidat users are allowed in')
        return redirect(url_for('auth.login'))

    if profile['social_id'] is None:
        logger.error("Authentication failed for profile: %r", profile)
        flash('Authentication failed for user %s' % profile['email'])
        return redirect(url_for('auth.login'))

    u = Usermod()
    user = u.get_by_social_id(profile['social_id'])
    logger.debug('User found in DB: %r', user)
    if not user:
        user = u.save(profile)
        if not user:
            logger.error("Authentication failed for profile: %r", profile)
            flash('Authentication failed for user %s' % profile['email'])
            return redirect(url_for('auth.login'))

    login_user(user, True)
    return redirect(request.args.get("next") or url_for('main.dashboard'))
# __________________________________________


@auth.route('/login')
def login():
    return render_template("auth/login.html")
# __________________________________________


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out!")
    return redirect(url_for('auth.login'))
# __________________________________________
