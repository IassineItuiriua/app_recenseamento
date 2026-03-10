from deepface import DeepFace


def comparar_faces(selfie_path, bi_path):

    try:

        resultado = DeepFace.verify(
            img1_path=selfie_path,
            img2_path=bi_path,
            detector_backend="opencv",
            enforce_detection=False
        )

        return resultado["verified"]

    except Exception as e:

        print("Erro reconhecimento facial:", e)

        return False