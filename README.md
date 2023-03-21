# Availability App
A MicroPython application intended for deployment to Raspberry Pi Pico W. Utilizing an MQTT broker, allows multiple Pico Keypads to indicate a users "in a meeting" status (Red=in a meeting; Yellow=busy; Green=available)

### Required Hardware:
* Raspberry Pi Pico (W) Development Environment
  * Thonny IDE, Pycharm or similar
  * Standard firmware will do
* Raspberry Pi Pico W (x2)
  * Pimoroni Pico Keypad
* MQTT Broker
  * Can be a docker instance, or standalone deployment

## Getting Started
### Development
TODO

### Deploying
TODO

### How To Use
TODO

## Configuring A Local Docker MQTT Broker
Run the following command in Terminal, replace the path to the mosquitto.conf file as needed:

`docker run -it -d -p 1883:1883 -p 9001:9001 -v /location/of/local/mosquitto.conf:/mosquitto/config/mosquitto.conf eclipse-mosquitto`

Note: You might need to allow access to this port via your system firewall.