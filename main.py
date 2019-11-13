###############################################################################
# Mini Web Server
#
# Created by Zerynth Team 2015 CC
# Authors: G. Baldi, D. Mazzei
###############################################################################

# import streams & socket
import streams
import socket

# import the wifi interface
from wireless import wifi

# the wifi module needs a networking driver to be loaded
# in order to control the board hardware.
# FOR THIS EXAMPLE TO WORK, A NETWORK DRIVER MUST BE SELECTED BELOW

# uncomment the following line to use the CC3000 driver (Particle Core or CC3000 Wifi shields)
# from texas.cc3000 import cc3000 as wifi_driver

# uncomment the following line to use the BCM43362 driver (Particle Photon)
# from broadcom.bcm43362 import bcm43362 as wifi_driver
from espressif.esp32net import esp32wifi as wifi_driver

streams.serial()
new_resource("index.html")

# init the wifi driver!
# The driver automatically registers itself to the wifi interface
# with the correct configuration for the selected board
wifi_driver.auto_init()
# use the wifi interface to link to the Access Point
# change network name, security and password as needed
print("Establishing Link...")
try:
    # FOR THIS EXAMPLE TO WORK, "Network-Name" AND "Wifi-Password" MUST BE SET
    # TO MATCH YOUR ACTUAL NETWORK CONFIGURATION
    wifi.link("Net-One",wifi.WIFI_WPA2,"88888888")
except Exception as e:
    print("ooops, something wrong while linking :(", e)
    while True:
        sleep(1000)

# Yes! we are connected
print("Linked!")

# Let's print our ip, it will be needed soon
info = wifi.link_info()
print("My IP is:",info[0])

# Now let's create a socket and listen for incoming connections on port 80
sock = socket.socket()
sock.bind(80)
sock.listen()


while True:
    try:
        # Type in your browser the board ip!
        print("Waiting for connection...")
        # here we wait for a connection
        clientsock,addr = sock.accept()
        print("Incoming connection from",addr)
        
        # yes! a connection is ready to use
        # first let's create a SocketStream
        # it's like a serial stream, but with a socket underneath.
        # This way we can read and print to the socket
        client = streams.SocketStream(clientsock)
        
        # let's read all the HTTP headers from the browser
        # stop when a blank line is received
        line = client.readline()
        while line!="\n" and line!="\r\n":
            line = client.readline()
        print("HTTP request received!")
        
        f = open("resource://index.html",'rb')

        html_response = "HTTP/1.1 200 OK\r\n"
        html_response += "Content-Type: text/html\r\n"
        html_response += "Content-Length: "+str(f.size)+"\r\n"
        html_response += "Connection: close\r\n\r\n"

        clientsock.send(html_response)

        offset = 0
        chunk = 32
        while True:
            data = f.read(chunk)
            if data:
                if '@' in data:
                    data = data.replace('@',str(random(0,100)))
                    clientsock.send(data)
                    offset += chunk
                    f.seek(offset)
            else:
                break

        clientsock.close()

    except Exception as e:
        print("ooops, something wrong:",e)
