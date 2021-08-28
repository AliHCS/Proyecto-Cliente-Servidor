# Librerias que utilizaremos
import socket
import sys
import Crypto
from Crypto.PublicKey import RSA
import binascii
from Crypto.Cipher import PKCS1_OAEP
import time

# Leemos desde línea de comandos el puerto y la IP
IPServidor = sys.argv[1]
puertoServidor = int(sys.argv[2])


# Clave pública y privada
randomNum = Crypto.Random.new().read
privateKey = RSA.generate(1024, randomNum)
publicKey = privateKey.publickey()

# Exportando key publica y privada
privateKey = privateKey.exportKey(format='DER')
publicKey = publicKey.exportKey(format='DER')

# Decodificando a ascii
privateKey = binascii.hexlify(privateKey).decode('utf8')
publicKey = binascii.hexlify(publicKey).decode('utf8')
#print(publicKey)

# Codificando solo la llave privada
privateKey = RSA.importKey(binascii.unhexlify(privateKey))

# Creamos una clave de decifrado
cipher = PKCS1_OAEP.new(privateKey)

# Iniciamos el socket
socketCliente = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
socketCliente.connect((IPServidor, puertoServidor))
print("Cliente iniciado")
contador = 2

# Mandamos la llave pública al Servidor
socketCliente.send(publicKey.encode(encoding = "ascii",errors = "ignore"))

flag = True
try:
    flag = True
    while flag:
        recibidoCipher = socketCliente.recv(1024) # Recibimos el mensaje cifrado
        recibido = cipher.decrypt(recibidoCipher) # Deciframos el mensaje con cipher
        print("-SERVIDOR:  ",recibido.decode()) # Mensajes del servidor
        enviar = input("\nENTRADA: ").upper().strip() # Seleccionamos la opción desde teclado
        socketCliente.send(enviar.encode(encoding = "ascii",errors = "ignore")) # Enviamos la opción elegida

        # Terminamos conexión
        if enviar == "SALIR":
            print("CONEXIÓN FINALIZADA")
            flag = False
except ValueError:
    print("Espera un momento ")

socketCliente.close()
