from .auto_register import *


class AutoRegister(object, metaclass=MetaRegister):
    """
        This class is to be subclassed to auto fill a table with values
    """
    # these will be localized to the child subclass upon fill_table in case of multiple uses of AutoRegister
    REGISTERED = {}  # id: class_instance # which means it has the id
    LOOKUP = {}  # {name: id}
    NAME = {} # {id: name}
    ORDER = []  # [class]
    MODELS = {}  # {name: model}

    def __init__(self, id):
        self.id = id

    @classmethod
    def load_table(cls, api_model, id_name, database, unique_columns=None, clear_database=True, printer=None):
        return auto_register_load_table(cls, api_model, id_name, database, unique_columns, clear_database, printer)
