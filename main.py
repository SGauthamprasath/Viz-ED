import cv2
import mediapipe as mp
from cvzone.HandTrackingModule import HandDetector
import numpy as np

pts = []
imgG = None
contours = None
imgGray = None
imgCanvas=None

def contour():
    return contours
def fun_imgG():
    return imgG
def fun_imgGray():
    return imgGray
def detecting(image,object_position):

    """this function verifies whether the hand pointer is present within the contour or not is not it will return false"""
    
    global pts
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, threshold = cv2.threshold(gray, 110, 255, cv2.THRESH_BINARY)
    global contours
    contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    temp=0
    check_list=[]
    for cnt in contours[1:]:
        temp+=1
        approx = cv2.approxPolyDP(cnt, 0.009 * cv2.arcLength(cnt, True), True)
        if cv2.pointPolygonTest(approx, object_position, False) >= 0:
            check_list.append(1)
            if object_position not in pts:
                pts.append(list(object_position))
    if len(check_list)==0 or len(check_list)!=temp:
        return False
    return True

def checking(gray,contour,imgray):

    """this function checks for how much area is filled inside the contour and return the coverage percentag"""

    contour_mask = np.zeros_like(gray)
    cv2.drawContours(contour_mask, [contour], -1, 255, thickness=cv2.FILLED)
    _,line_mask= cv2.threshold(imgray, 127, 255, cv2.THRESH_BINARY)
    combined_mask = cv2.bitwise_and(contour_mask, line_mask)
    contour_area = np.sum(contour_mask == 255)
    covered_area = np.sum(combined_mask == 255)
    coverage_percentage = (covered_area / contour_area) * 10
    return coverage_percentage

def checking_outside(gray,contour,imgray):

    """ this function checks for how much area is covered outside the bounding box and returns the percentage of it """
    
    contour_mask = np.zeros_like(gray)
    cv2.drawContours(contour_mask, [contour], -1, 255, thickness=cv2.FILLED)
    _,line_mask= cv2.threshold(imgray, 50, 255, cv2.THRESH_BINARY)
    combined_mask = cv2.bitwise_or(contour_mask, line_mask)
    combined_mask1 = cv2.bitwise_xor(combined_mask, contour_mask)
    #cv2.imshow("contour_mask",combined_mask1)
    #cv2.imshow("contour_mask",combined_mask1)
    contour_area = np.sum(contour_mask == 255)
    covered_area = np.sum(combined_mask1 == 255)

    coverage_percentage = (covered_area/contour_area) * 10
    return coverage_percentage

def generate_frames(picture):
    camera = cv2.VideoCapture(0)
    camera.set(3, 1280)
    camera.set(4, 740)

    detector = HandDetector(detectionCon=0.9)
    global imgCanvas
    imgCanvas = np.zeros((600, 690, 3), np.uint8)

    xp = 0
    yp = 0
    drawColor = (0, 0, 255)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            frame = cv2.resize(frame, (690, 600))
            frame = cv2.flip(frame, 1)
            photo="static/images/"+ picture +".jpg"
            img = cv2.imread(photo, cv2.IMREAD_COLOR)
            if img is None:
                print("image not found")
                break
            img = cv2.resize(img, (690, 600))
            hands, frame = detector.findHands(frame)

            if len(hands) == 1:
                lmList1 = hands[0]["lmList"]
                x1, y1 = lmList1[8][0:2]
                finger = detector.fingersUp(hands[0])
                if finger == [1, 1, 1, 1, 1]:
                    xp, yp = 0, 0
                if finger in ([1, 1, 0, 0, 0], [0, 1, 0, 0, 0], [1, 0, 0, 0, 0]):
                    if xp == 0 and yp == 0:
                        xp = x1
                        yp = y1

                    cv2.circle(frame, (x1, y1), 30, drawColor, cv2.FILLED)
                    cv2.line(frame, (xp, yp), (x1, y1), color=drawColor, thickness=30)
                    cv2.line(imgCanvas, (xp, yp), (x1, y1), color=drawColor, thickness=30)

                    if not detecting(img, (xp, yp)):
                        drawColor = (0, 0, 255)
                    if detecting(img, (xp, yp)):
                        drawColor = (0, 255, 0)
                    xp, yp = x1, y1

            global imgG
            imgG = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, imgI = cv2.threshold(imgG, 50, 255, cv2.THRESH_BINARY_INV)
            imgI = cv2.cvtColor(imgI, cv2.COLOR_GRAY2BGR)
            frame = cv2.bitwise_and(frame, img, imgI)

            global imgGray
            imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
            _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
            imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)

            frame = cv2.bitwise_and(frame, imgInv)
            frame = cv2.bitwise_or(frame, imgCanvas)

            res, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
cv2.destroyAllWindows()

def retrytoggle():
    imgCanvas = np.zeros((600, 690, 3), np.uint8)