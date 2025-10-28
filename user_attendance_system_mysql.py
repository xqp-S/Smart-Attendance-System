import os
import time

import cv2
import face_recognition as fr
import numpy as np
from datetime import datetime
import json
import pveagle
from pvrecorder import PvRecorder
from user import User

userClass = User()
ACCESS_KEY = "21kJS433hxxi6lFh/tKKqVrYO7fwcBxSXJzrs7pYMxbwXAoiGulSWw=="
DEFAULT_DEVICE_INDEX = 1

faceDetected = ""
faceDetectedCounter = 0
faceNotDetectedCounter = 0

value = 4


# presented_today_text = set()
# presented_today_date = datetime.now().strftime('%Y-%m-%d')
# def markAttended(name):
#     global presented_today_text, presented_today_date
#
#     current_date = datetime.now().strftime('%Y-%m-%d')
#     if current_date != presented_today_date:
#         presented_today_text = set() #clear the set
#         presented_today_date = current_date #update the date
#
#     now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     with open('attendance.csv','r+') as f:
#         myDataList = f.readlines()
#         already_present_today = False
#
#         for line in myDataList:
#             if line.strip() == "":
#                 continue
#             entry = line.strip().split(',')
#             recorded_name = entry[0]
#             recorded_time = entry[1]
#             recorded_date = recorded_time.split(' ')[0]
#             if recorded_name == name and recorded_date == current_date:
#                 already_present_today = True
#                 break
#
#         if not already_present_today:
#             f.writelines(f'{name},{now}\n')
#             print(f'Marked attendance for: {name} at {now}')
#         else:
#             if name not in presented_today_text:
#                 print(f'{name} is alraedy marked for today.')
#                 presented_today_text.add(name)
userIds = []
names = []
encodedFacesList = []
audioProfilesList = []

#region loading users
users = userClass.getAllUsers()

for user in users:
    id, name, password, ff, ap, isActive = user
    ff = ff.split(", ")
    ff = np.asarray(ff, dtype=np.float64)
    ap = pveagle.EagleProfile.from_bytes(ap)

    userIds.append(id)
    names.append(name)
    encodedFacesList.append(ff)
    audioProfilesList.append(ap)

print(names)


try:
    eagle = pveagle.create_recognizer(
        access_key=ACCESS_KEY,
        speaker_profiles=audioProfilesList)
except pveagle.EagleError as e:
    # Handle error
    print(e)
    pass

recorder = PvRecorder(
    device_index=DEFAULT_DEVICE_INDEX,
    frame_length=eagle.frame_length)

#endregion




cam = cv2.VideoCapture(0)


CamLoop = True


def test(faceMatchIndex):
    global faceDetected, faceDetectedCounter, names
    print(f"listening for {names[faceMatchIndex]}...")
    startTime = time.time()
    recorder.start()
    eagle.reset()

    try:
        while ((time.time() - startTime) < 5):
            audio_frame = recorder.read()
            scores = eagle.process(audio_frame)
            audioMatchIndex = np.argmax(scores)
            if ((scores[audioMatchIndex] > 0.8) and (audioMatchIndex == faceMatchIndex)):
                print(f"{names[audioMatchIndex]} is detected")
                faceDetected = ""
                faceDetectedCounter = 0
                return True

    except KeyboardInterrupt:
        pass

    faceDetected = ""
    faceDetectedCounter = 0
    recorder.stop()
    print("no recognized speaker is detected")
    return False



while CamLoop:
        ret, frame = cam.read()
        frameS = cv2.resize(frame, (0, 0), None, 1 / value, 1 / value)
        name = ""
        matchIndex = -1
        # frameS = cv2.cvtColor(frameS, cv2.COLOR_BGR2RGB)

        faceLoc = fr.face_locations(frameS)
        if (faceLoc):

            faceLoc = faceLoc[0]
            encodedFrame = fr.face_encodings(frameS, [faceLoc])
            faceDis = fr.face_distance(encodedFacesList, encodedFrame[0])

            if (faceDis.min() < 0.5):
                faceNotDetectedCounter = 0
                matchIndex = np.argmin(faceDis)
                if faceDis[matchIndex]:
                    name = names[matchIndex]

                    if (faceDetected == name):
                        faceDetectedCounter += 1
                    else:
                        faceDetected = name
                        faceDetectedCounter = 0



                    faceDetectedCounter += 1
                    tmp = round((faceDetectedCounter / 11) * 100, 1)
                    txt = f"{name} {tmp}%"
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * value, x2 * value, y2 * value, x1 * value
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 2)
                    cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (255, 0, 255), cv2.FILLED)
                    cv2.putText(frame, txt, (x1, y2 -10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255),2)
            else:
                    faceNotDetectedCounter += 1
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * value, x2 * value, y2 * value, x1 * value
                    cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (255, 0, 255), cv2.FILLED)
                    cv2.putText(frame, "not found", (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 2)

        if (faceDetectedCounter > 11):
            faceDetectedCounter = 0
            if (test(matchIndex)):
                userClass.markAttended(userIds[matchIndex])

        if (faceNotDetectedCounter > 10):
            faceNotDetectedCounter = 0
            name = input("enter your name: ").strip()
            password = input("enter your password: ").strip()
            userClass.markAttended(credit = (name, password))


        # if len(faceLoc) > 0:
        #     faceLoc = faceLoc[0]
        #     cv2.rectangle(frame, (faceLoc[3] * 10, faceLoc[0] * 10), (faceLoc[1] * 10, faceLoc[2] * 10), (255, 0, 255,), 2)


        cv2.imshow('Camera', frame) # frame[50:600, 400:900] to crop
        # Press 'q' to exit the loop
        if cv2.waitKey(1) == ord('q'):
            break



recorder.delete()
eagle.delete()
cam.release()
cv2.destroyAllWindows()

