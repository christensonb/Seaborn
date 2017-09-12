from settings.global_import import *

log.trace("Importing endpoint user.views")

from werkzeug.security import generate_password_hash
from endpoints.user.models import User

USER = Blueprint('user', __name__)


@USER.route('/user', methods=['GET'])
@api_endpoint(auth='User')
def get():
    """
    :return: User dict of the current user
    """
    return current_user


@USER.route('/user/login', methods=['POST'])
@api_endpoint(auth='Anonymous')
def login(username, password, email=None):
    """
        This will process logging the user in
    :param username: str of the username
    :param password: str of the password
    :param email:    str of the email as an alternative to username
    :return:         User dict
    """
    if email and username == "":
        existing_users = User.query.filter_by(email=email).all()
    elif email:
        existing_users = User.query.filter(or_(User.username == username,
                                               User.email == email)).all()
    else:
        existing_users = User.query.filter_by(username=username).all()

    if not existing_users:
        if username:
            raise NotFoundException(username='Invalid User')
        else:
            raise NotFoundException(email='Invalid Email')

    for existing_user in existing_users:
        if existing_user.check_password(password):
            if not existing_user.is_active:
                raise ForbiddenException("This account is not active")

            login_user(existing_user, remember=True)
            flash('You have successfully logged in.', 'success')
            return existing_user
        else:
            pass
    raise UnauthorizedException(password='Invalid Password: %s' % password)


@USER.route('/user/login/email', methods=['POST'])
@api_endpoint(auth='Anonymous')
def login_by_email(email, password):
    """
        This will process logging the user in
    :param email:    str of the email as an alternative to username
    :param password: str of the password
    :return:         User dict
    """
    return login._undecorated(username="", password=password, email=email)


@USER.route('/user/logout', methods=['POST'])
@api_endpoint(auth='User', redirect='/user/login')
def logout():
    """
        This will log the user out
    :return: str of a message saying success
    """
    session.pop('_id', None)
    return 'Successfully logged out'


@USER.route('/user', methods=['DELETE'])
@api_endpoint(auth='Admin', validator=User, delete=True)
def delete(user_id=None):
    """
        This will delete a user from the Database
    :param user_id: int of the users id
    :return:        User dict of the user created
    """
    user = User.query.filter_by(user_id=user_id).first()
    return user


@USER.route('/user/username', methods=['DELETE'])
@api_endpoint(auth='Admin', validator=User, delete=True)
def username_delete(username):
    """
        This will delete a user from the Database
    :param username: str of the username give my the player
    :return:         User dict of the user created
    """
    user = User.query.filter_by(username=username).first()
    return user


@USER.route('/user/signup', methods=['PUT'])
@api_endpoint(auth='Anonymous', validator=User, html='user/signup.html', redirect='/')
def create(username, password, email=None, full_name=None):
    """
        This will create a PnP user
    :param username:  str of the username give my the player
    :param password:  str of the password which will be hashed
    :param email:     str of the user's email address
    :param full_name: str of the full name
    :return:          User dict of the user created
    """
    if email:
        users = User.query.filter(or_(User.username == username,
                                      User.email == email)).all()
    else:
        users = User.query.filter_by(username=username).all()

    if not users:
        users = [User(username=username, _password_hash=generate_password_hash(password),
                      full_name=full_name or username, status='Active')]

    for user in users:
        if user.check_password(password):
            if not user.is_active:
                raise ForbiddenException("This user exists, but is not active")

            user.full_name = full_name or user.full_name
            if len(users) == 1:
                user.username = username or user.username
                user.email = email or user.email

            user.auth_level = "User"
            # this is here instead of the decorator so that the user can be logged in
            db.session.add(user)
            db.session.commit()

            login_user(user, remember=True)
            return user

    time.sleep(2)
    if users[0].username == username:
        raise UnauthorizedException(username="Username %s has already been taken" % username)
    else:
        raise ForbiddenException(username="Email %s has already been taken" % email)


@USER.route('/user', methods=['POST'])
@api_endpoint(auth='User', validator=User, html='user/signup.html', redirect='/')
def update(username=None, email=None, full_name=None, password=None):
    """
        This will update a PnP user
    :param username:  str of the username give my the player
    :param email:     str of the user's email address
    :param full_name: str of the full name
    :param password:  str of the password which will be hashed
    :return:          User dict of the user updated
    """
    conditions = [User.user_id == current_user.user_id]
    if username is not None:
        conditions.append(User.username == username)
    if email is not None:
        conditions.append(User.email == email)
    users = User.query.filter(or_(*conditions)).all()

    if not [user for user in users if user.user_id == current_user.user_id]:
        raise NotFoundException("Cannot find user of user_id: %s" % current_user.user_id)

    if email is not None and [user for user in users if user.user_id != current_user.user_id and user.email == email]:
        raise ForbiddenException("Email address (%s) is already being used" % email)

    if len(users) > 1:
        raise UnauthorizedException("Username (%s) is already being used" % username)

    user = users[0]
    for k, v in function_kwargs(exclude_keys=['password']).items():
        setattr(user, k, v)

    if password:
        user._password_hash = generate_password_hash(password)

    if 'username' in session:
        session.pop('username')

    db.session.add(user)
    db.session.commit()
    login_user(user, remember=True)
    return user


@USER.route('/user/admin', methods=['GET', 'PUT', 'POST'])
@api_endpoint(auth='Admin', validator=User, html='user/admin_update.html', commit=True, add=True)
def admin_update(username, email=None, full_name=None, password=None, status=None, auth_level=None, user_id=None):
    """
    :param username:   str of the username give my the player
    :param email:      str of the user's email address
    :param full_name:  str of the full name
    :param password:   str of the encrypted password
    :param status:     str of the enum status ['Active', 'Suspended']
    :param auth_level: str of the enum auth_level ['User', 'Demo', 'Superuser', 'Admin']
    :param user_id:    int of the user_id to update
    :return:           User dict of the user updated by admin
    """
    kwargs = function_kwargs(exclude_keys='password')
    if password:
        kwargs['_password_hash'] = generate_password_hash(password)
    user = User.get_or_create(kwargs, username=username)
    return user


@USER.route('/user/array', methods=['GET', 'POST'])
@api_endpoint('Admin')
def get_array(user_ids=None, usernames=None, status=None):
    """
    :param user_ids:  list of int of the user_ids to return
    :param usernames: list of str of the usernames to return
    :param status:    str of the status
    :return:          list of User
    """
    query = User.query

    if user_ids:
        query = query.filter(User.user_id.in_(user_ids))
    if usernames:
        query = query.filter(User.username.in_(usernames))

    if status:
        query = query.filter(User.status == status)

    users = query.all()
    return users
