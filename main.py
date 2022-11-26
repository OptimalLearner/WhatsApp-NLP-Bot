# Utils
from utils.visualisation import studentProgress
from utils.video import youtube
from utils.sendMessage import send_message
# from utils.quiz import quiz_bot
from utils.dialogflowQuery import dialogflow_query
from utils.webSearch import google_search
from utils.organisationInfo import organisationIntroduction
# from utils.quiz import quiz_bot
from utils.dialogflowQuery import dialogflow_query
from utils.TrialFlow import trialFlow
from utils.db import db
from utils.schedule import getTimeSlot
from utils.schedule import bookTimeSlot
from utils.reschedule import rescheduleAppointment
from utils.imgMedia import imgToText

from api.text import sendText
from api.quizButtons import sendQuiz
from api.oneButton import sendOneButton
from api.twoButton import sendTwoButton
from api.threeButton import sendThreeButton
from api.list import sendList
from api.uploadMedia import uploadMedia
from api.sendTemplate import sendTemplateForYoutube

# Extra imports
from pymongo import MongoClient
from datetime import date, timedelta, datetime
import os
import json
import random
from deep_translator import GoogleTranslator


import langid
#import requests to make API call
import requests
# import dotenv for loading the environment variables
from dotenv import load_dotenv
# import flask for setting up the web server
from flask import *



load_dotenv()

import razorpay
razorpay_key = os.environ['RAZORPAY_KEY_ID']
razorpay_secret = os.environ['RAZORPAY_KEY_SECRET']


# creating the Flask object
app = Flask(__name__)
app.secret_key = b'delph@!#78d%'

quiz_time = False


@app.route('/', methods=['POST'])
def reply():
   

    # _______________ TESTING__________________

#     print(request.form.to_dict)
#     print(jsonify(request={"status": 200}))
    if request.get_data() is not None:
        print("Inside Request json loads data")
        print(json.loads(request.data))
    global request_data
    request_data = json.loads(request.data)
    # if request_data.get('sourceCountry') is not None:
    #     return ''
    
    print(request_data)
    if "businessId" not in request_data:
        return ''

    if request_data["message"]["type"] == "order":
        WaId = request_data["from"]
        if len(request_data["message"]["order"]["product_items"]) < 1:
            print('No Course Selected')
            sendText(WaId,'en',"No Course Selected")
            pass
        else:
            # fetch coursera id of current user
            userInfo = db['test'].find_one({'_id': WaId})
            print(userInfo)
            if userInfo["courseraId"] == '':
                print('Coursera Id Not There')
                sendText(WaId,'en',"Coursera Link Not Set")
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
                                "quantity": item["quantity"]
                            }
                        else:
                            courseTemp = {
                                "courseId": courseData["_id"],
                                "courseType": "dynamic",
                                "courseFees": courseData["courseFees"],
                                "courseStartDate": courseData["courseStart"],
                                "courseEndDate": courseData["courseEnd"],
                                "quantity": item["quantity"]
                            }
                        courseDetails.append(courseTemp)
                        totalFees += courseData["courseFees"]
                
                print("Course Details")
                print(courseDetails)

                
                if alreadyRegisteredFlag == 1:
                    # course already registered message to user
                    print('course already registered message to user')
                    sendText(WaId,'en',"Course(s) already registered by the user once")
                else:
                    # send payment link
                    sendText(WaId,'en',"https://vikings.onrender.com//register-for-course/"+WaId)
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
    
    #_________________________________________
    if 'image' in request_data['message']:
        
        print(request.form)
       
        print(request.form)
       
        response = requests.get(request.form.get('MediaUrl0'))
        if response.status_code:
            fp = open('client_Image.jpg', 'wb')
            fp.write(response.content)
            fp.close()
        textFromImage = imgToText('client_Image.jpg')
        langId = 'en'
        # if langid.classify(textFromImage) is None:
        #     langId = 'en'
        # langId = langid.classify(textFromImage)[0]
        
        print(textFromImage)
        print(google_search(textFromImage))
        sendText(request_data['from'],'en',google_search(textFromImage))
        return ''
    # print(request)
    global quiz_time
    # global message
    message_ = request_data['message']['text']['body']
    # print(request.form)

    langId = 'en'
    if langid.classify(message_) is None:
        langId = 'en'
    langId = langid.classify(message_)[0]
    if langId != 'en':
        message = GoogleTranslator(
            source="auto", target="en").translate(message_)
    else:
        message = message_
    response_df = dialogflow_query(message)


#_____________Video Search wiith send Template ________________________________________________

    ytResults = youtube(message_)
    for ytResult in ytResults:
        print(os.path.splitext(ytResult['thumbnail'])[0])
        print(os.path.splitext(ytResult['thumbnail'])[1])
        img_url = ytResult['thumbnail']
        response = requests.get(img_url)
        if response.status_code:
            fp = open('ytImage.jpg', 'wb')
            fp.write(response.content)
            fp.close()
        mediaId,mediaType = uploadMedia('ytImage.jpg','ytImage.jpg','jpg')
        print(mediaId)
        url_link = '\n' + ytResult['url'] + '\n'
        # sendTemplateForYoutube(request_data['from'],mediaId,mediaType,""" URL    sdfghbj""")
        print()

#_______________________________   Video Search Send Template Ends  ________________________________________________________________


    user = db['test'].find_one({'_id': request_data['from']})
    print(response_df.query_result.intent.display_name)
    if user == None and response_df.query_result.intent.display_name != 'Register' and response_df.query_result.intent.display_name != 'Organisation':
        # send button to register
        # sendTwoButton(request_data['from'], "Welcome to our world of education", "register", "I want to register right now!", "surf",  "I am just here to surf and explore!")
        welcome_text = ["Welcome to our world of education",
                        "It's a better place if you register today!",
                        "Trust me! Registering with us will brighten your future",
                        "Vishal, the business tycoon recommends us, register now!"]
        print(message)
        # print(response_df.query_result.language_code)

        sendTwoButton(request_data['from'], langId, welcome_text[random.randint(0, 3)], ["register", "roam"], ["Register right now!", "Just exploring!"])
        return '' 

    if user == None and (response_df.query_result.intent.display_name == 'Register' or response_df.query_result.intent.display_name == 'Register-Follow'):
        db["test"].insert_one({'_id': request_data['from'], 'name': '', 'email': '', 'langId': langId})
        sendText(request_data['from'], langId, response_df.query_result.fulfillment_text)
        return ''

    if user == None and response_df.query_result.intent.display_name == 'Organisation':
        organisationIntroduction(request_data['from'], langId)
        return ''

    if user == None and response_df.query_result.intent.display_name == 'Organisation - history' or response_df.query_result.intent.display_name == 'Organisation - vision' or response_df.query_result.intent.display_name == 'Organisation - visit':
        sendText(request_data['from'], langId, response_df.query_result.fulfillment_text)
        return ''

    if user != None and (response_df.query_result.intent.display_name == 'Register' or response_df.query_result.intent.display_name == 'Register-Follow' or response_df.query_result.intent.display_name == 'Enroll-Courses' ):
        if user['name'] == '':
            name_ = str(response_df.query_result.output_contexts[0].parameters.fields.get(
                'person.original'))
            name = name_.split("\"")[1]
            db['test'].update_one({'_id': request_data['from']}, {"$set": {'name': name}})
            sendText(request_data['from'], user['langId'], response_df.query_result.fulfillment_text)
            return ''

        elif user['email'] == '' :
            email_ = str(response_df.query_result.output_contexts[0].parameters.fields.get('email.original'))
            email = email_.split("\"")[1]
            db['test'].update_many({'_id': request_data['from']}, {"$set": {'email': email.lower(), 'scheduleDone': "false"}})
            sendText(request_data['from'], user['langId'], response_df.query_result.fulfillment_text)
            # sendText(request_data['from'], user['langId'],"Please find below the courses we offer")
            # sendList(request_data['from'],user['langId'],"These are the courses We offer , Please select one","Courses",["Math","Science","History","Geography","English"],["Math-Course","Science-Course","History-Course","Geography-Course","English"],["NCERT + JEE + CET ","Arihant + JEE","Textbook questions + Revision","Textbook questions + Revision","English grammer + Writing skills and much more..."])
            return ''
        


    # if user != None and (response_df.query_result.intent.display_name == 'Register' or response_df.query_result.intent.display_name == 'Register-Follow'):

    # quiz_count = user['quiz_count']
    quiz_count = 100
    print("HELLLLLOCOCOCOCOCO")
    # message = request_data['message']['text']['body'].lower()
    if quiz_time and quiz_count == 0:
        quiz_initial(user, quiz_count,request_data)
        return ''

    workflow(user, request_data, response_df)
    return ''


def quiz_initial(user, quiz_count,request_data):
    quiz_count = quiz_count + 1
    quiz_bot2(db, 'M1', quiz_count)
    db['test'].update_one({'_id': request_data['from']}, {"$set": {'quiz_count': quiz_count}})
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
        sendQuiz(request_data['from'], quiz, questionNumberString)

    if questionNumber > 1 and questionNumber < 7:
        questionNumberString = str(questionNumber - 1)
        return quiz[questionNumberString]['answer']
    else:
        return ''


def quiz_chat(user, user_answer):
    global quiz_time
    quiz_count = user['quiz_count']
    quiz_count = quiz_count + 1
    db['test'].update_one({'_id': request_data['from']}, {"$set": {'quiz_count': quiz_count}})
    print(quiz_count)
    previous_answer = quiz_bot2(db, 'M1', quiz_count)
    if user_answer == previous_answer:
        quiz_marks = user['quizzes']['M1'] + 2
        print(quiz_marks)
        db['test'].update_one({'_id': request_data['from']}, {"$set": {'quizzes.M1': quiz_marks}})
    if quiz_count == 6 or quiz_count > 6:
        quiz_time = False
        db['test'].update_one({'_id': request_data['from']}, {"$set": {'quiz_count': 0}})
        sendText(request_data['from'], 'Your quiz is over!')
        return ''
    else:
        return ''


def workflow(user, request_data, response_df):
    global quiz_time
    if quiz_time:
        # user = db['test'].find_one({'_id': request_data['from']})
        quiz_answer = db['course']
        quiz_chat(user, request_data['message']['text']['body'])
        return ''

    if not quiz_time:
        # message = request_data['message']['text']['body'].lower() # video on digimon
        # response_df = dialogflow_query(message)
        
        if response_df.query_result.intent.display_name == 'Organisation':
            organisationIntroduction(request_data['from'], user['langId'])
            return ''
        
        if response_df.query_result.intent.display_name == 'Organisation - history' or response_df.query_result.intent.display_name == 'Organisation - vision' or response_df.query_result.intent.display_name == 'Organisation - visit':
            sendText(request_data['from'], user['langId'], response_df.query_result.fulfillment_text)
            return ''
        
        if response_df.query_result.intent.display_name == 'Schedule':
            timeSlots = getTimeSlot()
            print(timeSlots)
            sendList(request_data['from'], user["langId"], "Please choose your preferred time for tomorrow!", "Free slots tomorrow!", timeSlots, timeSlots, None)
            return '' 
        
        if response_df.query_result.intent.display_name == 'Schedule - time':
            bookTimeSlot(request_data['message']['text']['body'], request_data['from'], user['langId'])
            return ''
        
        if response_df.query_result.intent.display_name == 'Schedule - time - yes' or response_df.query_result.intent.display_name == 'Schedule - time - no':
            desiredTime_ = str(response_df.query_result.output_contexts[0].parameters.fields.get('time.original'))
            desiredTime = desiredTime_.split("\"")[1]
            rescheduleAppointment(response_df.query_result.intent.display_name, request_data['from'], user['langId'], desiredTime)
            return ''

        if user['scheduleDone'] == 'false':
            # sendTwoButton(request_data['from'], user["langId"], "Why not explore the courses we offer? \n You can also know more about us!", ["courses", "organisation"], ["Explore courses now!", "Know more about us!"])
            # studentProgress(request_data['from'])
            print("Working !")
            # sendText(request_data['from'], user['langId'], 'https://a837-115-96-217-68.ngrok.io/register-for-course/'+request_data['from'])
            return ''

        if response_df.query_result.intent.display_name == 'Videos':
            result_videos = youtube(response_df.query_result.query_text)
            print(result_videos)
            for video in result_videos:
                sendText(request_data['from'],video['url'] + ' | ' + video['title'])
            return ''

        if response_df.query_result.intent.display_name == 'WebSearch':  # Google JEE datde
            result_search = google_search(response_df.query_result.query_text)
            sendText(request_data['from'], result_search)

        if response_df.query_result.intent.display_name == 'Parent':
            print(response_df.query_result.parameters)
            picture_url = studentProgress()
            send_message(
                response_df.query_result.fulfillment_text, picture_url)
            return ''

        else:
            # quiz_bot(db, 'M1')
            now = datetime.datetime.now()
            print(now.year, now.month, now.day,now.hour, now.minute, now.second)
            print(type(now.year), type(now.month), type(now.day),type(now.hour), type(now.minute), type(now.second))
            # print(request.form.get('From'))
            # send_message(request.form.get('From'), response_df.query_result.fulfillment_text,'')
            print(response_df.query_result.fulfillment_text)
            print(response_df.query_result.intent.display_name)
            print(request.form)
            sendText(request_data['from'], user['langId'], response_df.query_result.fulfillment_text)

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

        userInfo = db['test'].find_one({"_id": WaId})
        cartInfo = db['cart'].find_one({"_id": WaId})

        if cartInfo is not None:
            courseDetails = cartInfo["courseDetails"]
            totalFees = cartInfo["totalFees"]
        else:
            # send message to user
            return 'Cart Empty'

        res = []
        messageCourse = []
        for c in courseDetails:
            if c["courseType"] == "static":
                messageCourse.append(c["courseId"])
            json = {
                "courseId": c["courseId"],
                "courseType": c["courseType"],
                "courseStartDate": c["courseStartDate"],
                "courseEndDate": c["courseEndDate"],
                "courseQuizzzes": [],
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

        print('session offer', session['offer'])

        if session['offer'] != 'None':
            db['test'].update_one({'_id': WaId, 'offersAvailed.discountId': session['offer']}, {'$set': {'offersAvailed.$[offersAvailed].discountRedeemed': "true"}}, array_filters=[{"offersAvailed.discountId": {"$eq": session['offer']}}], upsert=True)
            print('update done')              

        wa_message = ''
        if len(messageCourse) != 0:
            wa_message = ', '.join(messageCourse) + ' are static courses.\nYou can attempt quizzes for such courses and bag rewards! Use *Quiz me* for example!\n\n'

        wa_message += 'You can also check for progress of individual courses!\nText *Progress me* for example!'
        sendText(WaId,'en', wa_message)

        # pop all sessions

        return render_template('success.html', payment_id=request.form['razorpay_payment_id'], contact=session["contact"], email = userInfo["email"], amount=session["amount"])
        

if __name__ == '__main__':
    app.run(debug=True)
