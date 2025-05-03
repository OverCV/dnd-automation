from cvzone.HandTrackingModule import HandDetector

from hand_ctrl import set_leds
import cv2

num_str = "uno", "dos", "tres", "cuatro", "cinco"
detector = HandDetector(
    detectionCon=0.8,
    maxHands=1,
)

video = cv2.VideoCapture(0)

while True:
    hay_vision, foto = video.read()
    foto = cv2.flip(foto, 1)
    manos, img = detector.findHands(foto)

    if hay_vision and manos:
        print(manos)
        mano = manos[0]

        dedo_arriba = detector.fingersUp(mano)
        dedos_arriba = sum(dedo_arriba)

        print(dedo_arriba)
        set_leds(dedo_arriba)

        cv2.putText(
            img=foto,
            text=f"Dedos Arriba: {num_str[dedos_arriba - 1]}",
            org=(20, 460),
            fontFace=cv2.FONT_HERSHEY_COMPLEX,
            fontScale=1,
            color=(255, 255, 255),
            thickness=1,
            lineType=cv2.LINE_AA,
        )

        puntos = mano["lmList"]
        for punto in enumerate(puntos):
            cv2.putText(
                img=foto,
                text=str(punto[0]),
                org=(punto[1][0], punto[1][1]),
                fontFace=cv2.FONT_HERSHEY_COMPLEX,
                fontScale=0.5,
                color=(255, 255, 255),
                thickness=1,
                lineType=cv2.LINE_AA,
            )

    cv2.imshow("frame", foto)
    key = cv2.waitKey(1)
    if key == ord("q"):
        break

video.release()
cv2.destroyAllWindows()
