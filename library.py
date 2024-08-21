from machine import Pin , I2C ,  RTC
from info import *
import tm1637 #Display
import bme280 #Sensor
import ds3231 #Reloj
import dlog #

# Funciones
def config():   #configuración I2C
    i2c = I2C(0, scl=Pin(1, Pin.OPEN_DRAIN, Pin.PULL_UP),
              sda=Pin(0, Pin.OPEN_DRAIN, Pin.PULL_UP), freq=100000)
    print('i2c:', i2c.scan() )
    rtc = RTC()
    return i2c, rtc
    
def format_date(date, utc=0):
    #extrae info de tupla
    date = date[0:3] + date[4:7]
    #convierte UTC
    utc = '{:+03d}'.format(utc)
    #convirtiendo a cadena con formato
    date_str = [str(date[0])] +\
            ["{:02d}".format(e) for e in date[1:]]
    #uniendo 
    date_str = '-'.join(date_str[0:3]) + \
            'T'+':'.join(date_str[3:]) + utc
    return (date_str)

def update_RTC(rtc):
    wlan = dlog.wlan_connect(ssid, password)
    if wlan == None:
        YY, MM, DD,wday, hh, mm, ss, _ = ds3231.get_time(i2c)
        rtc.datetime( (YY, MM, DD, wday, hh, mm, ss, 0))
        print('No hay NTP, Reloj:', rtc.datetime())
        return None
    print(wlan.ifconfig())
    if dlog.get_date_NTP(['1.mx.pool.ntp.org', 'cronos.cenam.mx']) == True:
        ds3231.set_time(i2c)
        print('Reloj actualizado:', ds3231.get_time(i2c))
    else:
        YY, MM, DD,wday, hh, mm, ss, _ = ds3231.get_time(i2c)
        rtc.datetime( (YY, MM, DD, wday, hh, mm, ss, 0))
        print('No hay NTP, Reloj:', rtc.datetime())

    wlan.active(False)
    return True

def mide(i2c):
    data_str = []
    data_str = ','.join(data_str)
    sht_values = bme.values
    data_str += ','+sht_values[0]
    data_str += ','+sht_values[2]
    data_str += ','+sht_values[1]
    return data_str

def save(data, file_save):
    with open(file_save, 'a') as file:
        file.write(data +'\n')
    print("Datos guardados")

def send(data, wlan):
    timeout_send = 4.0
    #url de API
    url_server= "https://ruoa.unam.mx:8041/pm_api"
    #separa url, asume que incluye puerto y protocolo
    protoc, _, host = url_server.split('/',2)
    host, port = host.split(':')
    print('host:',host, port)
    wlan = dlog.wlan_connect(ssid, password)
    if wlan == None:
        print('No hay red!')
        return None
    addr2 = socket.getaddrinfo(host, port)[0][-1]
    #addr2 = ('132.248.8.29', 8041)

    if wlan.isconnected() == False:
        wlan = dlog.wlan_connect(ssid, password)
    if wlan != None:
        print('conectado a', ssid)
        print('Enviando datos instantaneos a', host, data)
        #sock_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock_send = socket.socket()
            sock_send.settimeout(timeout_send)
            sock_send.connect(addr2)
            print('connect')
            sock_send = ssl.wrap_socket(sock_send)
            sock_send.write(bytes('PUT /pm_api HTTP/1.1\r\n', 'utf8'))
            sock_send.write(bytes('Content-Length: %s\r\n' % (len(data)), 'utf8'))
            sock_send.write(bytes('Content-Type: text/csv\r\n\r\n', 'utf8'))
            sock_send.write(bytes(data, 'utf8'))
            print('send:', data)
            #sock_send.send(bytes('\r\n', 'utf8'))
            line =b''
            response=b''
            while line != b'0\r\n':
                line = sock_send.readline()
                print('line:', line)
                response+=line
            #response = sock_send.read(165)
            sock_send.close()
            if response!=b'':
                if response.split()[1] == b'201':
                    print('datos instantáneos recibidos')
            print('response:', response)
        except OSError:
            print ('Error en la conexión con el servidor ', host)
            if sock_send:
                sock_send.close()
                print('socket cerrado')
    else:
        print('No se pudo conectar a WiFi')
    wlan.active(False)
    
    
i2c, rtc = config()
bme = bme280.BME280(i2c=i2c)
