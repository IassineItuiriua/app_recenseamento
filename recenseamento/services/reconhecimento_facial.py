from deepface import DeepFace


def verificar_face(bi_path, selfie_path):

    try:

        resultado = DeepFace.verify(
            img1_path=bi_path,
            img2_path=selfie_path,
            detector_backend="opencv",
            enforce_detection=False,
            model_name="VGG-Face"
        )

        return resultado["verified"]

    except Exception:
        return False