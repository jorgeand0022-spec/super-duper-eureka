# utils/auth.py

def validar_credenciales(usuario, contraseña):
    """Valida las credenciales del usuario contra la base de datos"""
    from conexion.conexion_mongo import ConexionMongoDB

    usuarios_collection = ConexionMongoDB().get_collection("usuarios")
    
    # Busca al usuario por nombre y contraseña
    user_data = usuarios_collection.find_one({
        "usuario": usuario,
        "contraseña": contraseña
    })

    if user_data:
        return user_data["rol"]  # Devuelve el rol si coincide
    else:
        return None  # No encontrado