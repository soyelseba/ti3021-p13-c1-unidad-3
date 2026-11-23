import requests # Librería para conectarme a la API
import oracledb # Librería para conectarme a la Base de datos

# Trabajar con credenciales de manera segura con el archivo .env
import os
from dotenv import load_dotenv
load_dotenv()

# Establecer conexion con la base de datos
class ConexionOracle:
    def __init__(self, user, password, dsn):
        self.__user = user
        self.__password = password
        self.__dsn = dsn
    def obtener_conexion(self): 
        try:
            conexion = oracledb.connect(
                user = self.__user,
                password = self.__password,
                dsn = self.__dsn
            )
            return conexion
        except:
            print("No se pudo conectar a la base de datos")
            raise 

class APIClima:
    def __init__(self, token):
        self.__base_url = "https://api.weatherapi.com/v1/current.json"
        self.__token = token
    def obtener_clima(self, locacion, conexion: oracledb.Connection): # Por favor, agregar TRY EXCEPT
        payload = { "q" : locacion, "lang": "es", "key": self.__token}
        response = requests.get(
            url = self.__base_url,
            params = payload
        )
        data = response.json()

        locacion = data["location"]["name"]
        region = data["location"]["region"]
        pais = data["location"]["country"]
        hora_consulta = data["location"]["localtime"]
        temperatura_c = data["current"]["temp_c"]
        pronostico = data["current"]["condition"]["text"]
        uv = data["current"]["uv"]
        nubosidad = data["current"]["cloud"]

        data_consulta = {
            locacion,
            region,
            pais,
            hora_consulta,
            temperatura_c,
            pronostico,
            uv,
            nubosidad,
        }

        self.guardar_en_base_datos(conexion, data_consulta)

        return data
    def crear_tabla(self, conexion: oracledb.Connection):
        cursor = conexion.cursor()
        cursor.execute("""CREATE TABLE climas (
            id_consulta NUMBER PRIMARY KEY,
            locacion VARCHAR2(64),
            region VARCHAR2(64),
            pais VARCHAR2(64),
            hora_consulta VARCHAR2(64),
            temperatura_c VARCHAR2(64),
            pronostico VARCHAR2(64),
            uv VARCHAR2(64),
            nubosidad VARCHAR2(64)
        )""")
        conexion.commit()  
    def guardar_en_base_datos(self, conexion: oracledb.Connection, data_consulta):
        cursor = conexion.cursor()
        cursor.execute(
            statement="""INSERT INTO
        climas(id_consulta, locacion, region, pais, hora_consulta, temperatura_c, pronostico, uv, nubosidad)
        VALUES (:id_consulta, :locacion, :region, :pais, :hora_consulta, :temperatura_c, :pronostico, :uv, :nubosidad)""",
        parameters=data_consulta)
        conexion.commit()

api_clima = APIClima( token = os.getenv("token_weather_api") )
informacion_climatica = api_clima.obtener_clima(locacion="Quilicura")
print(informacion_climatica)