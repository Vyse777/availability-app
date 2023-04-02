# Availability App
A MicroPython application intended for deployment to a Raspberry Pi Pico W. Utilizing an MQTT broker, allows multiple (Client & Associate) Pico Keypads to indicate a users "in a meeting" status (Red=in a meeting; Yellow=busy; Green=available)

### Required Hardware:
* Raspberry Pi Pico (W) Development Environment
  * Thonny IDE, Pycharm or similar
  * Standard firmware will do
* Raspberry Pi Pico W (x2)
  * Pimoroni Pico Keypad (x2 one for each Pi)
* MQTT Broker
  * Can be a docker instance, or standalone deployment

# Getting Started
## Development
Development requires the setup of a Pico W. Follow the standard steps for flashing a Pico W with the latest/most stable version of MicroPython. At the moment, there is no requirement on a particular version.

After this you can develop in two ways:
1) Using PyCharm with the MicroPython plugin installed
   * This way requires a few hacks if you intend to debug/monitor your run, but it offers the best IDE/development experience. Obviously, because you get to use PyCharm.
2) Using Thonny
   * This is not as nice as PyCharm but provides the best known control over managing the Pico W. Thonny's MicroPython integration is by far superior to PyCharm's plugin. But the IDE leaves much to be desired.
   * I would highly recommend using Thonny to set up the Pico W's

Note: While you can technically have both IDEs, **do not** have both running! There can be only one COM connection to the Pico W and so having both IDEs running could cause issues with that communication.

Either way - the only requirements for the runtime is to have the UMQTT.simple package installed on each Pico W.
This can be easily installed using Thonny's "Manage Packages" feature. Or by simply downloading the latest UQMTT.simple version and including it when you flash the software to the Pico W.

You will also need a MQTT broker running/deployed. You can host one on Synology, Docker (in or out of Synology), locally, etc.
You only need to ensure it is reachable from devices on the same Lan as the Pico W's
#### Configuring A Local Docker MQTT Broker For Development
Run the following command in Terminal, replace the path to your mosquitto.conf file as needed:
`docker run -it -d -p 1883:1883 -p 9001:9001 -v /location/of/local/mosquitto.conf:/mosquitto/config/mosquitto.conf eclipse-mosquitto`
Note: You might need to allow access to this port via your system firewall.


## Deploying
Once the dependencies are installed, simply flash a config.json file & main.py to the board. 

* To configure the board for Client / Associate interaction: Add the contents of either the `pippy-config.json`/`whippy-config.json` files to the `config.json` file on each board (same location as the main.py file)
  * One will operate as a Client; The other as the Associate - just make sure not to use the same config for both Pi's
* Update the Wi-Fi JSON config for your access point's name and password
* Update the MQTT JSON config for your local server's DNS name; or full MQTT server URI

Flash all of this to each one of the Pico W's; One for Client (say, Pippy) and one for an Associate (say, Whippy).

Boot them and enjoy!

## How To Use / Operation Manual
### Startup:
When the Pi boots the keypad will turn all white to indicate startup.
All the following occurs during boot-up/startup:
1) The Pico W will attempt to connect to Wi-Fi
2) A connection attempt to the MQTT broker occurs
   1) Upon successful connection the Client/Associate will attempt to fetch its last known status from the MQTT broker
   2) NOTE: If this is a first time startup of the MQTT broker the last status will be empty. This will cause the Pi(s) to block/wait until a status has been published! Send a message to the MQTT broker of the startup status (preferably 'AVAILABLE') for both the Client & Associate. **You must ensure the `retain` bit is set, otherwise the broker will not store the last status in the subscription!**
3) When all of the above succeeds the keypad will enter user operation mode
   * The onboard LED on the Pico W will also illuminate to indicate the device has successfully booted as well

If an error occurs during startup the keypad will display a red sad face indicating a problem occurred.

### User Operation Mode:
The keypad will display 3 lights at the top in the first row, and two lights (first and last) on the bottom row.
   * The Top row lights are to set 'this' Pi's status. 
     * Green - "I am available"
     * Yellow - "I am about to enter a meeting, or I am working; But you can still bother me a bit"
     * Green - "I am available, and you can bug me"
   * The first light in th bottom row indicates 'this' Pi's (the Client) current status
   * The last light in the bottom row indicates the 'other' Pi's (the Associate) current status

### Ping for status update (v1.1.0):

Version 1.0.0 grants the user the ability to 'ping' the other keypad's status. This can be useful if you intend to scream, call, yell profanities, etc. but would like to 'confirm' that the other person is indeed free/not on a meeting beforehand. 

To do this:
1) Press the Associate Pi status indicator (bottom right button); The light will start to blink to indicate you requested an update
   * On the Associate's Pi ***their*** current status indicator light will blink to indicate that someone else asked for a status update. This will continue to blink until the user updates the status (by selecting a new status OR selecting whatever their current status is)
2) Once the other Pi/User selects a status, the blinking will stop to indicate an update occurred. Now the status indicator of the Associate could be either the same color it was before (meaning their status has not changed), or a different color (meaning they actually are in a new status and simply forgot to update it - good thing you pinged!)

Enjoy!
