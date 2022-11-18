# Utils
# from utils.visualisation import student_progress
from utils.video import youtube
from utils.sendMessage import send_message
# from utils.quiz import quiz_bot
from utils.dialogflowQuery import dialogflow_query
from utils.webSearch import google_search
from utils.organisationInfo import organisationIntroduction

from api.text import sendText
from api.quizButtons import sendQuiz
from api.oneButton import sendOneButton
from api.twoButton import sendTwoButton
from api.threeButton import sendThreeButton

# Extra imports
from pymongo import MongoClient
import datetime
import json
import os
import json
import random
from deep_translator import GoogleTranslator
import langid

import langid
#import requests to make API call
import requests
# import dotenv for loading the environment variables
from dotenv import load_dotenv
# import flask for setting up the web server
from flask import Flask, Response, request
# Extra imports
from pymongo import MongoClient

from api.text import sendText
# from utils.quiz import quiz_bot
from utils.dialogflowQuery import dialogflow_query
# from utils.speech_to_text import speech_to_text
from utils.sendMessage import send_message
from utils.video import youtube
# from utils.visualisation import student_progress
from utils.webSearch import google_search
from utils.TrialFlow import trialFlow
from utils.db import db


load_dotenv()


# creating the Flask object
app = Flask(__name__)

import utils.payment 
#importing youtube Videos 

quiz_time = False


@app.route('/', methods=['POST'])
def reply():
    
    global quiz_time
    message_ = request.form.get('Body')
    print(request.form)
    langId = langid.classify(message_)[0]
    if langId != 'en':
        message = GoogleTranslator(
            source="auto", target="en").translate(message_)
    else:
        message = message_
    response_df = dialogflow_query(message)

    user = db['test'].find_one({'_id': request.form.get('WaId')})

    if user == None and response_df.query_result.intent.display_name != 'Register' and response_df.query_result.intent.display_name != 'Organisation':
        # send button to register
        # sendTwoButton(request.form.get('WaId'), "Welcome to our world of education", "register", "I want to register right now!", "surf",  "I am just here to surf and explore!")
        welcome_text = ["Welcome to our world of education",
                        "It's a better place if you register today!",
                        "Trust me! Registering with us will brighten your future",
                        "Vishal, the business tycoon recommends us, register now!"]
        print(message)
        # print(response_df.query_result.language_code)

        sendTwoButton(request.form.get('WaId'), langId, welcome_text[random.randint(0, 3)], ["register", "roam"], ["Register right now!", "Just exploring!"])
        return ''

    if user == None and (response_df.query_result.intent.display_name == 'Register' or response_df.query_result.intent.display_name == 'Register-Follow'):
        db["test"].insert_one({'_id': request.form.get(
            'WaId'), 'name': '', 'email': '', 'langId': langId})
        sendText(request.form.get('WaId'), langId, response_df.query_result.fulfillment_text)
        return ''

    if user == None and response_df.query_result.intent.display_name == 'Organisation':
        organisationIntroduction(request.form.get('WaId'), langId)
        return ''

    if user == None and response_df.query_result.intent.display_name == 'Organisation - history' or response_df.query_result.intent.display_name == 'Organisation - vision' or response_df.query_result.intent.display_name == 'Organisation - visit':
        sendText(request.form.get('WaId'), langId, response_df.query_result.fulfillment_text)
        return ''

    if user != None and (response_df.query_result.intent.display_name == 'Register' or response_df.query_result.intent.display_name == 'Register-Follow'):
        if user['name'] == '':
            name_ = str(response_df.query_result.output_contexts[0].parameters.fields.get(
                'person.original'))
            name = name_.split("\"")[1]
            db['test'].update_one({'_id': request.form.get('WaId')}, {"$set": {'name': name}})
            sendText(request.form.get('WaId'), user['langId'], response_df.query_result.fulfillment_text)
            return ''

        elif user['email'] == '':
            email_ = str(response_df.query_result.output_contexts[0].parameters.fields.get(
                'email.original'))
            email = email_.split("\"")[1]
            db['test'].update_many({'_id': request.form.get('WaId')}, {"$set": {'email': email.lower(), 'scheduleDone': "false"}})
            sendText(request.form.get('WaId'), user['langId'], response_df.query_result.fulfillment_text)
            return ''

    # if user != None and (response_df.query_result.intent.display_name == 'Register' or response_df.query_result.intent.display_name == 'Register-Follow'):

    # quiz_count = user['quiz_count']
    quiz_count = 100
    print("HELLLLLOCOCOCOCOCO")
    # message = request.form.get('Body').lower()
    if quiz_time and quiz_count == 0:
        quiz_initial(user, quiz_count)
        return ''

    workflow(user, request, response_df)
    return ''


def quiz_initial(user, quiz_count):
    quiz_count = quiz_count + 1
    quiz_bot2(db, 'M1', quiz_count)
    db['test'].update_one({'_id': request.form.get('WaId')}, {"$set": {'quiz_count': quiz_count}})
    print('COUNT ' + str(quiz_count))
    return ''


def quiz_bot2(db, quizID, questionNumber):
    collection = db["course"]
    quiz = collection.find_one({'_id': quizID})
    questionNumberString = str(questionNumber)
    if questionNumber > 0 and questionNumber < 6:
        # send_message(quiz[questionNumberString]['question'], '')
        # options = '\n' + quiz[questionNumberString]['A'] + '\n' + quiz[questionNumberString]['B'] + '\n' + quiz[questionNumberString]['C'] + '\n' + quiz[questionNumberString]['D'] + '\n'
        # send_message(options, '')
        sendQuiz(request.form.get('WaId'), quiz, questionNumberString)

    if questionNumber > 1 and questionNumber < 7:
        questionNumberString = str(questionNumber - 1)
        return quiz[questionNumberString]['answer']
    else:
        return ''


def quiz_chat(user, user_answer):
    global quiz_time
    quiz_count = user['quiz_count']
    quiz_count = quiz_count + 1
    db['test'].update_one({'_id': request.form.get('WaId')}, {"$set": {'quiz_count': quiz_count}})
    print(quiz_count)
    previous_answer = quiz_bot2(db, 'M1', quiz_count)
    if user_answer == previous_answer:
        quiz_marks = user['quizzes']['M1'] + 2
        print(quiz_marks)
        db['test'].update_one({'_id': request.form.get('WaId')}, {"$set": {'quizzes.M1': quiz_marks}})
    if quiz_count == 6 or quiz_count > 6:
        quiz_time = False
        db['test'].update_one({'_id': request.form.get('WaId')}, {"$set": {'quiz_count': 0}})
        sendText(request.form.get('WaId'), 'Your quiz is over!')
        return ''
    else:
        return ''


def workflow(user, request, response_df):
    global quiz_time
    if quiz_time:
        # user = db['test'].find_one({'_id': request.form.get('WaId')})
        quiz_answer = db['course']
        quiz_chat(user, request.form.get('Body'))
        return ''

    if not quiz_time:
        # message = request.form.get('Body').lower() # video on digimon
        # response_df = dialogflow_query(message)
        
        if response_df.query_result.intent.display_name == 'Organisation':
            organisationIntroduction(request.form.get('WaId'), user['langId'])
            return ''
        
        if response_df.query_result.intent.display_name == 'Organisation - history' or response_df.query_result.intent.display_name == 'Organisation - vision' or response_df.query_result.intent.display_name == 'Organisation - visit':
            sendText(request.form.get('WaId'), user['langId'], response_df.query_result.fulfillment_text)
            return ''
        

        if user['scheduleDone'] == 'false':
            sendTwoButton(request.form.get('WaId'), user["langId"], "Why not explore the courses we offer? \n You can also know more about us!", ["courses", "organisation"], ["Explore courses now!", "Know more about us!"])
            return ''

        if response_df.query_result.intent.display_name == 'Videos':
            result_videos = youtube(response_df.query_result.query_text)
            print(result_videos)
            for video in result_videos:
                sendText(request.form.get('WaId'),video['url'] + ' | ' + video['title'])
            return ''

        if response_df.query_result.intent.display_name == 'WebSearch':  # Google JEE datde
            result_search = google_search(response_df.query_result.query_text)
            sendText(request.form.get('WaId'), result_search)

        if response_df.query_result.intent.display_name == 'Parent':
            print(response_df.query_result.parameters)
            picture_url = student_progress(db)
            send_message(
                response_df.query_result.fulfillment_text, picture_url)
            return ''

        else:
            # quiz_bot(db, 'M1')
            now = datetime.datetime.now()
            print(now.year, now.month, now.day,now.hour, now.minute, now.second)
            print(type(now.year), type(now.month), type(now.day),type(now.hour), type(now.minute), type(now.second))
            print(request.form.get('From'))
            # send_message(request.form.get('From'), response_df.query_result.fulfillment_text,'')
            print(response_df.query_result.fulfillment_text)
            print(response_df.query_result.intent.display_name)
            print(request.form)
            sendText(request.form.get('WaId'), user['langId'], response_df.query_result.fulfillment_text)

    return ''


if __name__ == '__main__':
    app.run(debug=False)
