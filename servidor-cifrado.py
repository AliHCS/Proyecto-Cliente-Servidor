# Librerias que utilizaremos
import socket
import sys
from io import open
import Crypto
from Crypto.PublicKey import RSA
import binascii
from Crypto.Cipher import PKCS1_OAEP
import time
import itertools
import threading

done = False
# Animación de espera
def animate():
    for c in itertools.cycle(['....','.......','..........','............']):
        if done:
            break
        sys.stdout.write('\rESPERANDO CONEXIÓN DEL CLIENTE '+c)
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\r-----CONEXIÓN ESTABLECIDA-----\n')

direccionServidor = "localhost"
puertoServidor = int(sys.argv[1])
# Conección con los sockets
socketServidor = socket.socket(socket.AF_INET,socket.SOCK_STREAM);
socketServidor.bind( (direccionServidor, puertoServidor) )
socketServidor.listen()
print("Servidor Iniciado") # Mensaje que se inicio el servidor

# La animación se ejecuta hasta que un cliente se conecte
t = threading.Thread(target=animate)
t.start()
socketConexion, addr = socketServidor.accept()
done = True

# Reciviendo la llave publica del cliente
key = socketConexion.recv(1024).decode(encoding = "ascii",errors = "ignore")

# Codificando solo la llave publica
publicKey  = RSA.importKey(binascii.unhexlify(key))
cipher = PKCS1_OAEP.new(publicKey)

flag = True
#Bucle infinito
while flag:
    # Mostramos el menu disponible
    menu = """\n-----MENU-----
--CONSULTA
--DEPOSITAR (monto)
--RETIRO (monto)
--SALIR
-------------"""
    # Ciframos y codificamos el mensaje antes de enviar
    menu = menu.encode()
    menuCipher = cipher.encrypt(menu)

    socketConexion.send(menuCipher) # Enviamos el menu al cliente de forma encode
    recibido = socketConexion.recv(1024)  # Esperamos la respuesta del Cliente
    opcion = recibido.decode(encoding = "ascii", errors = "ignore") # Pasamos la respuesta del cliente a cadena con decode
    print("Se recibio la opcion: ",opcion) # Mostramos que opcion escogio el cliente
    select = opcion.split(" ")

    if  select[0] == "CONSULTA" : # Si la opción que mando el cliente es CONSULTA entra en el if
        archivo = open("cuenta.txt", "r") # Abrimos el archivo como lectura (read)
        consulta = archivo.read() # Guardamos el archivo en la variable consulta
        consultaCadena = "".join(consulta) # Pasamos a cadena lo leido del archivo

        # Ciframos y codificamos el mensaje antes de enviar
        consultaCadena = consultaCadena.encode()
        consultaCipher = cipher.encrypt(consultaCadena)

        socketConexion.send(consultaCipher)  # Enviamos la cadena al cliente
        archivo.close() # Cerramos el archivo

    elif  select[0] == "DEPOSITAR": # Si la opcion que llego es deposito entra al if
        cantidad = int(select[1])

        archivo = open("cuenta.txt", 'r+' ) # Abro el archivo como lectura y escritura
        deposito = archivo.readlines() # Lee todas las lineas y las guarda como lista en deposito
        dinero = deposito[2] # Guardo la cantidad que tiene el archivo
        print("Saldo anterior: ",dinero)
        dineroFloat = float(dinero) # Paso la cantidad a flotante y la guardo en su variable
        dineroFloat = dineroFloat + cantidad # Realizo la suma  correspondiente al deposito
        dineroStr = str(dineroFloat) # Paso el monto final a string para poder escribir en el archivo

        deposito[2] = dineroStr # Escribo en la lista que remplazara al antiguo saldo
        print("Saldo nuevo: ",deposito[2])
        archivo.seek(0) # Se posiciona al principio de la linea
        archivo.writelines(deposito) # Escribe todo el texto de nuevo ya con las modificaciones
        archivo.close() # Cierra el archivo

        # Enviamos el saldo actual al Cliente
        actual = "Su saldo nuevo es de: $"+dineroStr
        actual = actual.encode()
        actualCipher = cipher.encrypt(actual)
        socketConexion.send(actualCipher)

    elif  select[0] == "RETIRO": # Si la opcion que llego es deposito entra al if
        cantidad = int(select[1])

        archivo = open("cuenta.txt", 'r+' ) # Abro el archivo como lectura y escritura
        deposito = archivo.readlines() # Lee todas las lineas y las guarda como lista en deposito
        dinero = deposito[2] # Guardo la cantidad que tiene el archivo
        print("Saldo anterior: ",dinero)
        dineroFloat = float(dinero) # Paso la cantidad a flotante y la guardo en su variable
        dineroFloat = dineroFloat - cantidad # Realizo la suma  correspondiente al deposito
        dineroStr = str(dineroFloat) # Paso el monto final a string para poder escribir en el archivo

        deposito[2] = dineroStr # Escribo en la lista que remplazara al antiguo saldo
        print("Saldo nuevo: ",deposito[2])
        archivo.seek(0) # Se posiciona al principio de la linea
        archivo.writelines(deposito) # Escribe todo el texto de nuevo ya con las modificaciones
        archivo.close() # Cierra el archivo

        # Enviamos el saldo actual al Cliente
        actual = "Su saldo nuevo es de: $"+dineroStr
        actual = actual.encode()
        actualCipher = cipher.encrypt(actual)
        socketConexion.send(actualCipher)

    # Se finaliza la conexión
    elif select[0] == "SALIR":
        print("CONEXIÓN FINALIZADA")
        flag = False

    # En caso de que el usuario no ingrese una opcion válida
    else:
        error = "ERROR: Ingrese una opcion valida."
        error = error.encode()
        errorCipher = cipher.encrypt(error)
        socketConexion.send(errorCipher)

socketConexion.close()
