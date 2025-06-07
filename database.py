from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, Boolean
from flask_login import UserMixin

# Creating the database
class Base(DeclarativeBase):
  pass

# the above just says every class that inherits from the Base will become a table in the database

db = SQLAlchemy(model_class=Base)

# Creating the model for our database to follow
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False) # the equivalent of VARCHAR is String(255) which specify the max number of characters is 255
    map_url: Mapped[str] = mapped_column(nullable=False)
    img_url: Mapped[str] = mapped_column(nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    seats: Mapped[str] = mapped_column(nullable=False)
    coffee_price: Mapped[str] = mapped_column(nullable=False)

    # if you make any changes to the mapped_column, aka add/remove stuff in the parenthesis, make sure to delete the db and run the code again, since the changes won't be applied to the existing db

# Create the user class
class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)