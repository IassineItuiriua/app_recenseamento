def verificar_foto(bi_path, foto_path):
    from deepface import DeepFace  # ✅ lazy import

    try:
        resultado = DeepFace.verify(
            img1_path=foto_path,
            img2_path=bi_path,
            model_name="ArcFace",
            enforce_detection=False
        )
        return resultado.get("verified", False)
    except Exception as e:
        print(f"Erro ao verificar foto: {e}")
        return False
