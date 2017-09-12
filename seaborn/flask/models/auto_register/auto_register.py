__author__ = 'Ben Christenson'
__date__ = "9/22/15"
from seaborn.logger import log
import inspect
from seaborn.flask.models.models import ApiModel


def auto_register_load_table(cls, api_model, id_name, database, unique_columns=None, clear_database=True, printer=None):
    """
    This will create an update all columns in the class_model for each subclass
    It will also instantiate each of the of the classes and assign their id and ave it in registered

    I have moved this out of the class to mitigate teh python 2.7 vs. 3.5 issue

    :param api_model:      ApiModel class of the table to put the the values in.
    :param id_name:        str of the name of the unique id for this class
    :param database:       obj of Flask Database Object
    :param unique_columns: list of str values of values that must be unique
    :param clear_database: bool if true will delete records not in this list
    :param log:            Logger if applied will log for debug purposes
    :return:               None
    """

    cls.REGISTERED = {}
    cls.LOOKUP = {}
    cls.ORDER = []
    cls.MODELS = {}

    if printer is None:
        def printer(text): pass

    assert issubclass(api_model, ApiModel), 'api_model must be a subclass of ApiModel'
    printer("Starting auto register of base class: %s to api model: %s for id: %s" % (
        cls.__name__, api_model.__name__, id_name))

    unique_columns = [unique_columns] if isinstance(unique_columns, str) else unique_columns or []
    update_columns = [col.name for col in api_model.__table__.columns
                      if col.name not in unique_columns and col.name != id_name]

    printer("Unique Columns: %s" % unique_columns)
    printer("Update Columns: %s" % update_columns)

    def get_value(class_, column):
        try:
            ret = getattr(class_, column, None)
            return ret() if getattr(ret, '__call__', None) else ret
        except Exception as e:
            raise e.__class__("Failed to get value for column: '%s'  because of %s" % (column, e.args))

    e = None
    for class_ in MetaRegister.ORDER:
        if issubclass(class_, cls) and class_ is not cls:
            try:
                if "raise NotImplmented" in inspect.getsource(class_):
                    continue

                printer("\n" * 5 + "%s: Registering sub class: %s" % (str(len(cls.ORDER)).rjust(5),
                                                                      class_.__name__))
                cls.ORDER.append(class_)
                unique_kwargs = {column: get_value(class_, column) for column in unique_columns}
                update_kwargs = {column: get_value(class_, column) for column in update_columns}

                printer("\n" + " " * 10 + "with unique kwargs: %s" % unique_kwargs)
                printer("\n" + " " * 10 + "with update kwargs: %s" % update_kwargs)

                model = api_model.get_or_create(update_kwargs, **unique_kwargs)
                database.session.add(model)
                cls.MODELS[class_.__name__] = model
            except Exception as e:
                log.error("Exception with class " + class_.__name__.ljust(15) + " of: " + str(e))

    printer("\n" * 5 + "Starting commiting to the database" + "\n" * 5)

    if cls.MODELS.values():
        database.session.commit()
    else:
        log.error("Failed to find any models to load into the table")
        return

    class_dict = {class_.__name__: class_ for class_ in MetaRegister.ORDER}
    for name, model in cls.MODELS.items():
        id_ = getattr(model, id_name)
        cls.REGISTERED[id_] = class_dict[name](id_)
        cls.LOOKUP[name] = id_
        cls.NAME[id_] = name
        printer("Class: %s was registered to %s: %s" % (name.ljust(15), id_name, id_))

    if (clear_database and e is None):
        id = getattr(api_model, id_name)
        models = api_model.query.filter(id.in_(cls.REGISTERED.keys())).all()
        if models:
            [database.session.delete(model) for model in models]
            database.session.commit()
    printer("Finished Registering %s entries into %s" % (api_model.query.count(), api_model.__name__))


class MetaRegister(type):
    ORDER = []

    def __new__(cls, name, bases, attrs):
        """ :param name: str of the class name
            :param bases: tuple of the base classes
            :param attrs: obj of attributes defined for the class
        """
        new_cls = type.__new__(cls, name, bases, attrs)
        cls.ORDER.append(new_cls)
        return new_cls
