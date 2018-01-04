import platform
from seaborn import *
from seaborn import relative_path, os

if platform.platform() == "Linux-3.13.0-106-generic-x86_64-with-debian-jessie-sid":  # this is my AWS linux box
    Config = ProductionConfig
else:
    Config = LocalDebugConfig

flask_folder = os.path.dirname(relative_path())
configuration = LocalDebugConfig(domain='demo.BenChristenson.com',
                                 name='Demo',
                                 flask_folder=flask_folder,
                                 data_folder=os.path.dirname(flask_folder),
                                 database_source='sqlite')
