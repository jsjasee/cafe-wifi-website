from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, URLField, BooleanField
from wtforms.validators import DataRequired, URL, InputRequired, ValidationError
# so DataRequired actually checks if the value is None, or empty and raises an error if so,
# but InputRequired only checks if the user typed something in the field, if the user did not type nothing then no error is raised, so even if user typed justs spaces it passes the validator
from database import db, Cafe

class CafeForm(FlaskForm):
    name = StringField('Cafe name', validators=[DataRequired()])
    map_url = URLField("Cafe Location on Google Maps (URL)", validators=[URL()])
    img_url = URLField("Google map image link of the cafe (URL)", validators=[URL()])
    location = StringField('Cafe location', validators=[DataRequired()])
    has_sockets = BooleanField("Sockets Available?") # no need put datarequired here since users can leave this unchecked
    has_toilet = BooleanField("Toilet Available?")
    has_wifi = BooleanField("Wifi Available?")
    can_take_calls = BooleanField("Can take calls?")
    seats = StringField('How many seats are in the cafe? (rough estimate)', validators=[DataRequired()])
    coffee_price = StringField('Price of cheapest coffee', validators=[DataRequired()])
    submit = SubmitField("Submit")

    # WTForms automatically looks for a method named validate_<fieldname>() -> see below def function
    # This is a custom validator for the 'name' field to prevent duplicate cafe names.
    # It runs after the built-in validators like DataRequired().
    # The 'field' argument is the actual form field (e.g., StringField), and its value is accessed with field.data.
    # Do NOT include this in the validators=[] list — WTForms links it by naming convention.

    def validate_name(self, field):
        # note: field is a WTForm object, so to get the actual value need to tap into its data attribute
        cafe_record = db.session.execute(db.select(Cafe).where(Cafe.name == field.data)).scalar()
        if cafe_record:
            raise ValidationError("A cafe with this name already exists.")