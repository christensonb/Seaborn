from settings.global_import import *

log.trace("Importing endpoint test.models")


class Echo(db.Model, ApiModel):
    __tablename__ = "echo"
    echo_key = db.Column(db.String, primary_key=True)
    echo_value = db.Column(db.String)
