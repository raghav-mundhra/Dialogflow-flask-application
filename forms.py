from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from functions import getEntities, getIntents

class add_intent_form(FlaskForm):
    intent_name = StringField('Intent Name',
                           validators=[DataRequired(), Length(min=2, max=30)])

    submit = SubmitField('Add Intent')


class add_phrase_form(FlaskForm):
    intent = SelectField('Intent Name')
    phrase_text = StringField('Phrases')
    entities = StringField('Enter Entities Present in phrase (comma separated) (format:  `entity_name:entity_type`)')

    submit = SubmitField('Add Phrases')

class test_app_form(FlaskForm):
    phrase_text = StringField('Phrase',
                           validators=[DataRequired()])
    submit = SubmitField('Test App')

class create_entity_form(FlaskForm):
    entity_class = StringField('Entity Type',
                        validators=[DataRequired()])
    submit = SubmitField('Create Entity')

class add_entity_form(FlaskForm):
    entities = getEntities()
    entity_class = SelectField('Entity Type')
    entity_list = StringField('Enter Entity')
    entity_csv = FileField('Upload CSV', validators=[FileAllowed(['csv'])])
    synonyms = StringField('Enter Synonyms for the above Entity (comma separated)')
    submit = SubmitField('Add Entity')