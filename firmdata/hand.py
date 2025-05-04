from cvzone.HandTrackingModule import HandDetector

from hand_ctrl import switch_leds
import cv2

numeros_str = "cero", "uno", "dos", "tres", "cuatro", "cinco"
detector = HandDetector(
    detectionCon=0.8,
    maxHands=1,
)
direccion = {"Right": "derecha", "Left": "izquierda"}

video = cv2.VideoCapture(0)

while True:
    hay_vision, foto = video.read()
    # foto = cv2.flip(foto, 0)
    manos, img = detector.findHands(foto)

    if hay_vision and manos:
        print(manos)
        mano = manos[0]

        estado_mano = detector.fingersUp(mano)
        switch_leds(estado_mano)

        dedos_arriba = sum(estado_mano)

        cv2.putText(
            img=foto,
            text=f"Dedos Arriba: {numeros_str[dedos_arriba]} en {direccion[mano['type']]}",
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
