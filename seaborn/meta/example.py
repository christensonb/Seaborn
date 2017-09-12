class MetaRegister(type):
    ORDER = []

    def __new__(mcs, name, parents, dct):
        print ("Registering Class")
        new_cls = super(MetaRegister, mcs).__new__(mcs, name, parents, dct)
        new_cls.__name__ = name
        mcs.ORDER.append(new_cls)
        return new_cls


class A(object, metaclass=MetaRegister):
    def __init__(self, hello='world'):
        self.hello = hello


class B(A):
    def __init__(self, hello='cruel world'):
        super(B, self).__init__(hello)


for i, class_ in enumerate(MetaRegister.ORDER):
    print("%s: Class - %s    Parent - %s" % (i, class_.__name__, class_.__class__.__name__))

assert MetaRegister.ORDER[0] is A
