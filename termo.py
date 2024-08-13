'''
Sensor de T, P y RH
Código principal

autor: Citlally Galeana

'''
from machine import Pin , I2C ,  RTC
from time import sleep, time, localtime, mktime, sleep_ms, ticks_ms, ticks_diff
from library import * #Biblioteca de funcione 
import network
import tm1637 #Display

ap = network.WLAN(network.AP_IF) # create access-point interface
ap.config(ssid='TPHR0000') # set the SSID of the access point
ap.config(max_clients=2) # set how many clients can connect to the network
ap.active(True)         # activate the interface
#if (pin) == 1:
ID = 'TPHR_001'
print('ID:' , ID)    
# definición de intervalos en [segundos]
# intervalo de medición y  almacenamiento
Δs = 10
ΔRTC = 60*60*1 # intervalo de actualización de RTC
utc = -6
i2c, rtc = config()
bme = bme280.BME280(i2c=i2c)
tm = tm1637.TM1637(clk=Pin(3), dio=Pin(4))
time_now = time() # tiempo actual (hora y fecha)
time_mide = time_now  # tiempo de siguiente medición
time_RTC = time_now #tiempo de siguiente update RTC
update_RTC(rtc)
secs = time()-6*3600
local_time = localtime(secs)
while True:
    time_now = time()
    start = ticks_ms()

    if time_RTC <= time_now:
        time_RTC += ΔRTC
        print('RTC update:', time_now)

    if time_mide <= time_now:
        time_mide += Δs
        #lectura de fecha
        date = rtc.datetime()
        #conversión de fecha
        date_str = format_date(date, utc= utc)
        filename = ID + '_' + date_str[:10]+'.csv'
        data_str = ID + "," + date_str + mide(i2c)
        print(filename)
        print(data_str)  
        save(data_str, filename)
        #send(data_str, wlan)
        tm.temperature(int(data_str.split(',')[2][0:2])) #Temperatura (XX°C)
        sleep(2)
        tm.show(data_str.split(',')[4][0:3]+'P') #Presión (XXXP)
        sleep(2)
        tm.show(data_str.split(',')[3][0:2]+'HR') #Humedad (XXHr)
        sleep(2)
        tm.numbers(local_time[3],local_time[4]) #Hora (HH:MM)
        sleep(2)
        tm.scroll(data_str[17:19] + data_str[13:17] + data_str[9:13]) #Fecha (DD-MM-AAAA)
        sleep(2)
        tm.show('    ')