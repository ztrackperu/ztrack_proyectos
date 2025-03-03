#from Crypto.Cipher import AES
from Cryptodome.Cipher import AES
#from Crypto.Random import get_random_bytes
import base64

# Generar clave AES de 32 bytes (256 bits)
def generar_clave():
    return get_random_bytes(32)  # 256 bits

# Generar IV de 16 bytes (128 bits)
def generar_iv():
    return get_random_bytes(16)  # 128 bits

# Función para encriptar un mensaje
def encriptar(mensaje, clave, iv):
    cipher = AES.new(clave, AES.MODE_CBC, iv)
    mensaje_bytes = mensaje.encode()

    # Relleno PKCS7 para que el mensaje sea múltiplo de 16 bytes
    padding_length = 16 - (len(mensaje_bytes) % 16)
    mensaje_bytes += bytes([padding_length] * padding_length)

    mensaje_cifrado = cipher.encrypt(mensaje_bytes)
    return base64.b64encode(mensaje_cifrado).decode()

# Función para desencriptar un mensaje
def desencriptar(mensaje_cifrado, clave, iv):
    cipher = AES.new(clave, AES.MODE_CBC, iv)
    mensaje_bytes = base64.b64decode(mensaje_cifrado)

    mensaje_desencriptado = cipher.decrypt(mensaje_bytes)

    # Eliminar el padding PKCS7
    padding_length = mensaje_desencriptado[-1]
    mensaje_desencriptado = mensaje_desencriptado[:-padding_length]

    return mensaje_desencriptado.decode()

# --- Ejemplo de uso ---
clave = generar_clave()  # Guardar de forma segura
iv = generar_iv()        # Guardar de forma segura

clave ="clave_secreta_32_bytes__"
iv = "1234567890123456"

mensaje_original = "Hola, API segura!"
mensaje_cifrado = encriptar(mensaje_original, clave, iv)
mensaje_descifrado = desencriptar(mensaje_cifrado, clave, iv)

print("Mensaje Original:", mensaje_original)
print("Mensaje Encriptado:", mensaje_cifrado)
print("Mensaje Desencriptado:", mensaje_descifrado)
