from cvzone.HandTrackingModule import HandDetector
from controller import set_leds
import cv2

detector = HandDetector(
    detectionCon=0.8,
    maxHands=1,
)

video = cv2.VideoCapture(0)

while True:
    ret, frame = video.read()
    frame = cv2.flip(frame, 1)
    manos, img = detector.findHands(frame)

    if manos:
        mano_der, mano_izq = manos
        finger_up = detector.fingersUp(mano_der)
        dedos_arriba = sum(finger_up)

        print(finger_up)
        set_leds(finger_up)

        cv2.putText(
            img=frame,
            text=f"Dedos Arriba: {dedos_arriba}",
            org=(20, 460),
            fontFace=cv2.FONT_HERSHEY_COMPLEX,
            fontScale=1,
            color=(255, 255, 255),
            thickness=1,
            lineType=cv2.LINE_AA,
        )

    cv2.imshow("frame", frame)
    key = cv2.waitKey(1)
    if key == ord("q"):
        break

video.release()
cv2.destroyAllWindows()
