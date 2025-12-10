from conexion.conexion_mongo import ConexionMongoDB
from utils.auth import hash_password

conexion = ConexionMongoDB()
usuarios = conexion.get_collection("usuarios")

usuarios.delete_many({})  # Limpiar antes de insertar

usuarios.insert_many([
    {
        "usuario": "admin",
        "contraseña": hash_password("1234"),
        "rol": "administrador"
    },
    {
        "usuario": "supervisor",
        "contraseña": hash_password("1234"),
        "rol": "supervisor"
    },
    {
        "usuario": "empleado",
        "contraseña": hash_password("1234"),
        "rol": "empleado"
    }
])

print(" Usuarios creados correctamente")