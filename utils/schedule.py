# import dotenv for loading the environment variables
from dotenv import load_dotenv
load_dotenv()

from utils.db import db
from api.text import sendText
from api.twoButton import sendTwoButton
from datetime import date, timedelta

time_slots = {
    "5:00 PM": "17:00",
    "6:00 PM": "18:00",
    "7:00 PM": "19:00"
}

# https://www.mongodb.com/docs/atlas/app-services/triggers/scheduled-triggers/
def getTimeSlot():
    tomorrow_ = date.today() +  timedelta(1)
    tomorrow = tomorrow_.strftime("%Y-%m-%d")
    available = db["appointments"].find_one({
        '_id': tomorrow
    })
    res = [k for k,v in available.items() if v is None and k != '_id']
    return res

def bookTimeSlot(time, userWAId, langId):
    tomorrow_ = date.today() +  timedelta(1)
    tomorrow = tomorrow_.strftime("%Y-%m-%d")
    free = db["appointments"].find_one({
        '_id': tomorrow,
        time: None
    })
    print(free)
    if free is not None:
        
        alreadyBooked = False
        
        bookedTime = ''
        
        tomorrowSchedule = db["appointments"].find_one({
            '_id': tomorrow
        })
        
        for key in tomorrowSchedule.keys():
            if tomorrowSchedule[key] == userWAId:
                alreadyBooked = True
                bookedTime = key
                break

        if not alreadyBooked:
            updated = db["appointments"].update_one({ '_id': tomorrow }, { "$set": { time: userWAId }} )
            if updated:
                print('Appointment scheduled')
                sendText(userWAId, langId, "Your appointment for tomorrow has been scheduled at " + time + ". You will be called by our counselor at the given time and date." )
                return ''
            else:
                print('An erroneous response')
                sendText(userWAId, langId, "Please select one of the time slots from the list")
                return ''
        else: 
            sendTwoButton(userWAId, langId,  "You have already booked a slot at " + bookedTime +"! Do you want to reshedule your appointment?", ["yes", "no"], ["Yes", "No"])
            return ''
    else:
        print('Time Slot unavailable')
        sendText(userWAId, langId, "Time slot unavailable")
        return ''