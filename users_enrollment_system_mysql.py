import cv2
import face_recognition as fr
import numpy
import pveagle
from pvrecorder import PvRecorder
from user import User



userClass = User()


ACCESS_KEY = "21kJS433hxxi6lFh/tKKqVrYO7fwcBxSXJzrs7pYMxbwXAoiGulSWw=="
DEFAULT_DEVICE_INDEX = 1
try:
    eagle_profiler = pveagle.create_profiler(access_key=ACCESS_KEY)
except pveagle.EagleError as e:
    print(e)
    pass
recorder = PvRecorder(
    device_index=DEFAULT_DEVICE_INDEX,
    frame_length=eagle_profiler.min_enroll_samples
    )

def showUsers():
    users = userClass.getAllUsers()
    print("#=========== Users =============#")
    print("user_id- name")
    for user in users:
        id, name, password, ff, ap, isActive = user
        print(str(id) + "- " + name)
    print("#===============================#")

def getUserCount():
    return len(userClass.getAllUsers())

def modifyUser():
    showUsers()
    while True:
        index = int(input("enter user's id to modify or -1 to exit: "))

        if(index < 0):
            break

        op = input("enter property number to modify\n"
              "1. name\n"
              "2. face features\n"
              # "3. audio features\n"
              # "4. password\n"
             )

        match op:
            case '1':
                name = input("enter the new user's name: ")
                userClass.updateUser(index, name=name)
                print("name modified to " + name)
                break

            case '2':
                ff = getFaceEncoding()  # ff stands for face features
                if ff:
                    userClass.updateUser(index, face_features=ff)
                    print("face features modified")
                break
            case _:
                break





def getFaceEncoding():
    faceEncoding = None
    value = 4
    # create a cam and start recording
    window_name = "abc"
    #cam = cv2.VideoCapture("http://192.168.1.9:4747/video/mjpeg")
    cam = cv2.VideoCapture(0)


    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)


    def askForAcceptance(frame):
        cv2.imshow(window_name, frame)
        res = input("do want to use this picture? (y or n): ")
        if (res == "y"):
            # cv2.imwrite("faketest.png", frame)
            return fr.face_encodings(frame)[0]
        else:
            return None

    # image recording
    print("press S when a purple box is shown around the face")
    while True:
        ret, frame = cam.read()
        #frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        frameS = cv2.resize(frame, (0, 0), None, 1 / value, 1 / value)
        frame2 = frame.copy()
        allFacesLoc = fr.face_locations(frameS)
        for faceLoc in allFacesLoc:
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * value, x2 * value, y2 * value, x1 * value
            cv2.rectangle(frame2, (x1, y1), (x2, y2), (255, 0, 255), 2)

        cv2.imshow(window_name, frame2)
        if cv2.waitKey(1) == ord('s'):
            if (len(allFacesLoc) > 0):
                faceEncoding = askForAcceptance(frame)
                break
        if cv2.waitKey(1) == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()



    if (isinstance(faceEncoding, numpy.ndarray)):
        return str(faceEncoding.tolist()).replace("[", "").replace("]", "")

def getAudioEncoding(speaker_name):
    eagle_profiler.reset()
    recorder.start()
    print(f"Hi, my name is {speaker_name}, and I’m speaking to help create my voice profile. I enjoy reading, talking with friends, and exploring new ideas.\nThis is my natural speaking voice, and I’m talking in a calm, steady tone. I’ll continue speaking so there’s enough audio for analysis.\nVoice recognition is useful in many smart applications, and I’m excited to try this out.")
    enroll_percentage = 0.0
    while enroll_percentage < 100.0:
        audio_frame = recorder.read()
        enroll_percentage, feedback = eagle_profiler.enroll(audio_frame)
        # print(enroll_percentage)

    recorder.stop()

    speaker_profile = eagle_profiler.export().to_bytes()
    # audio_path = f"users_profiles/audio/{speaker_name}.bin"
    # with open(audio_path, "wb") as f:
    #     f.write(speaker_profile.to_bytes())

    return speaker_profile

def addUser():

    name = input("enter the new user's name: ")
    password = input("enter the new user's password: ")
    ff = getFaceEncoding() # ff stands for face features
    ap = getAudioEncoding(name) # returns audio profile

    if ff and ap:
        if (userClass.addUser(name, password, ff, ap)):
            print(name + " is add to users list")
        else:
            print("error: no user is added")
    else:
        print("Error: no face features or audio features are provided\n")

def removeUser():
    showUsers()
    op = int(input("enter the user's id to remove: "))
    id, name, password, ff, ap = userClass.getOneUser(op)


    if (userClass.deleteUser(op)):
        print(f"user with name {name} removed")
    else:
        print("error: no user deleted")






systemLoop = True
print("Welcome to Attendance System"
      "here is the list of all commands: \n")
while systemLoop:

    print(f"1. show users ({getUserCount()})\n"
          "2. add a user\n"
          "4. modify a user\n"
          "5. remove a user\n"
          "6. exit\n")

    op = input("\nenter option number: ")

    match op:
        case '1':
            showUsers()

        case '2':
            addUser()

        case '4':
            modifyUser()

        case '5':
            removeUser()

        case _:
            # saveFile()
            print("system closed")
            break




recorder.delete()
eagle_profiler.delete()
#endregion