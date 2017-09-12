__author__ = 'Ben Christenson'
__date__ = "9/22/15"
import sys
from seaborn.logger import log
from datetime import datetime
import inspect
import json
from flask_login import current_user
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.associationproxy import _AssociationList, _AssociationDict, _AssociationCollection
from seaborn.calling_function import function_defaults
from seaborn.rest.errors import *
from seaborn.timestamp import datetime_to_str


ALCHEMY_TO_PYTHON_TYPE = {'String': 'str',
                          'Integer': 'int',
                          'Float': 'float',
                          'Enum': 'str',
                          'Boolean': 'bool',
                          'DateTime': 'datetime',
                          'Text': 'str',
                          }


def get_ipaddress():
    return ""  # this should return all the ipaddresses from the request


class ApiModel(object):
    """ This is to be paired with a db.Model to subclass """

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @classmethod
    def keys(cls):
        column_order = [col.name for col in cls.__table__.columns if col.name[0] != '_']
        return column_order

    @classmethod
    def _primary_key(cls):
        return [col for col in cls.__table__.columns if col.primary_key][0].name

    def __hash__(self):
        return id(self)
#        return hash(getattr(self,self._primary_key(),None) or id(self))

    @classmethod
    def key_type(cls, key, models=None):
        """
            This will return the type of variable for the keys
        :param models:
        :param key: str of the attribute requesting
        :return: str of the python type
        """
        if key == 'moves':
            pass
        if key in cls.__table__.columns:
            return ALCHEMY_TO_PYTHON_TYPE[repr(cls.__table__.columns[key]).split(',')[1].split('(')[0].strip()]
        elif key in cls.__dict__ and not ':return:' in (cls.__dict__[key].__doc__ or ''):
            for model in models or []:
                name = model.__name__
                if name == key or name == key.title():
                    return name
                if name == key[:-1] or name == key.title()[:-1]:
                    return 'list of %s' % name
            return key.title()
        elif key in cls.__dict__:
            assert cls.__dict__[key].__doc__, "Missing doc for %s in model %s" % (key, cls.__name__)
            return_desc = cls.__dict__[key].__doc__.split(':return:')[1].lstrip()
            if return_desc.startswith('list of'):
                return ' '.join(return_desc.split()[:3])
            return return_desc.split()[0]
        raise AttributeError('Could not find var type for key reference "%s" in object "%s"' % (key, cls.__name__))

    def __repr__(self):
        return '< %s: %s >' % (self.__class__.__name__, getattr(self, self.keys()[0]))

    def __iter__(self):
        return iter([getattr(self, k) for k in self.keys() if k[0] != '_'])

    def items(self):
        return [(k, getattr(self, k)) for k in self.keys()]

    def iteritems(self):
        return iter(self.items())

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return json.dumps(self.serialize())

    def serial(self, key, obj):
        if isinstance(obj, datetime):
            return datetime_to_str(obj)
        if obj is None and self.key_type(key) == 'str':
            return ''
        if isinstance(obj, ApiModel):
            return obj.serialize()
        if isinstance(obj, (dict, _AssociationDict)):
            return {k: self.serial(key, v) for k, v in obj.items()}
        if isinstance(obj, (list, _AssociationList)):
            return [self.serial(key, o) for o in obj]
        return obj

    def serialize(self):
        from collections import OrderedDict
        return OrderedDict([(k, self.serial(k, v)) for k, v in self.items() if v is not None])

    @classmethod
    def required_args(cls):
        func_args = inspect.getargspec(cls.__init__).args
        _required_args = func_args[:len(func_args) - len(function_defaults(cls.__init__))]
        cls.required_args = lambda cls_: _required_args
        return _required_args

    @classmethod
    def get_or_create(cls, kwargs=None, **filtered_arguments):
        """
        This will retrieve the item from the database for the parameters that are not none and are required by __init__
        If it is not in the database then it will create it.
        If it is in the database then it will update it with values that are not None
        :param kwargs:             dict of the parameters that don't have to be unique
        :param filtered_arguments: dict of the parameters that need to be unique
        :return:                   obj of the model created or updated
        """
        instance = cls.query.filter_by(**filtered_arguments).first()
        if not instance:
            kwargs = kwargs or {}
            kwargs.update(filtered_arguments)
            instance = cls(**kwargs)
        elif kwargs:
            for k in kwargs:  # note sqlalchemy will lose changes to __dict__.update
                try:
                    if kwargs[k] is not None and kwargs[k] != getattr(instance, k, kwargs[k]):
                        setattr(instance, k, kwargs[k])
                except Exception as e:
                    setattr(instance, k, kwargs[k])

        return instance

    @classmethod
    def get(cls, id_, joined_load=None):
        """
        This will return the game if access is granted
        :param id_:          int of the unique id
        :param joined_load:  list of str of member relations to eager load
        :return:             obj of the model
        """
        query = cls.query
        for child in joined_load or []:  # todo replace this with a single join call
            query = query.options(joinedload(child))

        obj = query.get(id_)

        if obj is None:
            raise NotFoundException('ID: %s does not exist' % id_)
        if getattr(obj, 'user_id', current_user.user_id) != current_user.user_id and \
                not current_user.is_auth_level('Superuser'):
            raise NotAuthorizedException('User is not the owner of this %s' % cls.__name__)
        return obj

