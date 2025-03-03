from cryptography.fernet import Fernet
from datetime import datetime


import hashlib

def generar_token(contraseña):
    return hashlib.sha256(contraseña.encode()).hexdigest()
la_punta ="0f2adb0aee3de894ac4e28bfce85a54f5a80b06cb4118b374892a1248b02a395"
contraseña = "MiClaveSecreta123"
token_ok = generar_token(contraseña)


print("#########")
print(token_ok)
print("#########")




fecha_hora_actual = datetime.now()
fecha_formateada = fecha_hora_actual.strftime("%d-%m-%Y_%H-%M-%S")
# Generar clave de cifrado (¡Guárdala bien, la necesitas para descifrar!)
print("*******")
clave = Fernet.generate_key()
clave = "mAyHChS0owzG_M_wkQU_NTvrLPzxCRFYy1nfXHayag0="
clave_ok =clave.encode()
print(clave)
fernet = Fernet(clave)
print("*****")
print(fernet)
print("*****")


clave_genial="gAAAAABnxcsFIpVoie5W8gGi0xOX02lAI4Y22laVGdheSVwB1woO8dInTRgolbuuuK3W4Of7YTc21P1dCAwZkfaAHN92V7O_8N-f5jntLg4h520k3Rx0ro4="
clave_genial_2= clave_genial.encode()
print("-----------")
print(clave_genial)
print("-----------")
print(clave_genial_2)
print("-----------")

def encriptar(contraseña):
    return fernet.encrypt(contraseña.encode())

def desencriptar(token):
    return fernet.decrypt(token).decode()

# Uso
contraseña = "MiClaveSecreta123"
token = encriptar(contraseña)

print(f"Token cifrado: {token}")
print(f"Token cifrado: {fecha_formateada}")
print(f"Contraseña original: {desencriptar(token)}")

print("*******")
print(f"Contraseña desde texto: {desencriptar(clave_genial)}")
