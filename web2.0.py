from machine import Pin
import network
import usocket as socket
import ure
import time
from html import html

red = Pin(0, Pin.IN, Pin.PULL_UP)
print(red.value())

# Configurar el ESP32 como un punto de acceso (Access Point)
print('Iniciando configuración wifi')
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='ESP32')

while ap.active() == False:
    pass
print('Acces point activo')
print('Dirección IP:', ap.ifconfig()[0])

def handle_request(client):
    request = client.recv(1024)
    request = str(request)
    print("Solicitud de cliente:")
    print(request)
    
    if 'POST /config' in request:
        ssid = ''
        password = ''
        try:
            ssid = ure.search(r'ssid=([^&]*)&', request).group(1)
            password = ure.search(r'password=([^&]*)', request).group(1)
            ssid = ssid.replace('%3F', '?').replace('%21', '!').replace('%23', '#').replace('%24', '$').replace('%25', '%').replace('%26', '&').replace('%27', "'").replace('%28', '(').replace('%29', ')').replace('%2A', '*').replace('%2B', '+').replace('%2C', ',').replace('%2D', '-').replace('%2E', '.').replace('%2F', '/')
            password = password.replace('%3F', '?').replace('%21', '!').replace('%23', '#').replace('%24', '$').replace('%25', '%').replace('%26', '&').replace('%27', "'").replace('%28', '(').replace('%29', ')').replace('%2A', '*').replace('%2B', '+').replace('%2C', ',').replace('%2D', '-').replace('%2E', '.').replace('%2F', '/')
        except:
            pass

        response = "Conectando a la red WiFi..."
        client.send('HTTP/1.1 200 OK\r\n')
        client.send('Content-Type: text/html\r\n')
        client.send('Connection: close\r\n\r\n')
        client.sendall(response)
        
        client.close()
        
        if ssid and password:
            print('Intentando conectar a la red WiFi:')
            print('SSID:', ssid)
            print('Contraseña:', password)
            
            sta = network.WLAN(network.STA_IF)
            sta.active(True)
            sta.connect(ssid, password)
            
            start = time.ticks_ms()
            while not sta.isconnected() and time.ticks_diff(time.ticks_ms(), start) < 30000:
                time.sleep(1)
                print('.', end='')
            
            if sta.isconnected():
                print('\nConectado a la red WiFi')
                print('IP:', sta.ifconfig()[0])
            else:
                print('\nNo se pudo conectar a la red WiFi')
    else:
        client.send('HTTP/1.1 200 OK\r\n')
        client.send('Content-Type: text/html\r\n')
        client.send('Connection: close\r\n\r\n')
        client.sendall(html)
        client.close()
        print('saliendo')

# Crear un socket y escuchar conexiones
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print('Servidor web en ejecución...')

while True:
    cl, addr = s.accept()
    print('Conexión desde:', addr)
    handle_request(cl)
