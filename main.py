from flask import Flask, render_template, url_for, flash, redirect
from forms import add_intent_form, add_phrase_form, add_entity_form, test_app_form, create_entity_form
from functions import addIntent, testApp, createEntity, getEntities, addEntity, getIntents, addPhrase
import warnings
import os

warnings.filterwarnings("ignore")


app = Flask(__name__)
app.config['SECRET_KEY'] = '886cf2b74ac16acb81cad9ec489221fe'
app.config['UPLOAD_FOLDER'] = 'uploads'


@app.route("/",  methods=['GET', 'POST'])
@app.route("/addIntent", methods=['GET', 'POST'])
def add_intent():
    form = add_intent_form()
    if form.validate_on_submit():
        addIntent(form)
    return render_template('add_intent.html', title='Add Intent', form=form, intent_data = getIntents())

@app.route("/addPhrase", methods=['GET', 'POST'])
def add_phrase():
    form = add_phrase_form()
    form.intent.choices = [(x,x) for x in getIntents()]
    if form.validate_on_submit():
        addPhrase(form)
    return render_template('add_phrase.html', title='Add Training Phrases', form=form)

@app.route("/createEntity", methods=['GET', 'POST'])
def create_entity():
    form = create_entity_form()
    if form.validate_on_submit():
        createEntity(form)
    return render_template('create_entity.html', title='Create Entity', form=form, intent_data = getEntities())

@app.route("/testApp", methods=['GET', 'POST'])
def test_app():
    print('test app called')
    form = test_app_form()
    if form.validate_on_submit():
        testApp(form)
    return render_template('test_app.html', title='Test Chat Bot', form=form)

@app.route("/addEntity", methods=['GET', 'POST'])
def add_entity():
    form = add_entity_form()
    form.entity_class.choices = [(x,x) for x in getEntities()]
    if form.validate_on_submit():
        addEntity(form)
    return render_template('add_entity.html', title='Add Entities', form=form)

if __name__ == '__main__':
    port = int(os.getenv('PORT',80))    
    app.run(debug=True,port = port,host = '0.0.0.0')
