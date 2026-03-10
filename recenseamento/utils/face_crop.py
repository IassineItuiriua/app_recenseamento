import cv2


def extrair_rosto_bi(caminho):

    img = cv2.imread(caminho)

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) == 0:
        return None

    x, y, w, h = faces[0]

    rosto = img[y:y+h, x:x+w]

    return rosto
# import cv2

# def extrair_rosto_bi(caminho):

#     img = cv2.imread(caminho)

#     face_cascade = cv2.CascadeClassifier(
#         cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
#     )

#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#     faces = face_cascade.detectMultiScale(gray, 1.3, 5)

#     if len(faces) == 0:
#         return None

#     x, y, w, h = faces[0]

#     rosto = img[y:y+h, x:x+w]

#     return rosto