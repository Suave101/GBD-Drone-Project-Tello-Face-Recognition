import cv2
import time
import socket
import threading
import numpy as np
import os
import face_recognition
import playsound
import logging
# todo: Add GUI for Camera


def estop():
    send("emergency")
    speaktext(0)
    while True:
        send("emergency")


def speaktext(tc=0):
    os.chdir("text to speak")
    if tc == 0:
        playsound.playsound("estop.mp3")
    elif tc == 1:
        playsound.playsound("fric.mp3")
    elif tc == 2:
        playsound.playsound("fullyoperational.mp3")
    elif tc == 3:
        playsound.playsound("initinit.mp3")
    elif tc == 4:
        playsound.playsound("sst.mp3")
    elif tc == 5:
        playsound.playsound("veac.mp3")
    elif tc == 6:
        playsound.playsound("wdpo.mp3")
    os.chdir("..")


def send(message):
    try:
        sock.sendto(message.encode(encoding="utf-8"), tello_address)
        print("Sending message: " + message)
    except Exception as effg:
        print("Error sending: " + str(effg))


def receive():
    global french
    while True:
        try:
            response, _ = sock.recvfrom(128)
            message = response.decode(encoding='utf-8')
            print("Received message: " + message)
            if french and "ok" in message:
                print("resetting command in progress")
                french = False

        except Exception as exceptiontenthisisaexception:
            sock.close()
            print("Error receiving: " + str(exceptiontenthisisaexception))
            break


def send_with_buffer():
    global bs_list
    global commands_survey
    global french
    global taken_off
    try:
        while True:
            if french:
                while french:
                    time.sleep(0)
            try:
                if bs_list["Top Priority"][0] is not None:
                    message = bs_list["Top Priority"][0]
                    if message == "takeoff":
                        taken_off = True
                    elif message == "land":
                        taken_off = False
                    print("Top Priority Command is being sent")
                    while True:
                        try:
                            sock.sendto(message.encode(encoding="utf-8"), tello_address)
                            print("Sending message: " + message)
                        except Exception as eikk:
                            print("Error sending: " + str(eikk))
                        try:
                            response, _ = sock.recvfrom(128)
                            message = response.decode(encoding='utf-8')
                            if french and "ok" in message:
                                break
                        except Exception as eikk:
                            print("Error Receiving: " + str(eikk))

                            sock.close()
                            break
                    french = False
            except Exception as expoint:
                logging.info("Exception: " + str(expoint))
                try:
                    if bs_list["Secondary Priority"][0] is None:
                        bs_list["Secondary Priority"].extend(commands_survey)
                    else:
                        message = bs_list["Secondary Priority"][0]
                        if message == "takeoff":
                            taken_off = True
                        elif message == "land":
                            taken_off = False
                        while True:
                            try:
                                sock.sendto(message.encode(encoding="utf-8"), tello_address)
                                print("Sending message: " + message)
                            except Exception as eikk:
                                print("Error sending: " + str(eikk))
                            try:
                                response, _ = sock.recvfrom(128)
                                message = response.decode(encoding='utf-8')
                                if french and "ok" in message:
                                    break
                            except Exception as eikk:
                                print(f"Error: {str(eikk)}")
                                sock.close()
                                break
                        french = False
                except Exception as eikk:
                    print(f"Error Something Bad Happened: {eikk}")
                    bs_list["Secondary Priority"].extend(commands_survey)
                    print(bs_list)
    except Exception as a_very_bad_exception:
        print("Big Bad Error: " + str(a_very_bad_exception))


if __name__ == '__main__':
    logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S')
    try:
        logging.info("Logging Enabled")
        logging.info("System Init: Starting")
        speaktext(3)
        bs_list = {"Top Priority": [], "Secondary Priority": []}
        killing = True
        french = True
        commands_survey = ["takeoff", "up 30", "down 30", "cw 90", "cw 90", "cw 90", "cw 90", "land"]
        taken_off = False
        tello_address = ('192.168.10.1', 8889)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', 9000))
        current_command = 0
        receiveThread = threading.Thread(target=receive)
        receiveThread.daemon = True
        receiveThread.start()
        logging.info("Drone Partially Operational")
        speaktext(6)
        im1 = face_recognition.load_image_file("images/alexander.jpg")
        ima1 = face_recognition.face_encodings(im1)[0]
        known_face_encodings = [ima1]
        known_face_names = ["Alexander Doyle"]
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True
        logging.info("Facial Recognition Init Complete")
        speaktext(1)
        send("command")
        time.sleep(1)
        send("streamon")
        time.sleep(1)
        camera = cv2.VideoCapture('udp://127.0.0.1:11111')
        time.sleep(3)
        logging.info("Drone Video Stream Enabled")
        speaktext(5)
        logging.info("Drone Fully Operational")
    except Exception as Init_exception:
        logging.error("Error While Init: " + str(Init_exception))
    else:
        try:
            maincommandpipethread = threading.Thread(target=send_with_buffer, daemon=True).start()
            french = False
            speaktext(2)
            while True:
                ret, frame = camera.read()
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = small_frame[:, :, ::-1]
                if process_this_frame:
                    face_locations = face_recognition.face_locations(rgb_small_frame)
                    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                    face_names = []
                    for face_encoding in face_encodings:
                        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                        name = "Enemy"
                        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = known_face_names[best_match_index]
                            print("Person Found: " + name)
                            if name == "Alexander Doyle":
                                print("Fugitive Found")
                                if killing:
                                    if taken_off:
                                        bs_list["Top Priority"].append("forward 100")
                                        bs_list["Top Priority"].append("back 100")
                                        bs_list["Top Priority"].append("land")
                                    elif taken_off:
                                        bs_list["Top Priority"].append("takeoff")
                                        bs_list["Top Priority"].append("forward 100")
                                        bs_list["Top Priority"].append("back 100")
                                        bs_list["Top Priority"].append("land")
                                    else:
                                        logging.warning("Something Weird Happened in your attacking code")
                                else:
                                    print("Yo, We're Buffering Dude")
                        face_names.append(name)

                process_this_frame = not process_this_frame
                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
                cv2.imshow('Tello', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    logging.warning("Drone Video Stream Not Visible")
                    break
            sock.close()
            logging.warning("Drone Communication Capability Disabled")
            camera.release()
            cv2.destroyAllWindows()
        except Exception as e:
            logging.error(f"System Suddenly Stopped: {e}")
            exit(0)
    finally:
        print("System Exit By End of File")
        logging.info("System Exit By End of File :)")
