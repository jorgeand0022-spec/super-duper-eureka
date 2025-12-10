from pymongo import MongoClient


class ConexionMongoDB:
    def __init__(self, db_name="control_personal"):
        self.uri = "mongodb+srv://LuisBueno23:Luis2020123@clusterlbm.66uyt.mongodb.net/control_personal?retryWrites=true&w=majority&appName=ClusterLBM"

        try:
            self.client = MongoClient(self.uri)
            self.client.admin.command('ping')
            print("Conexión exitosa a MongoDB")
        except Exception as e:
            raise ConnectionError(f" Error al conectar a MongoDB: {e}")

        # Seleccionar base de datos
        self.db = self.client[db_name]

    def get_collection(self, collection_name):
        """Obtener una colección por nombre"""
        return self.db[collection_name]




#from pymongo import MongoClient
#
#class ConexionMongoDB:
#    def __init__(self, uri="mongodb+srv://LuisBueno23:Luis2020123@clusterlbm.66uyt.mongodb.net/?retryWrites=true&w=majority&appName=ClusterLBM", db_name="control_personal"):
#        self.client = MongoClient(uri)
#        self.db = self.client[db_name]
#
#    def get_collection(self, collection_name):
#        return self.db[collection_name] 
#