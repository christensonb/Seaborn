from settings.global_import import *

log.trace("Importing endpoint user.models")
import re
from werkzeug.security import check_password_hash

EMAIL_REGEX = re.compile(r'^.+@([^.@][^@]+)$')
GENERIC_REGEX = re.compile(r'^[A-Za-z0-9_]{2,30}$')

AUTH_LEVELS_ENUM = ['User',  # someone who has is a basic user
                    'Demo',  # someone who has signed up to be a demo user
                    'Superuser',  # someone trusted within the company
                    'Admin']  # someone trusted and given responsibility

USER_STATUS_ENUM = ['Active',
                    'Suspended']


class User(db.Model, ApiModel):
    __tablename__ = "usr"
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    email = db.Column(db.String(120), unique=True)
    full_name = db.Column(db.String(30), default="")
    _password_hash = db.Column(db.String)
    status = db.Column(db.Enum(*USER_STATUS_ENUM, name='user_status'), default=USER_STATUS_ENUM[0])
    auth_level = db.Column(db.Enum(*AUTH_LEVELS_ENUM, name='user_auth_level'), default=AUTH_LEVELS_ENUM[0])
    created_timestamp = db.Column(db.DateTime(timezone=True), default=cst_now)

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @classmethod
    def keys(cls):
        return ['user_id', 'username', 'email', 'full_name']

    def check_password(self, password):
        return check_password_hash(self._password_hash, password)

    @property
    def is_authenticated(self):
        return True

    def get_id(self):
        return self.user_id

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return self.status == 'Active'

    def is_auth_level(self, auth_level):
        """
        :param auth_level:  str of level to test for
        :return:            bool if the user is of the auth level
        """
        try:
            if AUTH_LEVELS_ENUM.index(self.auth_level) < AUTH_LEVELS_ENUM.index(auth_level):
                self._suspect += 1
                db.session.add(self)
                db.session.commit()
                return False
            return True
        except:
            raise

    @classmethod
    def validator_email(cls, email, **kwargs):
        """ This will determine if the email address is valid and not used"""
        assert EMAIL_REGEX.match(email) and len(email) < 121, 'Invalid Email Syntax: %s' % email

    @classmethod
    def validator_username(cls, username, **kwargs):
        """ This will determine if the email address is valid and not used"""
        assert GENERIC_REGEX.match(username), 'Invalid Username Syntax: %s' % username

    @classmethod
    def validate_full_name(cls, full_name, **kwargs):
        """ This will determine if the email address is valid and not used"""
        assert GENERIC_REGEX.match(full_name), 'Invalid Full Name Syntax: %s' % full_name

    @classmethod
    def validate_password(cls, password, **kwargs):
        assert password == kwargs.get('confirm_password', password), "Passwords don't match"

    @classmethod
    def validate_auth_level(cls, auth_level, **kwargs):
        assert auth_level in AUTH_LEVELS_ENUM, "Auth Level is not valid"

    @classmethod
    def validate_status(cls, status, **kwargs):
        assert status in USER_STATUS_ENUM, "User status is not valid"
