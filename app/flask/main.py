import os

from flask import Flask
from dataclasses import fields
#from domain.testform.dataclass import MyDataClass
from testform.dataclass import MyDataClass

app = Flask(__name__)



@app.route("/")
def hello_world():
    """Example Hello World route."""
    name = os.environ.get("NAME", "World")
    return f"Hello {name}! Dataclass: {MyDataClass.__name__}; fields: {fields(MyDataClass)}"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8081)))
