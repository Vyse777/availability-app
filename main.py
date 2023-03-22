import network
import time
import machine
from machine import Pin, Timer
from umqtt.simple import MQTTClient
from rgbkeypad import RGBKeypad

# region Config/Constants
# MQTT config stuff
mqtt_server = 'SERVER_NAME_HERE'
client_id = 'whippy-pie'
other_client_id = "pippy-pie"

topic_root = 'availability-app/meeting-status/'
topic_pub = topic_root + client_id
other_client_sub = topic_root+other_client_id

this_status_mqtt_client = None

status = "UNKNOWN"
other_status = "UNKNOWN"

# Keypad color tuples
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
# endregion


# region Functions that do shit
def mqtt_this_client_availability_handler(topic, message):
    global status  # Ensure we are updating a global here - this is because this is a callback
    print("Received message on topic: " + str(topic, 'utf-8') + ". Message: " + str(message, 'utf-8'))
    status = str(message, 'utf-8')
    # update_status_led()


def mqtt_other_client_availability_handler(topic, message):
    global other_status
    print("Received status message from other Pi: " + str(topic, 'utf-8') + ". Message: " + str(message, 'utf-8'))
    if "meeting-status" in str(topic, 'utf-8'):
        # First time running - ignore it, the update LED method will be called at the end of startup configuration
        if other_status == "UNKNOWN":
            other_status = str(message, 'utf-8')  # Just update the status
            return
        else:
            other_status = str(message, 'utf-8')
            update_other_status_led()


def update_status_led():
    print("Updating status LED")
    print("Status is: " + status)
    if status == "AVAILABLE":
        keypad[0, 3].color = GREEN
    elif status == "MODERATE":
        keypad[0, 3].color = YELLOW
    elif status == "UNAVAILABLE":
        keypad[0, 3].color = RED
    else:
        print("Unknown Status: " + status)


def update_other_status_led():
    print("Updating Other Status LED")
    print("Status is: " + other_status)
    if other_status == "AVAILABLE":
        keypad[3, 3].color = GREEN
    elif other_status == "MODERATE":
        keypad[3, 3].color = YELLOW
    elif other_status == "UNAVAILABLE":
        keypad[3, 3].color = RED
    else:
        print("Unknown other_status: " + other_status)


def publish_status(new_status):
    this_status_mqtt_client.publish(topic_pub, new_status, True)


def make_sad_face():
    keypad.color = (0, 0, 0)
    keypad.get_key(1, 0).color = RED
    keypad.get_key(2, 0).color = RED
    keypad.get_key(1, 2).color = RED
    keypad.get_key(2, 2).color = RED
    keypad.get_key(2, 2).color = RED
    keypad.get_key(0, 3).color = RED
    keypad.get_key(3, 3).color = RED


def ping(timer):
    print("Pinging mqtt broker")
    this_status_mqtt_client.ping()
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
    else:
        time.sleep_ms(200)

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
    init_status_mqtt_client = MQTTClient(client_id, mqtt_server, keepalive=120)
    init_status_mqtt_client.connect()
    init_status_mqtt_client.publish("availability-app/pi-status", client_id + " is alive inside!")
    init_status_mqtt_client.set_callback(mqtt_this_client_availability_handler)
    init_status_mqtt_client.subscribe(topic_pub)
    print("Waiting last message... Should get last status of this client soon")
    # Warning: Blocking call if needed, use check_msg instead but might require startup changes since it would be async
    init_status_mqtt_client.wait_msg()
    # Got last status, close this connection as it will be re-opened later for updates
    init_status_mqtt_client.disconnect()
    init_status_mqtt_client = None
    print("Got this client's previous availability status. Now getting other client status")
    this_status_mqtt_client = MQTTClient(client_id, mqtt_server, keepalive=120)
    this_status_mqtt_client.set_callback(mqtt_other_client_availability_handler)
    this_status_mqtt_client.connect()
    this_status_mqtt_client.subscribe(other_client_sub)
    this_status_mqtt_client.wait_msg()
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
update_other_status_led()

# Configure a timer to ping and watch the status of the other client MQTT feed
timer_ref = Timer(mode=Timer.PERIODIC, period=10000, callback=ping)

# region Main
while True:
    for key in keypad.keys:
        this_status_mqtt_client.check_msg()
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

# endregion
