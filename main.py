import network
import time
import machine
from machine import Pin
from umqtt.simple import MQTTClient
from rgbkeypad import RGBKeypad

# region Config/Constants
# MQTT config stuff
mqtt_server = 'SERVER_NAME_HERE'  ## TODO: Change to actual server location when the time comes
client_id = 'pippy-pie'
topic_pub = 'availability-app/meeting-status/pippy-pie'
status = "AVAILABLE"
# Keypad color tuples
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# topic_template_msg = 'Hey there, my current status is '
# endregion

# region Functions that do shit
def mqtt_connect():
    print("creating client")
    client = MQTTClient(client_id, mqtt_server, keepalive=60)
    print("connecting")
    client.connect()
    print('Connected to %s MQTT Broker' % (mqtt_server))
    return client


# TODO: maybe "restart" instead
def reconnect():
    print('Failed to connect to the MQTT Broker. Reconnecting...')
    time.sleep(5)
    machine.reset()


def led_user_alert():
    led.on()
    time.sleep(2.5)
    led.off()
    time.sleep(1)
    led.on()
    time.sleep(2.5)
    led.off()
    time.sleep(1)
    led.on()
    time.sleep(2.5)
    led.off()


def mqtt_this_client_availability_handler(topic, message):
    global status # Ensure we are updating a global here - this is because this is a callback
    print("Received message on topic: " + str(topic, 'utf-8') + ". Message: " + str(message, 'utf-8'))
    status = str(message, 'utf-8')
    # update_status_led()


def update_status_led():
    print("Updating status LED")
    print("Status is: " + status)
    if status == "AVAILABLE":
        keypad[0, 3].color = GREEN
    elif status == "MODERATE":
        keypad[0, 3].color = YELLOW
    elif status == "UNAVAILABLE":
        keypad[0, 3].color = RED

def publish_status(status):
    mqtt_client.connect()
    mqtt_client.publish(topic_pub, status, True)
    mqtt_client.disconnect()


def make_sad_face():
    keypad.color = (0, 0, 0)
    keypad.get_key(1, 0).color = RED
    keypad.get_key(2, 0).color = RED
    keypad.get_key(1, 2).color = RED
    keypad.get_key(2, 2).color = RED
    keypad.get_key(2, 2).color = RED
    keypad.get_key(0, 3).color = RED
    keypad.get_key(3, 3).color = RED

# endregion


# Configure Wi-Fi and other shit
# region Startup Config
led = Pin("LED", Pin.OUT)
led.off()  # Base state
# Setup Keypad and set color to white to indicate 'startup'
keypad = RGBKeypad()
keypad.brightness = 0.25
keypad.color = WHITE

keypad.get_key(0, 0).color = GREEN
# A shitty way to wait for user to boot
# Perhaps should only happen when a debug flag is set or something...
while True:
    if keypad.get_key(0, 0).is_pressed():
        keypad.color = GREEN
        break

# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("REPLACE_WITH_WIFI_NAME", "REPLACE_WITH_WIFI_PASSWORD")
time.sleep(5)  # Not really needed
if wlan.isconnected():
    print("Wifi connected successfully!")
else:
    print("An issue occurred while trying to connect to WiFf and so it is not currently connected.")

# Set 'status' key to current status
# keypad.get_key(0, 3).color = GREEN
# endregion

# Try to configure the mqtt client
try:
    mqtt_client = mqtt_connect()
    print("Bleh")
    mqtt_client.publish("availability-app/pi-status", client_id + " is alive inside!")
    print("Published alive status to MQTT!")
    mqtt_client.set_callback(mqtt_this_client_availability_handler)
    mqtt_client.subscribe(topic_pub)
    print("Waiting last message... Should get last status of this client soon")
    # Warning: Blocking call if needed, use check_msg instead but might require startup changes since it would be async
    mqtt_client.wait_msg()
    led.on()
except OSError as e:
    print("Failed to contact MQTT broker")
    make_sad_face()
    time.sleep(120)
    machine.reset()

# Note: the above does not prevent the app from starting (for now) but the LED will be ON if the mqtt client is
# successful

# Configure keypad colors now that we are nearing completion of setup
keypad.clear()
keypad.brightness = 1
# keypad.get_key(3, 3).color = (255, 255, 255)
# brightness = 1
keypad.get_key(0, 0).color = GREEN  # Set first key in first row
keypad.get_key(1, 0).color = YELLOW  # Set second  key in first row
keypad.get_key(2, 0).color = RED  # Set third key in first row
update_status_led()  # by this time we will have received the message, and the status will be set to the right value

# region Main
while True:
    for key in keypad.keys:
        if key.is_pressed():
            if key.x == 0 and key.y == 0 and status != "AVAILABLE":
                status = "AVAILABLE"
                publish_status("AVAILABLE")
                update_status_led()
                time.sleep_ms(200)
            elif key.x == 1 and key.y == 0 and status != "MODERATE":
                status = "MODERATE"
                publish_status("MODERATE")
                update_status_led()
                time.sleep_ms(200)
            elif key.x == 2 and key.y == 0 and status != "UNAVAILABLE":
                status = "UNAVAILABLE"
                publish_status("UNAVAILABLE")
                update_status_led()
                time.sleep_ms(200)
            # elif key.x == 3 and key.y == 3:
            #     print("Connection status: ")
            #     print(wlan.isconnected())

# endregion
