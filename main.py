# Utils
from utils.gradeReport import studentProgress
from utils.video import youtube
from utils.dialogflowQuery import dialogflow_query
from utils.webSearch import google_search
from utils.chaboSearch import chabo_search
from utils.organisationInfo import organisationIntroduction
from utils.dialogflowQuery import dialogflow_query
from utils.db import db
from utils.schedule import getTimeSlot
from utils.schedule import bookTimeSlot
from utils.reschedule import rescheduleAppointment
from utils.checkProfile import checkProfile
from utils.quizPicture import getQuizPicture
from utils.receipt import get_receipt
from utils.imageText import imageToText
from utils.audioText import speechToText

from api.text import sendText
from api.oneButton import sendOneButton
from api.twoButton import sendTwoButton
from api.threeButton import sendThreeButton
from api.list import sendList
from api.courseraProfile import getCourseraProfile
from api.quizTemplate import sendQuizQuestion
from api.downloadMedia import getMedia
from api.catalog import sendCatalog
from api.promotion import sendPromotion
from api.help import sendHelp
from api.uploadMedia import uploadMedia
from api.sendYoutube import sendTemplateForYoutube
from api.media import sendMedia
from api.downloadMedia import getMedia

# Extra imports
import pymongo as pymongo
import os
import json
import random
from deep_translator import GoogleTranslator
import langid
from datetime import date, timedelta, datetime
import requests
from dotenv import load_dotenv
from flask import *
from pymongo import MongoClient
import io 
import base64
from PIL import Image
import re
import emoji
from math import sin, cos, sqrt, atan2, radians

load_dotenv()

# For payment
import razorpay
razorpay_key = os.environ['RAZORPAY_KEY_ID']
razorpay_secret = os.environ['RAZORPAY_KEY_SECRET']

# creating the Flask object
app = Flask(__name__)
app.secret_key = b'delph@!#78d%'


@app.route('/', methods=['POST'])
def reply():
    request_data = json.loads(request.data)
    print(request_data)
    
    if "businessId" not in request_data:
        return ''
    message_ = ''
    
    #   #___Testing____
    # request_data = {
    #     'from': request.form.get('WaId'),
    #     'sessionId': '7575757575757',
    #     'message': {
    #         'text': {
    #             'body':request.form.get('Body')
    #         },
    #         'type': 'text'
    #     }
        
    # }
    # # ___________
    
    if request_data['from'] == '919870613280':
        
        print("Admin time")
        conditionTitle = ((request_data['message']['text']['body']).split(",")[0]).strip().lower()
        
        if conditionTitle == 'promotion':
            courseName_ = (request_data['message']['text']['body']).split(",")[1]
            courseLink_ = (request_data['message']['text']['body']).split(",")[2]
            for document in db['test'].find({}):
                sendPromotion(document.get("_id"), document.get("langId"), courseName_, courseLink_)
            return ''

        
        if conditionTitle == 'ngrok':
            ngrokSet = ((request_data['message']['text']['body']).split(",")[1]).lower()
            if ngrokSet == 'set':
                ngrokLink = ((request_data['message']['text']['body']).split(",")[2]).strip()
                db['config'].update_one({'_id': 'ngrok'}, { "$set": {'ngrokLink': ngrokLink}})
                sendText('919870613280', 'en', "ngrok is set", request_data['sessionId'])
                return ''
            
            if ngrokSet == 'clear' or ngrokSet != 'set':
                db['config'].update_one({'_id': 'ngrok'}, { "$set": {'ngrokLink': ''}})
                sendText('919870613280', 'en', "ngrok is cleared", request_data['sessionId'])
                return ''
        
        if conditionTitle == 'class-absent':
            absentStudent = ((request_data['message']['text']['body']).split(",")[1]).strip()
            absentUserData = db['test'].find_one({'_id': absentStudent})
            sendText(absentStudent, absentUserData['langId'], 'You missed your class today! No worries, you can access the recordings and notes by texting *I need resources*!', request_data['sessionId'])
            return ''
        
        if conditionTitle == 'class-start':
            courseName_ = (((request_data['message']['text']['body']).split(",")[1]).strip()).lower()

            # for document in db['test'].find({'$and':[{'courses.courseId':courseName_}, {'courses.courseFeedback': {"$lt": d}}]}):
            for document in db['test'].find({'courses.courseId':courseName_}):
                # if document.get('course') is not None or len(document.get('course')) != 0:
                sendText(document.get('_id'), document.get("langId"), 'The class for the course - ' + courseName_+' is starting in a few minutes! Here is the link for today!' , request_data['sessionId'])
                sendText(document.get('_id'), 'en', 'https://meet.google.com/kkr-ndxk-kdg' ,  request_data['sessionId'])
                
            return ''
        
        return ''
    
    if request_data["message"]["type"] == "order":
        userCatalog = db['test'].find_one({'_id':  request_data['from']})
        if userCatalog is not None:
            WaId = request_data["from"]
            if len(request_data["message"]["order"]["product_items"]) < 1:
                print('No Course Selected')
                sendText(WaId,'en',"No Course Selected", request_data['sessionId'])
                pass
            else:
                # fetch coursera id of current user
                userInfo = db['test'].find_one({'_id': WaId})
                print(userInfo)
                if userInfo["courseraId"] == '':
                    print('Coursera Id Not There')
                    mediaIdProfile, mediaTypeProfile = uploadMedia('courseraProfileHelp.jpg', 'static/helpMedia/courseraProfileHelp.jpg', 'jpg')
                    sendText(WaId, userInfo['langId'], "It looks like you haven't submitted a profile URL link.🤔 Please make sure that you submit the Coursera Profile link that is displayed when you visit your profile in our portal. To submit the link, just *text* it here, I will update it right away! For reference, please consider the image attached!\n Just copy and paste your profile URL here in our chat, for example, *Here is my profile ID https://www.coursera.org/user/4142eae2bd3c41fbec7d346083fa4f13*", request_data['sessionId'])
                    sendMedia(WaId, mediaIdProfile, mediaTypeProfile, request_data['sessionId'])
                    
                    # send message to add coursera id of the user
                    pass
                else:
                    # Get Requested Courses from cart
                    requestedCourses = request_data["message"]["order"]["product_items"]
                    alreadyRegisteredCourses = [x["courseId"] for x in userInfo["courses"]]
                    print("already registered", alreadyRegisteredCourses)
                    alreadyRegisteredFlag = 0

                    courseDetails = []
                    totalFees = 0

                    for item in requestedCourses:
                        retail_id = item["product_retailer_id"]
                        print(retail_id)

                        courseData = db['course'].find_one({"catalogProductId": retail_id})
                        print("course data")
                        print(courseData)

                        # check if alredy paid or not
                        if courseData["_id"] in alreadyRegisteredCourses:
                            alreadyRegisteredFlag = 1
                            break
                        else:
                            today = date.today()

                            if courseData["courseType"] == "static":
                                courseTemp = {
                                    "courseId": courseData["_id"],
                                    "courseType": "static",
                                    "courseFees": courseData["courseFees"],
                                    "courseStartDate": str(today),
                                    "courseEndDate": str(today + timedelta(weeks=courseData["courseDuration"])),
                                    "quantity": item["quantity"],
                                    "courseLink": courseData["courseLink"]
                                }
                            else:
                                courseTemp = {
                                    "courseId": courseData["_id"],
                                    "courseType": "dynamic",
                                    "courseFees": courseData["courseFees"],
                                    "courseStartDate": courseData["courseStart"],
                                    "courseEndDate": courseData["courseEnd"],
                                    "quantity": item["quantity"],
                                    "courseLink": courseData["courseLink"]
                                }
                            courseDetails.append(courseTemp)
                            totalFees += courseData["courseFees"]

                    print("Course Details")
                    print(courseDetails)


                    if alreadyRegisteredFlag == 1:
                        # course already registered message to user
                        print('course already registered message to user')
                        sendText(WaId,userInfo['langId'],"Course(s) already registered! Why not explore some more courses? 😋", request_data['sessionId'])
                        sendCatalog(request_data['from'],userInfo['langId'],request_data['sessionId'])
                    else:
                        # send payment link
                        sendText(WaId,'en',"https://vikings.onrender.com//register-for-course/"+WaId, request_data['sessionId'])
                        cartFlag = db["cart"].find_one({'_id': WaId})
                        if cartFlag is not None:
                            db["cart"].delete_one({'_id': WaId})

                        db['cart'].insert_one({
                            '_id': WaId,
                            'courseDetails': courseDetails,
                            'totalFees': totalFees
                        })
                        print("finally the end")
            return ''
        else: 
            sendText(request_data['from'], 'en',"You need to register first to buy our courses! Do not worry! It won't take much time!⚡ ", request_data['sessionId'])
            sendTwoButton( request_data['from'], 'en', "Register right now! It will be the best decision for a brighter future! 🌎", ["register", "roam"], ["Register right now!", "Just exploring!"], request_data['sessionId'])
            return ''
    
    
    if 'image' in request_data['message']:
        ngrok = db['config'].find_one({'_id':  'ngrok'})
        if ngrok['ngrokLink'] == '':
            sendText(request_data['from'],'en',"Bug 🐛 \n We do not support these types on Render Server!", request_data['sessionId'])
            return ''
        else:
            print('Image detected with ngrok link set')
            imageToText(request_data['message']['image']['id'], request_data['from'], 'en', request_data['sessionId'])
        
        return ''
    
    elif request_data["message"]["type"] == "audio":
        ngrok = db['config'].find_one({'_id':  'ngrok'})
        if ngrok['ngrokLink'] == '':
            sendText(request_data['from'],'en',"Bug 🐛 \n We do not support these types on Render Server!", request_data['sessionId'])
            return ''
        else:
            print('Audio detected with ngrok link set')
            speechToText(request_data['message']['audio']['id'], request_data['from'], 'en', request_data['sessionId'])
        
        return ''

    elif request_data["message"]["type"] == "location":
        R = 6373.0

        lat1 = radians(float(request_data["message"]["location"]["latitude"]))
        lon1 = radians(float(request_data["message"]["location"]["longitude"]))
        lat2 = radians(18.9437914)
        lon2 = radians(72.8224314)

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c

        print("Distance Result:", distance)
        mapToFollow = 'https://www.google.com/maps/dir/'+str(request_data["message"]["location"]["latitude"])+','+str(request_data["message"]["location"]["longitude"])+'/Marine+Lines,+Mumbai,+Maharashtra/@18.9437914,72.8224314,15z/'

        sendText(request_data['from'], 'en', 'Want to visit our office? You still seem far! Currently you are '+str(distance)+' kilometres far! Here is a guide to reach us!🌏', request_data['sessionId'])
        sendText(request_data['from'], 'en', mapToFollow, request_data['sessionId'])
        return ''
    
    elif request_data["message"]["type"] == "text":
        message_ = request_data['message']['text']['body']

    elif request_data["message"]["type"] == "interactive":
        if 'list_reply' in request_data['message']['interactive']:
            message_ = request_data['message']['interactive']['list_reply']['id']
    
        elif 'button_reply' in request_data['message']['interactive']:
            message_ = request_data['message']['interactive']['button_reply']['id']
        
    elif request_data["message"]["type"] == "button":
        message_ = request_data['message']['button']['payload']
        
    else:
        sendText(request_data['from'], 'en', "Sorry! We do not support this message type yet!", request_data['sessionId'])
        return ''
    
    message_ = emoji.replace_emoji(message_, replace="")
    
    if (len(message_) == 0):
        sendText(request_data['from'], 'en', "🤔😄", request_data['sessionId']) 
        return ''
    
    # isEmoji = dialogflow_query(message_)
    # if isEmoji.query_result.intent.display_name == 'Emoji handling - Activity' or isEmoji.query_result.intent.display_name == 'Emoji handling - Animals & Nature' or isEmoji.query_result.intent.display_name == 'Emoji handling - Flags' or isEmoji.query_result.intent.display_name == 'Emoji handling - Food & Drink' or isEmoji.query_result.intent.display_name == 'Emoji handling - Objects' or isEmoji.query_result.intent.display_name == 'Emoji handling - Smileys & People' or isEmoji.query_result.intent.display_name == 'Emoji handling - Symbols' or isEmoji.query_result.intent.display_name == 'Emoji handling - Travel & Places':
    #     user_ = db['test'].find_one({'_id':  request_data['from']})
    #     sendText(request_data['from'], user_['langId'], isEmoji.query_result.fulfillment_text, request_data['sessionId']) 
    #     return ''  
    
    langId = langid.classify(message_)[0]
    if langId != 'en':
        message = GoogleTranslator(
            source="auto", target="en").translate(message_)
    else:
        message = message_
    response_df = dialogflow_query(message)

    user = db['test'].find_one({'_id':  request_data['from']})

    if user == None and response_df.query_result.intent.display_name != 'Register' and response_df.query_result.intent.display_name != 'Organisation':
        
        welcome_text = ["Hey I am Chabo! Welcome to our world of education! 🎓 Register yourself now!",
                        "Hey I am Chabo! It's a better place if you register today! 😁",
                        "Hey I am Chabo! Trust me! Registering with us will brighten your future 🌠",
                        "Hey I am Chabo! Register now for an ocean of knowledge and skills! 🌊"]
        print(message)
        

        sendTwoButton( request_data['from'], langId, welcome_text[random.randint(0, 3)], ["register-now-none", "roam-now-none"], ["Register right now!", "Just exploring!"], request_data['sessionId'])
        return ''

    if (user == None and response_df.query_result.intent.display_name == 'Register') or (user == None and message == "register-now-none"):
        
        db["test"].insert_one({'_id': request_data['from'], 'name': '', 'email': '', 'langId': langId, 'courses': [], 'courseraId': '', 'offersAvailed': [], 'UNIT-TESTING': '', 'quizBusy': 'false', 'resultBusy': { 'busy':'false', 'user':''}, 'resource': 'false' })
        sendText(request_data['from'], langId,response_df.query_result.fulfillment_text, request_data['sessionId'])
            
        return ''

    if (user == None and response_df.query_result.intent.display_name == 'Organisation') or (user == None and message == "roam-now-none"):
        organisationIntroduction( request_data['from'], langId, request_data['sessionId'])
        return ''

    if (user == None and (response_df.query_result.intent.display_name == 'Organisation - history' or response_df.query_result.intent.display_name == 'Organisation - vision' or response_df.query_result.intent.display_name == 'Organisation - visit')) or message in ["org-history", "org-vision", "org-contact"] :
        if message == "org-contact":
            sendText(request_data['from'], langId, "If you are a learner and need help, please visit our *Learner Help Center* at Mumbai to find troubleshooting and FAQs or contact our *Learner Support team*! Why not try scheduling an appointment with one of our counselor? Try texting *'Schedule an appointment'* in the chat! 📞", request_data['sessionId'])
            return ''
        if message == "org-history":
            sendText(request_data['from'], langId, "Coursera was founded in 2012 by Stanford University computer science professors Andrew Ng and Daphne Koller. Ng and Koller started offering their Stanford courses online in fall 2011, and soon after left Stanford to launch Coursera. What a journey! 🛣️", request_data['sessionId'])
            return ''
        if message == "org-vision":
            sendText(request_data['from'], langId, "We believe learning is the source of human progress. It has the power to transform our world from illness to health, from poverty to prosperity, from conflict to peace. It has the power to transform our lives for ourselves, for our families,for our communities. 🌟", request_data['sessionId'])
            return ''
            
        else:        
            sendText(request_data['from'], langId, response_df.query_result.fulfillment_text, request_data['sessionId'])
            return ''


    if (user != None and (response_df.query_result.intent.display_name == 'Register - name' or response_df.query_result.intent.display_name == 'Register - name - email') and (user['name'] == '' or user['email'] == '')) or (user['name'] == '' or user['email'] == '') or (message == 'Yes-nme-nne' or message == 'No-nme-nne'):
        print(response_df.query_result.intent.display_name)
            
        if user['name'] == '' or message == 'Yes-nme-nne' or message == 'No-nme-nne':
            name_ = ''
            if response_df.query_result.intent.display_name == 'Register - name':
                print(response_df.query_result.parameters.fields.get("person").struct_value.fields.get("name"))
                name_ = str(response_df.query_result.parameters.fields.get("person").struct_value.fields.get("name"))
            name = ''
            intentOutput = ''
            if (name_ is not None and response_df.query_result.intent.display_name == 'Register - name') or message == 'Yes-nme-nne':
                if response_df.query_result.intent.display_name == 'Register - name':
                    name = name_.split("\"")[1]
                    intentOutput = response_df.query_result.fulfillment_text
                    db['test'].update_one({'_id': request_data['from']}, { "$set": {'name': name}})
                else:
                    intentOutput = 'Name Received'
                
                updatedUser_ = db['test'].find_one({'_id': request_data['from']})
                if updatedUser_['name'] == '':
                    sendText(request_data['from'],user['langId'], response_df.query_result.fulfillment_text, request_data['sessionId'])
                    return ''
                elif (response_df.query_result.fulfillment_text == 'Name Received' or intentOutput == 'Name Received') and updatedUser_['email'] == '': 
                    sendText(request_data['from'],user['langId'],"Please send me your email address!",request_data['sessionId'])
                    return ''
                elif (response_df.query_result.fulfillment_text == 'Name Received' or intentOutput == 'Name Received') and updatedUser_['email'] != '': 
                    sendText(request_data['from'],user['langId'], "You are all set!", request_data['sessionId'])
                    sendHelp(request_data['from'],user['langId'],request_data['sessionId'])
                    sendCatalog(request_data['from'],user['langId'],request_data['sessionId'])
                    return ''
            elif message == 'No-nme-nne':
                db['test'].update_one({'_id': request_data['from']}, { "$set": {'name': ''}})
                sendText(request_data['from'],user['langId'], "Please state your name for the registration!", request_data['sessionId'])
                return ''
            else:
                name = message
                intentOutput = 'Name Received'
                db['test'].update_one({'_id': request_data['from']}, { "$set": {'name': name}})
                sendTwoButton(request_data['from'], user['langId'], "Is this your confirmed name?", ["Yes-nme-nne", "No-nme-nne"], ["Yes", "No"], request_data['sessionId'])
                return''
            
            return ''

        elif user['email'] == '':
            # email_ = str(response_df.query_result.output_contexts.parameters.fields.get('email.original'))
            
            # print(response_df.query_result)
            print(response_df.query_result.parameters.fields.get("email"))
            email_ = str(response_df.query_result.parameters.fields.get("email"))
            email = ''
            intentOutput = ''
            if email_ is not None and response_df.query_result.intent.display_name == 'Register - name - email':
                email = email_.split("\"")[1]
                intentOutput = response_df.query_result.fulfillment_text
            else:
                emailTemp = re.findall(r'[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+', message)
                if len(emailTemp) == 0:
                    sendText(request_data['from'],user['langId'], "Please send a valid email address!", request_data['sessionId'])
                    return ''
                else:
                    email = emailTemp[0]
                    intentOutput = 'Email Received'
            db['test'].update_one({'_id': request_data['from']}, {"$set": {'email': email.lower()}})
            updatedUser_ = db['test'].find_one({'_id': request_data['from']})
            if updatedUser_['email'] == '':
                sendText(request_data['from'],user['langId'], response_df.query_result.fulfillment_text, request_data['sessionId'])
                return ''
            elif (response_df.query_result.fulfillment_text == 'Email Received' or intentOutput == 'Email Received') and updatedUser_['name'] == '': 
                sendText(request_data['from'],user['langId'],"Please send me your name!",request_data['sessionId'])
                return ''
            elif (response_df.query_result.fulfillment_text == 'Email Received' or intentOutput == 'Email Received') and updatedUser_['name'] != '': 
                sendText(request_data['from'],user['langId'], "You are all set!", request_data['sessionId'])
                sendHelp(request_data['from'],user['langId'],request_data['sessionId'])
                sendCatalog(request_data['from'],user['langId'],request_data['sessionId'])
                return ''




    workflow(user, request_data, response_df, langId, message)
    return ''


def workflow(user, request_data, response_df, langId, message):
    print(response_df.query_result.intent.display_name)
    
    if 'https://www.coursera.org/user/' in message:
        courseraUrl = re.findall(r'[A-Za-z0-9\b]?https://www.coursera.org/user/[A-Za-z0-9]*', message)
        print(courseraUrl[0])
        checkProfile(request_data['from'], user['langId'], courseraUrl[0], request_data['sessionId'])
        return ''
    
    if "chabo" in message.lower(): 
        print(message)
        query = re.sub("[^\S\n\t]*chabo[o]*[.,!?]*[^\S\n\t]*", "", message.lower())
        chabo_think = [
            'Chabo here!👾 Awesome question! Give me a minute!',
            'Chabo needs some time to process such a great thought! 🤖',
            'Let Chabo think about it! 👾',
            "It's Chabo! Sending what I found in a minute! 🤖"
        ]
        sendText(request_data['from'], langId, chabo_think[random.randint(0, 3)], request_data['sessionId'])
        result_search = chabo_search(query)
        print(result_search)
        sendText(request_data['from'], langId, result_search, request_data['sessionId'])
        return ''
    
    if response_df.query_result.intent.display_name == "HelpCommands":
        sendHelp(request_data['from'],user['langId'],request_data['sessionId'])
        return ''
    
    if response_df.query_result.intent.display_name == 'Catalog':
        sendCatalog(request_data['from'],user['langId'],request_data['sessionId'])
        return ''

    if response_df.query_result.intent.display_name == 'Organisation':
        organisationIntroduction(request_data['from'], user['langId'], request_data['sessionId'])
        return ''
    
    if (response_df.query_result.intent.display_name == 'Organisation - history' or response_df.query_result.intent.display_name == 'Organisation - vision' or response_df.query_result.intent.display_name == 'Organisation - visit') or message in ["org-history", "org-vision", "org-contact"] :
        if message == "org-contact":
            sendText(request_data['from'], langId, "If you are a learner and need help, please visit our *Learner Help Center* at Mumbai to find troubleshooting and FAQs or contact our *Learner Support team*! Why not try scheduling an appointment with one of our counselor? Try texting *'Schedule an appointment'* in the chat! 📞", request_data['sessionId'])
            return ''
        if message == "org-history":
            sendText(request_data['from'], langId, "Coursera was founded in 2012 by Stanford University computer science professors Andrew Ng and Daphne Koller. Ng and Koller started offering their Stanford courses online in fall 2011, and soon after left Stanford to launch Coursera. What a journey! 🛣️", request_data['sessionId'])
            return ''
        if message == "org-vision":
            sendText(request_data['from'], langId, "We believe learning is the source of human progress. It has the power to transform our world from illness to health, from poverty to prosperity, from conflict to peace. It has the power to transform our lives for ourselves, for our families,for our communities. 🌟", request_data['sessionId'])
            return ''
            
        else:        
            sendText(request_data['from'], langId, response_df.query_result.fulfillment_text, request_data['sessionId'])
            return ''
    
    if response_df.query_result.intent.display_name == 'Schedule':
        timeSlots = getTimeSlot()
        print(timeSlots)
        tagTimeSlots = []
        for timeSlot in timeSlots:
            tagTimeSlots.append(timeSlot+'-tme')
        sendList(request_data['from'], user["langId"], "Please choose your preferred time for tomorrow!🕓", "Free slots tomorrow!", tagTimeSlots, timeSlots, None, True, request_data['sessionId'])
        return ''
    
    if response_df.query_result.intent.display_name == 'Schedule - time' or '-tme' in message:
        # timeSlot_ = ''
        # timeSlots = getTimeSlot()
        # if 'list_reply' in request_data['message']['interactive']:
        #     if (request_data['message']['interactive']['list_reply']['id']).startswith('time-'):
        #         timeSlot_ = request_data['message']['interactive']['list_reply']['id']
        #         bookTimeSlot(timeSlot_, request_data['from'], user['langId'], request_data['sessionId'])
        #         return ''
        # elif message in timeSlots:
        timeSlot_ = message.split("-")[0]
        bookTimeSlot(timeSlot_, request_data['from'], user['langId'], request_data['sessionId'])
        return ''
        

    
    if (response_df.query_result.intent.display_name == 'Schedule - time - yes' or response_df.query_result.intent.display_name == 'Schedule - time - no') or message.startswith('reschedule-'):
        wantedTime = ''
        intentNeeded = ''
        desiredTime_ = str(response_df.query_result.output_contexts[0].parameters.fields.get('time.original'))
        if desiredTime_ is not None:
            desiredTime = desiredTime_.split("\"")[1]
            wantedTime = desiredTime
            intentNeeded = response_df.query_result.intent.display_name
        else:
            wantedTime = message.split("-")[2]
            if message.split("-")[1] == 'yes':
                intentNeeded = 'Schedule - time - yes'
            if message.split("-")[1] == 'no':
                intentNeeded = 'Schedule - time - no'
                
        rescheduleAppointment(intentNeeded, request_data['from'], user['langId'], wantedTime, request_data['sessionId'])
        return ''
    
    if user['quizBusy'] != 'false':
        date_format_str = '%d/%m/%Y %H:%M:%S'
        userCourses = []
        for i in range(0, len(user['courses'])):
            if user['courses'][i]['coursePayment'] is True and user['courses'][i]['courseEndDate'] > str(date.today()) and user['courses'][i]['courseType'] == 'static':
                courseListItem = db['course'].find_one({'_id': user['courses'][i]['courseId']})
                if len(courseListItem['courseQuizzes']) > len(user['courses'][i]['courseQuizzes']):
                    
                    userCourses.append((user['courses'][i]['courseId']))
                
        if user['quizBusy'] == 'true':
            
            if message in userCourses: 
            
                courseChosen = db["course"].find_one({ '_id': message })
                courseChosenName = courseChosen['_id']

                index  = -1
                for i in range(0, len(user['courses'])):
                    if user['courses'][i]['courseId'] == courseChosen['_id'] and len(courseChosen['courseQuizzes']) >= len(user['courses'][i]['courseQuizzes']):
                        index = i
                        quizNumber = len(user['courses'][index]['courseQuizzes'])

                quizId = courseChosen['courseQuizzes'][quizNumber]

                quizChosen = db["questions"].find_one({ '_id': quizId})

                if quizNumber == len(user['courses'][index]['courseQuizzes']):
                    db['test'].update_one({'_id': request_data['from'], 'courses.courseId':courseChosenName}, {'$push': {'courses.$.courseQuizzes': {
                        'quizId': quizId,
                        'quizStart': datetime.now().strftime(date_format_str),
                        'quizMarks':[],
                        'quizScore': 0
                    }}})

                quizOptions = []
                updatedUser = db['test'].find_one({'_id': request_data['from']})
                questionNumber_ = len(updatedUser['courses'][index]['courseQuizzes'][quizNumber]['quizMarks']) + 1
                questionNumber = str(len(updatedUser['courses'][index]['courseQuizzes'][quizNumber]['quizMarks']) + 1)
                quizOptions = [quizChosen[questionNumber]['A'], quizChosen[questionNumber]['B'], quizChosen[questionNumber]['C']]

                quizBusy = str(index) +'-'+str(quizNumber)+'-'+quizId+'-'+questionNumber
                db['test'].update_one({'_id': request_data['from']}, { "$set": {'quizBusy': quizBusy}})
                quizImageId = getQuizPicture(quizChosen[questionNumber]['image'])

                sendQuizQuestion(request_data['from'], user['langId'], quizChosen[questionNumber]['question'], quizOptions, quizImageId)

                return ''
            
            else:
                db['test'].update_one({'_id': request_data['from']}, { "$set": {'quizBusy': 'false'}})
                sendText(request_data['from'], user['langId'], "Invalid selection of course! The quiz has terminated. Please try again!", request_data['sessionId'])
                return ''

        if message in ['A', 'B', 'C']:
            
            index = int(user['quizBusy'].split("-")[0])
            quizNumber = int(user['quizBusy'].split("-")[1])
            quizId = user['quizBusy'].split("-")[2]
            questionNumber = user['quizBusy'].split("-")[3]
            quizChosen = db["questions"].find_one({ '_id': quizId})
            markPerQuestion = int(quizChosen['quizMarks'] / quizChosen['quizCount'])
            if int(questionNumber) >= quizChosen['quizCount']:
                if len(user['courses'][index]['courseQuizzes'][quizNumber]['quizMarks']) + 1 ==  (quizChosen['quizCount']) and int(questionNumber) == quizChosen['quizCount']:
                    if message == quizChosen[questionNumber]['answer']:
                        db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$push': {'courses.$[courses].courseQuizzes.$[courseQuizzes].quizMarks': markPerQuestion}}, array_filters=[{"courses.courseId": {"$eq": quizChosen['courseId']}},{"courseQuizzes.quizId": {"$eq": quizId}}], upsert=True)
                        db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$set': {'courses.$[courses].courseQuizzes.$[courseQuizzes].quizEnd': datetime.now().strftime(date_format_str)}}, array_filters=[{"courses.courseId": {"$eq": quizChosen['courseId']}},{"courseQuizzes.quizId": {"$eq": quizId}}], upsert=True)
                        # db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$push': {'courses.$.courseQuizzes.$[].quizMarks': markPerQuestion}})
                        # db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$set': {'courses.$.courseQuizzes.$[].quizEnd': datetime.now().strftime(date_format_str)}})

                    else:
                        db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$push': {'courses.$[courses].courseQuizzes.$[courseQuizzes].quizMarks': 0}}, array_filters=[{"courses.courseId": {"$eq": quizChosen['courseId']}},{"courseQuizzes.quizId": {"$eq": quizId}}], upsert=True)
                        db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$set': {'courses.$[courses].courseQuizzes.$[courseQuizzes].quizEnd': datetime.now().strftime(date_format_str)}}, array_filters=[{"courses.courseId": {"$eq": quizChosen['courseId']}},{"courseQuizzes.quizId": {"$eq": quizId}}], upsert=True)
                        # db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$push': {'courses.$.courseQuizzes.$[].quizMarks': 0}})
                        # db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$set': {'courses.$.courseQuizzes.$[].quizEnd': datetime.now().strftime(date_format_str)}})
                    
                updatedUser = db['test'].find_one({'_id': request_data['from']})
                completeMarks_ = updatedUser['courses'][index]['courseQuizzes'][quizNumber]['quizMarks']
                secondsTaken = int((datetime.strptime((updatedUser['courses'][index]['courseQuizzes'][quizNumber]['quizEnd']), date_format_str) - datetime.strptime((updatedUser['courses'][index]['courseQuizzes'][quizNumber]['quizStart']), date_format_str)).total_seconds())
                completeMarks = sum(completeMarks_) - (secondsTaken * 0.01)

                db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$set': {'courses.$[courses].courseQuizzes.$[courseQuizzes].quizScore': completeMarks}}, array_filters=[{"courses.courseId": {"$eq": quizChosen['courseId']}},{"courseQuizzes.quizId": {"$eq": quizId}}], upsert=True)
                
                sendText(request_data['from'], user['langId'], "Your quiz is over! You have scored " + str(completeMarks) + '! 🥁', request_data['sessionId'])
                if completeMarks >= (quizChosen['quizMarks'] * 0.8):
                    discountBagged = db["discounts"].find_one({ '_id': quizId})
                    discountPercentage = (1.0 - discountBagged['discountOffered']) * 100
                    db['test'].update_one({'_id': request_data['from'] }, {'$push': {'offersAvailed': {
                        'discountId': quizId,
                        'discountRedeemed': False
                    }}})
                    sendText(request_data['from'], user['langId'], "Congratulations!🎉 You have bagged a discount coupon! 🎁  Use code *" + str(quizId) + "* next time to avail a discount of " + str(int(discountPercentage))+ "% on your next payment!", request_data['sessionId'])
                    
                db['test'].update_one({'_id': request_data['from']}, { "$set": {'quizBusy': 'false'}})
                return ''

            if len(user['courses'][index]['courseQuizzes'][quizNumber]['quizMarks']) < quizChosen['quizCount']:
                quizOptions = []
                questionNumber_ = int(questionNumber) + 1
                questionNumber = str(questionNumber_)
                # questionNumber = str(len(user['courses'][index]['courseQuizzes'][quizNumber]['quizMarks']) + 1)
                quizOptions = [quizChosen[questionNumber]['A'], quizChosen[questionNumber]['B'], quizChosen[questionNumber]['C']]
                
                if questionNumber_ > 1:
                    if message == quizChosen[str(questionNumber_ - 1)]['answer']:
                        db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$push': {'courses.$[courses].courseQuizzes.$[courseQuizzes].quizMarks': markPerQuestion}}, array_filters=[{"courses.courseId": {"$eq": quizChosen['courseId']}},{"courseQuizzes.quizId": {"$eq": quizId}}], upsert=True)
                        # db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$push': {'courses.$.courseQuizzes.$[].quizMarks': markPerQuestion}})
                        print('COERCTE')
                
                    else:
                        db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$push': {'courses.$[courses].courseQuizzes.$[courseQuizzes].quizMarks': 0}}, array_filters=[{"courses.courseId": {"$eq": quizChosen['courseId']}},{"courseQuizzes.quizId": {"$eq": quizId}}], upsert=True)
                        # db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$push': {'courses.$.courseQuizzes.$[].quizMarks': 0}})
                        print('INCORCET')
                
                quizBusy = str(index) +'-'+str(quizNumber)+'-'+quizId+'-'+questionNumber
                db['test'].update_one({'_id': request_data['from']}, { "$set": {'quizBusy': quizBusy}})
                quizImageId = getQuizPicture(quizChosen[questionNumber]['image'])
                sendQuizQuestion(request_data['from'], user['langId'], quizChosen[questionNumber]['question'], quizOptions, quizImageId)
                return ''    
        
        quizId = user['quizBusy'].split("-")[2]
        quizChosen = db["questions"].find_one({ '_id': quizId})
        courseChosenName = quizChosen['courseId']
        db['test'].update_one({'_id': request_data['from']}, { "$set": {'quizBusy': 'false'}})
        sendText(request_data['from'], user['langId'], "Invalid selection! The quiz has been terminated. Please try again!", request_data['sessionId'])
        db['test'].update_one({'_id': request_data['from'], 'courses.courseId':courseChosenName}, {'$pop': {'courses.$.courseQuizzes': 1}})
        
        return ''
    
    
    
    if response_df.query_result.intent.display_name == 'New-Resource':
        
        db['test'].update_one({'_id': request_data['from']}, { "$set": {'resource': 'true'}})

        userCourses =  []
        resourceUserCourses = []
        
        if len(user['courses']) == 0:
            db['test'].update_one({'_id': request_data['from']}, { "$set": {'resource': 'false'}})
            sendText(request_data['from'], user['langId'], "You haven't enrolled in any courses for notes!😕 Please enrol in the course to get resources!", request_data['sessionId'])
            sendCatalog(request_data['from'],user['langId'],request_data['sessionId'])
            
            return ''
        
        for i in range(0, len(user['courses'])):
            if user['courses'][i]['coursePayment'] is True and user['courses'][i]['courseEndDate'] > str(date.today()):
                resourceUserCourses.append(user['courses'][i]['courseId']+'-resbnb')
                userCourses.append(user['courses'][i]['courseId'])
                
        print(userCourses)
        if len(userCourses) == 0:
            db['test'].update_one({'_id': request_data['from']}, { "$set": {'resource': 'false'}})
            sendText(request_data['from'], user['langId'], "You haven't enrolled in any courses for notes!😕 Please enrol in the course to get resources!", request_data['sessionId'])
            sendCatalog(request_data['from'],user['langId'],request_data['sessionId'])
            return ''
        
        sendList(request_data['from'], user['langId'], "Please choose the course for which you want resource", "Select Courses", resourceUserCourses, userCourses, None, False, request_data['sessionId'])
        return ''
    
    if response_df.query_result.intent.display_name == 'New-Resource - course' or '-resbnb' in message:
        userCourses =  []
        resourceUserCourses = []
        for i in range(0, len(user['courses'])):
            if user['courses'][i]['coursePayment'] is True and user['courses'][i]['courseEndDate'] > str(date.today()):
                resourceUserCourses.append(user['courses'][i]['courseId']+'-resbnb')
                userCourses.append(user['courses'][i]['courseId'])
        if message in userCourses or message in resourceUserCourses:
            subjectName_ = message.split("-")[0]
            db['test'].update_one({'_id': request_data['from']}, { "$set": {'resource': subjectName_}})
            sendThreeButton(request_data['from'], user['langId'],"Please select below which resource you want for " + subjectName_,['gveres-books','gveres-notes','gveres-both'],['Books','Notes','Both'], request_data['sessionId'])
            return ''
        
        else:
            sendText(request_data['from'], user['langId'], "Invalid selection! The quiz has been terminated. Please try again!", request_data['sessionId'])
            db['test'].update_one({'_id': request_data['from']}, { "$set": {'resource': 'false'}})
            return ''

    if response_df.query_result.intent.display_name == 'New-Resource - course - books' or message == 'gveres-books':
        subject_name = db['test'].find_one({'_id': request_data['from']})['resource']
        
        sendText(request_data['from'], user['langId'], "Sending you books for " + subject_name + " 📚\n"  + db['course'].find_one({'_id': subject_name})['courseBook'], request_data['sessionId'])
        db['test'].update_one({'_id': request_data['from']}, { "$set": {'resource': 'false'}})
        return ''


    if response_df.query_result.intent.display_name == 'New-Resource - course - notes' or message == 'gveres-notes':

        subject_name = db['test'].find_one({'_id': request_data['from']})['resource']

        sendText(request_data['from'], user['langId'], "Sending you notes for " + subject_name  + " 📑\n"  + db['course'].find_one({'_id': subject_name})['courseNotes'], request_data['sessionId'])
        db['test'].update_one({'_id': request_data['from']}, { "$set": {'resource': 'false'}})
        return ''

    if response_df.query_result.intent.display_name == 'New-Resource - course - both' or message == 'gveres-both':

        subject_name = db['test'].find_one({'_id': request_data['from']})['resource']

        sendText(request_data['from'], user['langId'], "Sending you books for " + subject_name + " 📚\n"  + db['course'].find_one({'_id': subject_name})['courseBook'], request_data['sessionId'])
        sendText(request_data['from'], user['langId'], "Sending you notes for " + subject_name  + " 📑\n"  + db['course'].find_one({'_id': subject_name})['courseNotes'], request_data['sessionId'])
        db['test'].update_one({'_id': request_data['from']}, { "$set": {'resource': 'false'}})
        return ''


    
    if response_df.query_result.intent.display_name == 'Quiz':
        
        db['test'].update_one({'_id': request_data['from']}, { "$set": {'quizBusy': 'true'}})
        
        userCourses =  []
        
        if len(user['courses']) == 0:
            db['test'].update_one({'_id': request_data['from']}, { "$set": {'quizBusy': 'false'}})
            sendText(request_data['from'], user['langId'], "You haven't enrolled in any courses that contain quizzes. Why not explore more quizzes right now! 🥳", request_data['sessionId'])
            sendCatalog(request_data['from'],user['langId'],request_data['sessionId'])
            return ''
        
        for i in range(0, len(user['courses'])):
            if user['courses'][i]['coursePayment'] is True and user['courses'][i]['courseEndDate'] > str(date.today()) and user['courses'][i]['courseType'] == 'static':
                courseListItem = db['course'].find_one({'_id': user['courses'][i]['courseId']})
                print(len(courseListItem['courseQuizzes']))
                print(len(user['courses'][i]['courseQuizzes']))
                print(user['courses'][i]['courseId'])
                if len(courseListItem['courseQuizzes']) > len(user['courses'][i]['courseQuizzes']):
                    # coursesRank.append(str(i + 1))
                    userCourses.append((user['courses'][i]['courseId']))
                
        print(userCourses)
        if len(userCourses) == 0:
            db['test'].update_one({'_id': request_data['from']}, { "$set": {'quizBusy': 'false'}})
            sendText(request_data['from'], user['langId'], "You haven't enrolled in any courses that contain quizzes for now. Why not explore more quizzes right now! 🥳", request_data['sessionId'])
            sendCatalog(request_data['from'],user['langId'],request_data['sessionId'])
            return ''
        
        sendList(request_data['from'], user['langId'], "Please choose the course for which you want to test yourself", "Choose Quiz", userCourses, userCourses, None, False, request_data['sessionId'])
        return ''
    
    # if user['quizBusy'] != 'false':
    #     date_format_str = '%d/%m/%Y %H:%M:%S'
    #     userCourses = []
    #     for i in range(0, len(user['courses'])):
    #         if user['courses'][i]['coursePayment'] is True and user['courses'][i]['courseEndDate'] > str(date.today()) and user['courses'][i]['courseType'] == 'static':
    #             courseListItem = db['course'].find_one({'_id': user['courses'][i]['courseId']})
    #             if len(courseListItem['courseQuizzes']) > len(user['courses'][i]['courseQuizzes']):
                    
    #                 userCourses.append((user['courses'][i]['courseId']))
                
    #     if user['quizBusy'] == 'true':
            
    #         if message in userCourses: 
            
    #             courseChosen = db["course"].find_one({ '_id': message })
    #             courseChosenName = courseChosen['_id']

    #             index  = -1
    #             for i in range(0, len(user['courses'])):
    #                 if user['courses'][i]['courseId'] == courseChosen['_id'] and len(courseChosen['courseQuizzes']) >= len(user['courses'][i]['courseQuizzes']):
    #                     index = i
    #                     quizNumber = len(user['courses'][index]['courseQuizzes'])

    #             quizId = courseChosen['courseQuizzes'][quizNumber]

    #             quizChosen = db["questions"].find_one({ '_id': quizId})

    #             if quizNumber == len(user['courses'][index]['courseQuizzes']):
    #                 db['test'].update_one({'_id': request_data['from'], 'courses.courseId':courseChosenName}, {'$push': {'courses.$.courseQuizzes': {
    #                     'quizId': quizId,
    #                     'quizStart': datetime.now().strftime(date_format_str),
    #                     'quizMarks':[],
    #                     'quizScore': 0
    #                 }}})

    #             quizOptions = []
    #             updatedUser = db['test'].find_one({'_id': request_data['from']})
    #             questionNumber_ = len(updatedUser['courses'][index]['courseQuizzes'][quizNumber]['quizMarks']) + 1
    #             questionNumber = str(len(updatedUser['courses'][index]['courseQuizzes'][quizNumber]['quizMarks']) + 1)
    #             quizOptions = [quizChosen[questionNumber]['A'], quizChosen[questionNumber]['B'], quizChosen[questionNumber]['C']]

    #             quizBusy = str(index) +'-'+str(quizNumber)+'-'+quizId+'-'+questionNumber
    #             db['test'].update_one({'_id': request_data['from']}, { "$set": {'quizBusy': quizBusy}})
    #             quizImageId = getQuizPicture(quizChosen[questionNumber]['image'])

    #             sendQuizQuestion(request_data['from'], user['langId'], quizChosen[questionNumber]['question'], quizOptions, quizImageId)

    #             return ''
            
    #         else:
    #             db['test'].update_one({'_id': request_data['from']}, { "$set": {'quizBusy': 'false'}})
    #             sendText(request_data['from'], user['langId'], "Invalid selection of course! The quiz has terminated. Please try again!", request_data['sessionId'])
    #             return ''

    #     if message in ['A', 'B', 'C']:
            
    #         index = int(user['quizBusy'].split("-")[0])
    #         quizNumber = int(user['quizBusy'].split("-")[1])
    #         quizId = user['quizBusy'].split("-")[2]
    #         questionNumber = user['quizBusy'].split("-")[3]
    #         quizChosen = db["questions"].find_one({ '_id': quizId})
    #         markPerQuestion = int(quizChosen['quizMarks'] / quizChosen['quizCount'])
    #         if int(questionNumber) >= quizChosen['quizCount']:
    #             if len(user['courses'][index]['courseQuizzes'][quizNumber]['quizMarks']) + 1 ==  (quizChosen['quizCount']) and int(questionNumber) == quizChosen['quizCount']:
    #                 if message == quizChosen[questionNumber]['answer']:
    #                     db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$push': {'courses.$[courses].courseQuizzes.$[courseQuizzes].quizMarks': markPerQuestion}}, array_filters=[{"courses.courseId": {"$eq": quizChosen['courseId']}},{"courseQuizzes.quizId": {"$eq": quizId}}], upsert=True)
    #                     db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$set': {'courses.$[courses].courseQuizzes.$[courseQuizzes].quizEnd': datetime.now().strftime(date_format_str)}}, array_filters=[{"courses.courseId": {"$eq": quizChosen['courseId']}},{"courseQuizzes.quizId": {"$eq": quizId}}], upsert=True)
    #                     # db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$push': {'courses.$.courseQuizzes.$[].quizMarks': markPerQuestion}})
    #                     # db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$set': {'courses.$.courseQuizzes.$[].quizEnd': datetime.now().strftime(date_format_str)}})

    #                 else:
    #                     db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$push': {'courses.$[courses].courseQuizzes.$[courseQuizzes].quizMarks': 0}}, array_filters=[{"courses.courseId": {"$eq": quizChosen['courseId']}},{"courseQuizzes.quizId": {"$eq": quizId}}], upsert=True)
    #                     db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$set': {'courses.$[courses].courseQuizzes.$[courseQuizzes].quizEnd': datetime.now().strftime(date_format_str)}}, array_filters=[{"courses.courseId": {"$eq": quizChosen['courseId']}},{"courseQuizzes.quizId": {"$eq": quizId}}], upsert=True)
    #                     # db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$push': {'courses.$.courseQuizzes.$[].quizMarks': 0}})
    #                     # db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$set': {'courses.$.courseQuizzes.$[].quizEnd': datetime.now().strftime(date_format_str)}})
                    
    #             updatedUser = db['test'].find_one({'_id': request_data['from']})
    #             completeMarks_ = updatedUser['courses'][index]['courseQuizzes'][quizNumber]['quizMarks']
    #             secondsTaken = int((datetime.strptime((updatedUser['courses'][index]['courseQuizzes'][quizNumber]['quizEnd']), date_format_str) - datetime.strptime((updatedUser['courses'][index]['courseQuizzes'][quizNumber]['quizStart']), date_format_str)).total_seconds())
    #             completeMarks = sum(completeMarks_) - (secondsTaken * 0.01)

    #             db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$set': {'courses.$[courses].courseQuizzes.$[courseQuizzes].quizScore': completeMarks}}, array_filters=[{"courses.courseId": {"$eq": quizChosen['courseId']}},{"courseQuizzes.quizId": {"$eq": quizId}}], upsert=True)
                
    #             sendText(request_data['from'], user['langId'], "Your quiz is over! You have scored " + str(completeMarks) + '! 🥁', request_data['sessionId'])
    #             if completeMarks >= (quizChosen['quizMarks'] * 0.8):
    #                 discountBagged = db["discounts"].find_one({ '_id': quizId})
    #                 discountPercentage = (1.0 - discountBagged['discountOffered']) * 100
    #                 db['test'].update_one({'_id': request_data['from'] }, {'$push': {'offersAvailed': {
    #                     'discountId': quizId,
    #                     'discountRedeemed': False
    #                 }}})
    #                 sendText(request_data['from'], user['langId'], "Congratulations!🎉 You have bagged a discount coupon! 🎁  Use code *" + str(quizId) + "* next time to avail a discount of " + str(int(discountPercentage))+ "% on your next payment!", request_data['sessionId'])
                    
    #             db['test'].update_one({'_id': request_data['from']}, { "$set": {'quizBusy': 'false'}})
    #             return ''

    #         if len(user['courses'][index]['courseQuizzes'][quizNumber]['quizMarks']) < quizChosen['quizCount']:
    #             quizOptions = []
    #             questionNumber_ = int(questionNumber) + 1
    #             questionNumber = str(questionNumber_)
    #             # questionNumber = str(len(user['courses'][index]['courseQuizzes'][quizNumber]['quizMarks']) + 1)
    #             quizOptions = [quizChosen[questionNumber]['A'], quizChosen[questionNumber]['B'], quizChosen[questionNumber]['C']]
                
    #             if questionNumber_ > 1:
    #                 if message == quizChosen[str(questionNumber_ - 1)]['answer']:
    #                     db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$push': {'courses.$[courses].courseQuizzes.$[courseQuizzes].quizMarks': markPerQuestion}}, array_filters=[{"courses.courseId": {"$eq": quizChosen['courseId']}},{"courseQuizzes.quizId": {"$eq": quizId}}], upsert=True)
    #                     # db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$push': {'courses.$.courseQuizzes.$[].quizMarks': markPerQuestion}})
    #                     print('COERCTE')
                
    #                 else:
    #                     db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$push': {'courses.$[courses].courseQuizzes.$[courseQuizzes].quizMarks': 0}}, array_filters=[{"courses.courseId": {"$eq": quizChosen['courseId']}},{"courseQuizzes.quizId": {"$eq": quizId}}], upsert=True)
    #                     # db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$push': {'courses.$.courseQuizzes.$[].quizMarks': 0}})
    #                     print('INCORCET')
                
    #             quizBusy = str(index) +'-'+str(quizNumber)+'-'+quizId+'-'+questionNumber
    #             db['test'].update_one({'_id': request_data['from']}, { "$set": {'quizBusy': quizBusy}})
    #             quizImageId = getQuizPicture(quizChosen[questionNumber]['image'])
    #             sendQuizQuestion(request_data['from'], user['langId'], quizChosen[questionNumber]['question'], quizOptions, quizImageId)
    #             return ''    
        
    #     quizId = user['quizBusy'].split("-")[2]
    #     quizChosen = db["questions"].find_one({ '_id': quizId})
    #     courseChosenName = quizChosen['courseId']
    #     db['test'].update_one({'_id': request_data['from']}, { "$set": {'quizBusy': 'false'}})
    #     sendText(request_data['from'], user['langId'], "Invalid selection! The quiz has been terminated. Please try again!", request_data['sessionId'])
    #     db['test'].update_one({'_id': request_data['from'], 'courses.courseId':courseChosenName}, {'$pop': {'courses.$.courseQuizzes': 1}})
        
    #     return ''
    
    
    if response_df.query_result.intent.display_name == 'Progress':
        sendTwoButton(request_data['from'], user['langId'], "Do you want to check progress for yourself? 📈", ["Yes-prg", "No-prg"], ["Yes", "No"], request_data['sessionId'])
        return ''
    
    if response_df.query_result.intent.display_name == 'Progress - no' or message == 'No-prg':
        sendText(request_data['from'], user['langId'], "Please specify the mobile number of that person starting with '91'. For example, 919876543210.", request_data['sessionId'])
        return ''
    
    if response_df.query_result.intent.display_name == 'Progress - yes' or response_df.query_result.intent.display_name == 'Progress - no - number' or message == 'Yes-prg':
        specifiedUser = ''
        if message.startswith("91"):
            foundUser = db['test'].find_one({'_id': request_data['message']['text']['body']})
            if foundUser is None:
                sendText(request_data['from'], user['langId'], "Invalid number. Please check if the provided number was correct.", request_data['sessionId'])
            else:
                specifiedUser = foundUser
        
        elif response_df.query_result.intent.display_name == 'Progress - yes' or message == 'Yes-prg':
            specifiedUser = user
            
        else:
            sendText(request_data['from'], user['langId'], "Exited the progress report procedure!", request_data['sessionId'])
            return ''
            
        userCourses = []
        for i in range(0, len(specifiedUser['courses'])):
            if specifiedUser['courses'][i]['courseStartDate'] <= str(date.today()):
                
                if specifiedUser['courses'][i]['courseType'] == 'static':
                    if len(specifiedUser['courses'][i]['courseQuizzes']) > 0:
                        userCourses.append((specifiedUser['courses'][i]['courseId']))
                        continue
                
                if specifiedUser['courses'][i]['courseType'] == 'dynamic':
                    if specifiedUser['courses'][i]['courseFeedback'] != '':
                        userCourses.append((specifiedUser['courses'][i]['courseId']))
                        continue
        
        if len(userCourses) == 0:
            sendText(request_data['from'], user['langId'], "No progress to show sadly! 😭", request_data['sessionId'])
            return ''
        
        db['test'].update_one({'_id': request_data['from']}, { "$set": {'resultBusy': { 'busy':'true', 'user': specifiedUser['_id']}}})
        sendList(request_data['from'], user['langId'], "Please choose the course to check progress", "Course", userCourses, userCourses, None, False, request_data['sessionId'])
        return ''
        
    if user['resultBusy']['busy'] == 'true':
        userCourses = []
        specifiedUser = db['test'].find_one({'_id': user['resultBusy']['user']})
        for i in range(0, len(specifiedUser['courses'])):
            if specifiedUser['courses'][i]['courseStartDate'] <= str(date.today()):
                
                userCourses.append((specifiedUser['courses'][i]['courseId']))
                
        if message in userCourses: 
            db['test'].update_one({'_id': request_data['from']}, { "$set": {'resultBusy': { 'busy':'false', 'user': ''}}})
            studentProgress(request_data['from'], user['resultBusy']['user'], message, request_data['sessionId'])
            return ''
            
        else:
            db['test'].update_one({'_id': request_data['from']}, { "$set": {'resultBusy': { 'busy':'false', 'user': ''}}})
            sendText(request_data['from'], user['langId'], "Invalid course selection!", request_data['sessionId'])
            return ''
        return ''
    
    if user['UNIT-TESTING'] == 'blue':
        return ''
    
    if response_df.query_result.intent.display_name == 'Videos':

        ytResults = youtube(request_data['message']['text']['body'])
        for ytResult in ytResults:
            img_url = ytResult['thumbnail']
            response = requests.get(img_url)
            if response.status_code:
                fp = open('static/youtubeMedia/youtubeThumbnail.jpg', 'wb')
                fp.write(response.content)
                fp.close()
            mediaId,mediaType = uploadMedia('youtubeThumbnail.jpg','static/youtubeMedia/youtubeThumbnail.jpg','jpg')
            print(mediaId)
            url_link = str(ytResult['url'])
            sendTemplateForYoutube(request_data['from'],mediaId,url_link)
        return ''
        
    if response_df.query_result.intent.display_name == 'WebSearch': 
        result_search = google_search(response_df.query_result.query_text)
        sendText(request_data['from'], langId, result_search, request_data['sessionId'])
    
    else:
        print(response_df.query_result.fulfillment_text)
        print(response_df.query_result.intent.display_name)
        if response_df.query_result.intent.display_name == 'Default Fallback Intent':
            sendText(request_data['from'],user['langId'], response_df.query_result.fulfillment_text, request_data['sessionId'])
            sendHelp(request_data['from'],user['langId'],request_data['sessionId'])
            return ''
        
        sendText(request_data['from'],user['langId'], response_df.query_result.fulfillment_text, request_data['sessionId'])
    
    return ''

@app.route('/healthz')
def healthz():
    return ''

@app.route('/register-for-course/<WaId>')
def form(WaId):
    global _id, name
    _id = WaId
    userInfo = db['test'].find_one({"_id": WaId})
    
    cartInfo = db['cart'].find_one({"_id": WaId})

    courseDetails = []
    totalFees = 0

    if cartInfo is not None:
        courseDetails = cartInfo["courseDetails"]
        totalFees = cartInfo["totalFees"]
    else:
        # send message to user
        sendText(WaId,'en', "Your cart is empty 🛒", '757575757575757575')
        return 'Cart Empty'

    print(totalFees)
    print(courseDetails)

    # discount checking
    offersAvailable = []
    offers = userInfo["offersAvailed"]
    print(offers)
    for o in offers:
        if o["discountRedeemed"] == "false":
            discountPercent = db['discounts'].find_one({'_id': o["discountId"]})
            offersAvailable.append(str(o["discountId"]) + ' - ' + str(int((1-float(discountPercent["discountOffered"]))*100)) + "%")

    print(offersAvailable)

    return render_template('payment_form.html', name=userInfo["name"], mobile=_id, courses=courseDetails, coursesLen=len(courseDetails), offers=offersAvailable, offersLen=len(offersAvailable))


@app.route('/pay', methods=['POST'])
def pay():
    if request.method == "POST":
        WaId = request.form['mobile']
        WaId = WaId[1:3] + WaId[4:]
        session['contact'] = WaId

        userInfo = db['test'].find_one({"_id": WaId})
        cartInfo = db['cart'].find_one({"_id": WaId})

        if cartInfo is not None:
            courseDetails = cartInfo["courseDetails"]
            totalFees = cartInfo["totalFees"]
        else:
            # send message to user
            return 'Cart Empty'

        offer = request.form['offers']
        if offer == "none":
            session['offer'] = 'None'
            offer = 1
        else:
            session['offer'] = offer.split(' - ')[0]
            offer = offer.split(' - ')[1][:-1]
        discountAmount = totalFees*int(offer)/100
        offer = 1 - int(offer)/100
        print('offer', offer)

        feesToBePaid = totalFees*offer

        client = razorpay.Client(auth=(razorpay_key, razorpay_secret))
        notes = {
            'name': userInfo["name"],
            'email': userInfo["email"],
            'contact': WaId,
            'totalFees': totalFees,
            'discountAmount': discountAmount,
            'offer': offer,
            'feesToBePaid': feesToBePaid
        }

        session["amount"] = feesToBePaid
        payment = client.order.create({"amount": int(feesToBePaid)*100,
            "currency": "INR",
            "payment_capture": 1,
            "notes": notes})
        return render_template('pay.html', payment=payment, razorpay_key=razorpay_key, course=courseDetails, courseLen=len(courseDetails))



@app.route('/success', methods=['POST'])
def success():
    if request.method == "POST":
        print('Razorpay Payment ID: ' + request.form['razorpay_payment_id'])
        print('Razorpay Order ID: ' + request.form['razorpay_order_id'])
        print('Razorpay Signature: ' + request.form['razorpay_signature'])
        print(request.form)

        WaId = session["contact"]
        amount = session["amount"]

        userInfo = db['test'].find_one({"_id": WaId})
        cartInfo = db['cart'].find_one({"_id": WaId})

        if cartInfo is not None:
            courseDetails = cartInfo["courseDetails"]
            totalFees = cartInfo["totalFees"]
        else:
            # send message to user
            sendText(WaId,'en', "Your cart is empty 🛒", '757575757575757575')
            return 'Cart Empty'

        res = []
        messageCourse = []
        json = {}
        for c in courseDetails:
            if c["courseType"] == "static":
                messageCourse.append(c["courseId"])
                json = {
                    "courseId": c["courseId"],
                    "courseType": c["courseType"],
                    "courseStartDate": c["courseStartDate"],
                    "courseEndDate": c["courseEndDate"],
                    "courseQuizzes": [],
                    "coursePayment": True
                }
            if c["courseType"] == "dynamic":
                messageCourse.append(c["courseId"])
                json = {
                    "courseId": c["courseId"],
                    "courseType": c["courseType"],
                    "courseStartDate": c["courseStartDate"],
                    "courseEndDate": c["courseEndDate"],
                    "courseFeedback": '',
                    "coursePayment": True
                }
            res.append(json)

        res = userInfo["courses"] + res

        db["test"].update_one({
                '_id': WaId
            }, {
                '$set': {
                    'courses': res
                }
            })

        db["cart"].delete_one({'_id': WaId})

        get_receipt(courseDetails, session['amount'])
        mediaId, mediaType = uploadMedia('receipt.pdf', 'static/paymentMedia/receipt.pdf', 'pdf')
        print(mediaId, mediaType)
        sendMedia(WaId, mediaId, mediaType, '7575757575757575')

        if session['offer'] != 'None':
            db['test'].update_one({'_id': WaId, 'offersAvailed.discountId': session['offer']}, {'$set': {'offersAvailed.$[offersAvailed].discountRedeemed': "true"}}, array_filters=[{"offersAvailed.discountId": {"$eq": session['offer']}}], upsert=True)
            print('update done')              

        wa_message = ''
        if len(messageCourse) != 0:
            wa_message = ', '.join(messageCourse) + ' are static courses.\nYou can attempt quizzes for such courses and bag rewards! Use *Quiz me* for example!\n\n'
        
        for c in courseDetails:
            wa_message += '\nVisit the course *'+ c['courseId'] + '* at '+c['courseLink']
        wa_message += '\nYou can also check for progress of individual courses!\nText *Progress me* for example! \n Need more resources? Try texting *I need study resources* for books and notes!'
        sendText(WaId,'en', wa_message, '757575757575757575')

        # remove all sessions values
        session.pop('contact', None)
        session.pop('offer', None)
        session.pop('amount', None)

        return render_template('success.html', payment_id=request.form['razorpay_payment_id'], contact=WaId, email = userInfo["email"], amount=amount)
        



if __name__ == '__main__':
    app.run(debug=False)
