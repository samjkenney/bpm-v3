import network
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led, LED
import machine
import rp2
import sys
import aioble
import bluetooth
import asyncio
import struct
from sys import exit

#Connect to Wi-Fi network
ssid = 'Jason Derulo' #Network name
password = 'losersonly'#Network password

# IAM = "Central" # Change to 'Peripheral' or 'Central'
IAM = "Peripheral"

if IAM not in ['Peripheral','Central']:
    print("IAM must be either Peripheral or Central")
    exit()

if IAM == "Central":
    IAM_SENDING_TO = "Peripheral"
else:
    IAM_SENDING_TO = "Central"

MESSAGE = f"Web Server Connecting."

# Bluetooth parameters
BLE_NAME = f"{IAM} - Web Server"  # You can dynamically change this if you want unique names
BLE_SVC_UUID = bluetooth.UUID(0x181A)
BLE_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)
BLE_APPEARANCE = 0x0300
BLE_ADVERTISING_INTERVAL = 2000
BLE_SCAN_LENGTH = 5000
BLE_INTERVAL = 30000
BLE_WINDOW = 30000

def encode_message(message):
    """ Encode a message to bytes """
    return message.encode('utf-8')

def decode_message(message):
    """ Decode a message from bytes """
    return message.decode('utf-8')

def send_data_task(connection, characteristic):
    """ Send data to the connected device """
    print("in send_data_task()")
    while True:
        if not connection:
            print("error - no connection in send data")
            continue

        if not characteristic:
            print("error no characteristic provided in send data")
            continue

        print(f"sending {MESSAGE}")

        try:
            msg = encode_message(MESSAGE)
            characteristic.write(msg)

            await asyncio.sleep(0.5)
            response = decode_message(characteristic.read())
            
            print(f"{IAM} sent: {message}, response {response}")
            if response == "True":
                return "ALERT"
            else:
                return "NO ALERT"
        except Exception as e:
            print(f"writing error {e}")
            continue

        # await asyncio.sleep(0.5)


async def receive_data_task(characteristic):
    """ Receive data from the connected device """
    while True:
        try:
            data = await characteristic.read()

            if data:
                print(f"{IAM} received: {decode_message(data)}")
                await characteristic.write(encode_message("Got it"))
                await asyncio.sleep(0.5)

        except asyncio.TimeoutError:
            print("Timeout waiting for data in {ble_name}.")
            break
        except Exception as e:
            print(f"Error receiving data: {e}")
            break

def get_connection():
    while True:
        connection = aioble.advertise(
            BLE_ADVERTISING_INTERVAL,
            name=BLE_NAME,
            services=[BLE_SVC_UUID],
            appearance=BLE_APPEARANCE)
        
        if connection:
            return connection
    

def peripheral_mode():
    """ Run the peripheral mode """
    print("running peripheral mode")
    # Set up the Bluetooth service and characteristic
    ble_service = aioble.Service(BLE_SVC_UUID)
    characteristic = aioble.Characteristic(
        ble_service,
        BLE_CHARACTERISTIC_UUID,
        read=True,
        notify=True,
        write=True,
        capture=True,
    )
    aioble.register_services(ble_service)

    print(f"{BLE_NAME} starting to advertise")

    while True:
        with await aioble.advertise(
            BLE_ADVERTISING_INTERVAL,
            name=BLE_NAME,
            services=[BLE_SVC_UUID],
            appearance=BLE_APPEARANCE) as connection:
            print(f"{BLE_NAME} connected to another device: {connection.device}")
            
            return send_data_task(connection, characteristic)
            
            
            # print(f"{IAM} disconnected")

def run_peripheral_mode():
    """ Run the peripheral mode """
    print("running peripheral mode")
    ble_service = aioble.Service(BLE_SVC_UUID)
    
    characteristic = aioble.Characteristic(
        ble_service,
        BLE_CHARACTERISTIC_UUID,
        read=True,
        notify=True,
        write=True,
        capture=True,
    )
    
    aioble.register_services(ble_service)
    
    print(f"{BLE_NAME} starting to advertise")
    
    connection = get_connection()
    
    print(connection)
    
    print(f"{BLE_NAME} connected to another device")
    

def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password) #update to include password if using a network with a password
    print(wlan.isconnected())
    while wlan.isconnected() == False:
        if rp2.bootsel_button() == 1:
            sys.exit()
        print('Waiting for connection...')
        pico_led.on()
        sleep(0.5)
        pico_led.off()
        sleep(0.5)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    pico_led.on()
    return ip

def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    print(connection)
    return connection

def mainWebpage():
     html = """
        <!DOCTYPE html>
        <html>
          <head>
            <style>
              *{
                font-family: 'Georgia', verdana;
                margin-right: 50px;
                margin-left: 50px;
                }

            input[type = "submit"]{
                height:200px;
                width:1000px;
                margin:25px;
                font-size:50px;
                background-color: #512FB5;
                color: white;
                border-radius: 40px;
                border-width: 5px;
                border-color: #150c2e;
            }

            .grid-container {
                 display: grid;  
                 place-items: center; 
                 align-items: center;
                }

            input[type = "submit"]:hover{
                background-color: #150c2e
            }

            h1 {
                font-size: 40px;
                display: grid;  
                place-items: center; 
                align-items: center;
            }

            h2{
                font-size: 32px;
            }

            p, li {
                font-size: 30px;
                line-height: 40px;
            }

            #main {
                height: 100px;
                width: 200px;
                margin: 10px;
                font-size: 40px;
                display: grid;  
                place-items: center; 
                align-items: center;
            }

            img{
                margin-bottom: 50px;
            }

            .instructions, .resources {
                margin-bottom: 50px;
            }

            .separator{
                margin: 50px;
                border-top: 2px dotted #512FB5;
                }
        </style>
        </head>
        <div class = "grid-container">
          <form>
          <input type = "submit" value = "Take a Narcan">
          </form>
        </div>
        <div class = "grid-container">
            <form method = "POST" action = "instructions.html">
            <input type = "submit" value = "Instructions">
            </form>
        </div>
        <div class = "grid-container">
            <form action="./resources">
            <input type="submit" value="Resources">
            </form>
        </div>
            </body>
            </html>
            """
     
     return str(html)

def instructionWebpage():
    html = f"""
    <!DOCTYPE html>
        <html>
            <head>
                <style>
                  *{
                    font-family: 'Georgia', verdana;
                    margin-right: 50px;
                    margin-left: 50px;
                    }

            input[type = "submit"]{
                height:200px;
                width:1000px;
                margin:25px;
                font-size:50px;
                background-color: #512FB5;
                color: white;
                border-radius: 40px;
                border-width: 5px;
                border-color: #150c2e;
            }

            .grid-container {
                 display: grid;  
                 place-items: center; 
                 align-items: center;
                }

            input[type = "submit"]:hover{
                background-color: #150c2e
            }

            h1 {
                font-size: 40px;
                display: grid;  
                place-items: center; 
                align-items: center;
            }

            h2{
                font-size: 32px;
            }

            p, li {
                font-size: 30px;
                line-height: 40px;
            }

            #main {
                height: 100px;
                width: 200px;
                margin: 10px;
                font-size: 40px;
                display: grid;  
                place-items: center; 
                align-items: center;
            }

            img{
                margin-bottom: 50px;
            }

            .instructions, .resources {
                margin-bottom: 50px;
            }

            .separator{
                margin: 50px;
                border-top: 2px dotted #512FB5;
            }
        </style>
    </head>
    <body>
    <div class = "grid-container">
          <img src = "instructions.jpg" alt="Instructions for administering Narcan" width = "955" height = "1236">
        </div>
        <div class="separator"></div>
    <section class = "instructions">
        <h1>Identify Overdose</h1>
        <ol>
            <li> Ask the person if they are okay.</li>
            <li> Shake their shoulders and firmly rub the middle of their chest.</li>
            <li> Lay the person on their back to recieve a dose of Narcan.</li>
        </ol>
    </section>
    <div class="separator"></div>
    <section class = "instructions">
        <h1> Administer Narcan</h1>
        <ol>
            <li> Remove Narcan from the box.</li>
            <li> Hold the Narcan with your thumb on the bottom of the plunger and you first and middle fingers on either side of the nozzle.</li>
            <li> Tilt the person's head back and provide support under the neck with your hand. Gently insert the tip of the nozzle into one nostril until your fingers on either side of the nozzle are against the bottom the person's nose.</li>
            <li> Press the plunger firmly.</li>
            <li> Remove the Narcan from the nostril after giving the dose. </li>
        </ol>
    </section>
    <div class="separator"></div>
    <section class = "instructions">
        <h1> Support and evaluate </h1>
        <ol>
            <li> Get emergency medical help right away.</li>
            <li> Move the person on their side, into a recovery position.</li>
            <li> If the person does not respond by waking up, to voice or touch, or is not breathing normally, another dose may be given every 2 to 3 minutes.</li>
            <li> Repeat step 2 every 2 to 3 minutes until the person responds or emergency medical help is received.</li>
        </ol>
    </section>
    <div class = "grid-container">
      <form method = "POST" action="./index.html">
        <input  type="submit" value="Main" id = "main" />
      </form>
    </div>
        
  </body>
  </html>
  """
    return str(html)

def resourcesWebpage():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
              *{
                font-family: 'Georgia', verdana;
                margin-right: 50px;
                margin-left: 50px;
                }

            input[type = "submit"]{
                height:200px;
                width:1000px;
                margin:25px;
                font-size:50px;
                background-color: #512FB5;
                color: white;
                border-radius: 40px;
                border-width: 5px;
                border-color: #150c2e;
            }

            .grid-container {
                 display: grid;  
                 place-items: center; 
                 align-items: center;
                }

            input[type = "submit"]:hover{
                background-color: #150c2e
            }

            h1 {
                font-size: 40px;
                display: grid;  
                place-items: center; 
                align-items: center;
            }

            h2{
                font-size: 32px;
            }

            p, li {
                font-size: 30px;
                line-height: 40px;
            }

            #main {
                height: 100px;
                width: 200px;
                margin: 10px;
                font-size: 40px;
                display: grid;  
                place-items: center; 
                align-items: center;
            }

            img{
                margin-bottom: 50px;
            }

            .instructions, .resources {
                margin-bottom: 50px;
            }

            .separator{
                margin: 50px;
                border-top: 2px dotted #512FB5;
                }
        </style>
    </head>
    <body<section class = "resources">
    <h1> After administering naloxone </h1>
    <h2> If they are independently breathing, put the person in recovery position: </h2>
    <ul>
        <li> Lay the person slightly on their side.</li>
        <li> Bend their knee.</li>
        <li> Turn their face to the side</li>
    </ul>
    <h2> Stay with them until medical services arrive </h2>
    <p> They may have opioid withdrawal symptoms when they wake up. These can include chills, nausea, and muscle aches. </p>
    <p> They may not remember what happened, and might be scared, nervous, restless, or upset. Keep them calm. </p>
<section>
    <div class="separator"></div>
<section class = "resources">
    <h1>Steve's Law</h1>
    <p> Under Minnesota's Good Samaritan Law, people who are receiving and providing help for someone experiencing a drug overdose are protected. </p>
    <p> Under this law, you are protected to call 911 to get help for an overdose, and administer naloxone (Narcan)</p>
    <p> Both the person having an overdose and the person providing help have limited protection from charges related to posession of drugs. </p>
    <p> Protection is given for: </p>
    <ul>
        <li> Up to 3 grams of heroin, cocaine or methamphetamine</li>
        <li> Up to 5 grams of fentanyl</li>
        <li>Up to 10 grams of other narcotics</li>
        <li>Up to 10 kilograms of marijuana</li>
    </ul>
    
</section>
<div class="separator"></div>
<p> Resources can be found online at<a href="https://nextdistro.org">nextdistro.org </a></p>

<div class = "grid-container">
    <form method = "POST" action="./index.html">
      <input  type="submit" value="Main" id = "main" />
    </form>
</div>
    </body>
    </html>
    """
    return str(html)
    

def serve(connection):
    #Start a web server
    print("serving")
    count = 0
    while True:
        print("in serve()'s while loop")
        run_peripheral_mode()
        print("ran peripheral mode")
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        print(request)
        if request == '/instructions.html':
            instructions = instructionWebpage()
            client.send(instructions)
        elif request == '/Main?':
            html = mainWebpage()
            client.send(html)
        elif request == '/resources?':
            html = resourcesWebpage()
            client.send(html)
        elif request == '/take':
            count = count + 1
            print(count)
            html = mainWebpage()
            client.send(html)       
        else:
            html = mainWebpage()
            client.send(html)
            client.close()
        
    
ip = connect()
connection = open_socket(ip)
serve(connection)
