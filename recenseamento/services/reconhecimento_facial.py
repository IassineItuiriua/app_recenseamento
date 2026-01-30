def verificar_face(bi_path, selfie_path):
    try:
        from deepface import DeepFace

        resultado = DeepFace.verify(
            img1_path=bi_path,
            img2_path=selfie_path,
            detector_backend="opencv",  # 🔥 SEM RetinaFace
            enforce_detection=True,
            model_name="VGG-Face"
        )
        return resultado.get("verified", False)

    except Exception as e:
        return False

# def verificar_foto(bi_path, foto_path):
#     try:
#         from deepface import DeepFace  # lazy + protegido
#     except ImportError:
#         # DeepFace não instalado (Render / produção)
#         return False

#     try:
#         resultado = DeepFace.verify(
#             img1_path=foto_path,
#             img2_path=bi_path,
#             model_name="ArcFace",
#             enforce_detection=False
#         )
#         return resultado.get("verified", False)
#     except Exception as e:
#         print(f"Erro ao verificar foto: {e}")
#         return False
