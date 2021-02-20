import cv2
import time
import socket
import threading
import numpy as np
import face_recognition


def killpe():
    global killing
    killing = False
    print("Killer Drone - Starting")
    send("takeoff")
    time.sleep(10)
    send("speed 100")
    time.sleep(10)
    send("forward 100")
    time.sleep(10)
    send("land")
    print("Killer Drone - Ended")
    killing = True


def send(message):
    try:
        sock.sendto(message.encode(), tello_address)
        print("Sending message: " + message)
    except Exception as e:
        print("Error sending: " + str(e))


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

        except Exception as e:
            sock.close()
            print("Error receiving: " + str(e))
            break


killing = True
french = False
tello_address = ('192.168.10.1', 8889)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 9000))
commands_survey = ["cw 90", "up 30", "down 30", "cw 90", "cw 90", "cw 90"]
# Up To 5 Only \/
current_command = 0
receiveThread = threading.Thread(target=receive)
receiveThread.daemon = True
receiveThread.start()
print("Face Rec Init - Starting")
im1 = face_recognition.load_image_file("images/alexander.jpg")
ima1 = face_recognition.face_encodings(im1)[0]
known_face_encodings = [ima1]
known_face_names = ["Alexander Doyle"]
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
print("Face Rec Init - Complete")
send("command")
time.sleep(1)
send("streamon")
time.sleep(1)
camera = cv2.VideoCapture('udp://127.0.0.1:11111')
time.sleep(3)
print("Stream Started")


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
            name = "Unknown"
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                print("Nah Fam That Ain't Happening")
                if killing:
                    j = threading.Thread(target=killpe)
                    j.daemon = True
                    j.start()
                else:
                    print("Yo, We're Buffering Dude")
            else:
                print("Kill")
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
        break

sock.close()
camera.release()
cv2.destroyAllWindows()
