# importing libraries
import re
import os
import dialogflow_v2 as dialogflow
from google.api_core.exceptions import InvalidArgument
from google.oauth2 import service_account
from flask import Flask, render_template, url_for, flash, redirect
import pandas as pd
from werkzeug.utils import secure_filename

# credentials

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ''
DIALOGFLOW_PROJECT_ID = ''
DIALOGFLOW_LANGUAGE_CODE = 'en'
SESSION_ID = '123'

def addIntent(form):
    """Create an intent of the given intent type."""
    intents_client = dialogflow.IntentsClient()

    parent = intents_client.project_agent_path(DIALOGFLOW_PROJECT_ID)
    
    intent = dialogflow.types.Intent(
        display_name=form.intent_name.data)

    response = intents_client.create_intent(parent, intent)

    print('Intent created: {}'.format(response))
    flash('Intent ' + form.intent_name.data + ' added!', 'success')

def testApp(form):

    text_to_be_analyzed = form.phrase_text.data

    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(DIALOGFLOW_PROJECT_ID, SESSION_ID)
    text_input = dialogflow.types.TextInput(text=text_to_be_analyzed, language_code=DIALOGFLOW_LANGUAGE_CODE)
    query_input = dialogflow.types.QueryInput(text=text_input)
    try:
        response = session_client.detect_intent(session=session, query_input=query_input)
    except InvalidArgument:
        raise
    intent = response.query_result.intent.display_name   
    
    flash('Detected Intent: ' + str(intent), 'success')
    c = [i for i in response.query_result.parameters.fields.keys()]
    en = c
    # en = en.join(c)
    flash('Entities Required: ' + str(en), 'success')
    x = []
    for i in response.query_result.parameters.fields.keys():
        x.append(response.query_result.parameters.fields[i].string_value)
    y = x
    # y = y.join(x)
    flash('Detected Entities in Text: ' + str(y), 'success')
    flash('Fulfillment text: {}\n'.format(response.query_result.fulfillment_text), 'success')

def createEntity(form):
    """Create an entity type with the given display name."""
    entity_types_client = dialogflow.EntityTypesClient()

    parent = entity_types_client.project_agent_path(DIALOGFLOW_PROJECT_ID)
    entity_type = dialogflow.types.EntityType(
        display_name=form.entity_class.data, kind=1)

    response = entity_types_client.create_entity_type(parent, entity_type)

    print('Entity type created: \n{}'.format(response))

    flash('Entity Type ' + form.entity_class.data + ' created!', 'success')

def getEntities():
    entity_types_client = dialogflow.EntityTypesClient()

    parent = entity_types_client.project_agent_path(DIALOGFLOW_PROJECT_ID)

    entity_types = entity_types_client.list_entity_types(parent)
    
    entity_names = []

    for entity_type in entity_types:
        entity_names.append(entity_type.display_name)

    return entity_names

def getEntityId(entity_name):
    entity_types_client = dialogflow.EntityTypesClient()
    parent = entity_types_client.project_agent_path(DIALOGFLOW_PROJECT_ID)

    entity_types = entity_types_client.list_entity_types(parent)
    
    entity_names = [
        entity.name for entity in entity_types
        if entity.display_name == entity_name]

    entity_ids = [
        entity_name.split('/')[-1] for entity_name
        in entity_names]

    return entity_ids[0]
    
def addEntity(form):
    entity_types_client = dialogflow.EntityTypesClient()

    # Note: synonyms must be exactly [entity_value] if the
    # entity_type's kind is KIND_LIST
    entity_type_path = entity_types_client.entity_type_path(DIALOGFLOW_PROJECT_ID, getEntityId(form.entity_class.data))
    if form.entity_list.data:
        entity_value = form.entity_list.data
        if form.synonyms.data:
            synonyms = form.synonyms.data.split(',')
        else:
            synonyms = [entity_value]
    
    else:
        f = form.entity_csv.data
        filename = f.filename
        print('filename:', filename)
        file_path = os.path.join('uploads', filename)
        print('filepath:', file_path)
        f.save(file_path)

        df = pd.read_csv(file_path)

        for i in range(len(df)):
            entity_value = df['entity'].loc[i]
            print('Entity:', entity_value)
            synonyms = [i.strip() for i in df['synonym'].loc[i].split(',')]
            print('Synonyms:', synonyms)
            entity = dialogflow.types.EntityType.Entity()
            entity.value = entity_value
            entity.synonyms.extend(synonyms)

            response = entity_types_client.batch_create_entities(
                entity_type_path, [entity])
        flash('Entity Added!', 'success')

    entity_type_path = entity_types_client.entity_type_path(DIALOGFLOW_PROJECT_ID, getEntityId(form.entity_class.data))

    entity = dialogflow.types.EntityType.Entity()
    entity.value = entity_value
    entity.synonyms.extend(synonyms)

    response = entity_types_client.batch_create_entities(
        entity_type_path, [entity])
    
    flash('Entity ' + entity_value + ' Added!', 'success')

    print('Entity created: {}'.format(response))

def getIntents():
    
    intents_client = dialogflow.IntentsClient()

    parent = intents_client.project_agent_path(DIALOGFLOW_PROJECT_ID)

    intents = intents_client.list_intents(parent)

    intent_names = []
    for intent in intents:  
        intent_names.append(intent.display_name)

    return intent_names

def getIntentId(display_name):
    intents_client = dialogflow.IntentsClient()

    parent = intents_client.project_agent_path(DIALOGFLOW_PROJECT_ID)
    intents = intents_client.list_intents(parent)
    intent_names = [
        intent.name for intent in intents
        if intent.display_name == display_name]

    intent_ids = [
        intent_name.split('/')[-1] for intent_name
        in intent_names]

    return intent_ids

def addPhrase(form):
    display_name = form.intent.data
    text = form.phrase_text.data
    x = form.entities.data.split(',')
    # annotation method overall
    project_id = DIALOGFLOW_PROJECT_ID
    intent_id = getIntentId(display_name)[0]

    client = dialogflow.IntentsClient()
    intent_name = client.intent_path(project_id, intent_id)
    intent = client.get_intent(intent_name, intent_view=dialogflow.enums.IntentView.INTENT_VIEW_FULL)
    training_phrases = []
    parts = []

    etype = dict()
    for i in x:
        temp = i.split(':')
        etype[temp[0].strip()] = temp[1].strip()
        
    entities = list(etype.keys())
    entities_for_split = ['('+x+')' for x in entities]

    split = '|'
    split = split.join(entities_for_split)
    split_list = re.split(split, text)

    while None in split_list: split_list.remove(None)

    print(split_list)

    for i in split_list:
        if i in entities:
            part = dialogflow.types.Intent.TrainingPhrase.Part(text=i, user_defined = True, entity_type = '@'+etype[i], alias = re.sub('[^A-Za-z0-9]+', '', etype[i]))
            parts.append(part)
        else:
            part = dialogflow.types.Intent.TrainingPhrase.Part(text=i)
            parts.append(part)


    print(parts)
    training_phrase = dialogflow.types.Intent.TrainingPhrase(parts=parts)
    training_phrases.append(training_phrase)
    intent.training_phrases.extend(training_phrases)
    response  = client.update_intent(intent, language_code='en')
    flash('Training Phrase Added Successfully!', 'success')