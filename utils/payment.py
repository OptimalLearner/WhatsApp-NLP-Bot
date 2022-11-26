# import flask for setting up the web server
from flask import *

# import OS for environment variables
import os

# import dotenv for loading the environment variables
from dotenv import load_dotenv
load_dotenv()

# import razorpay sdk
import razorpay
razorpay_key = os.environ['RAZORPAY_KEY_ID']
razorpay_secret = os.environ['RAZORPAY_KEY_SECRET']

from main import app
from utils.db import db
from api.text import sendText


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
        if o["discountRedemmed"] == "false":
            print("hehehehes")
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
            'offer': request.form['offers'],
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

        wa_message = ''
        if len(messageCourse) != 0:
            wa_message = ', '.join(messageCourse) + ' are static courses. You can attempt quizzes for such courses and bag rewards! Use Quiz me for example!\n'

        wa_message += 'You can also check for progress of individual courses! Text Progress me for example!'
        sendText(WaId,'en', wa_message)

        return render_template('success.html', payment_id=request.form['razorpay_payment_id'], contact=session["contact"], email = userInfo["email"], amount=session["amount"])
        