import ujson
import network
import time
import machine
from machine import Pin, Timer
from umqtt.simple import MQTTClient
from rgbkeypad import RGBKeypad

# import micropython # For debugging memory use

# print(micropython.mem_info())
file = open("config.json", "r")
config = ujson.load(file)
APP_DEBUG_ACTIVE = config['DEBUG']['active']

client_id = config['CLIENT']['name']
print("Client Id: " + client_id)
associate_id = config['ASSOCIATE']['name']
print("Associate Id: " + associate_id)

# region Config/Constants
# MQTT config stuff
mqtt_server = config['BROKER']['mqtt_server']
topic_root = 'availability-app'
# Pound symbol represents all subtopics from this point on - we can filter out subtopics in the listener/callback
mqtt_status_pub_topic_path = topic_root + '/' + client_id + '/status'
print(mqtt_status_pub_topic_path)
# Path of a publication where we want other associates to watch for requesting status updates
mqtt_request_associate_update_path = topic_root + '/' + client_id + '/request-update'
print(mqtt_request_associate_update_path)
# All associate sub-topics
mqtt_associate_status_sub_path = topic_root + '/' + associate_id + '/#'
print(mqtt_associate_status_sub_path)

client_status_mqtt_client = None

status = "UNKNOWN"
associate_status = "UNKNOWN"
asked_for_associate_update = False
associate_asked_for_update = False

associate_status_light_on = True
client_status_light_on = True

# Keypad color tuples
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
LED_OFF = (0, 0, 0)


# endregion


# region Functions that do shit
def mqtt_this_client_availability_handler(topic, message):
    global status  # Ensure we are updating a global here - this is because this is a callback
    print("Received message on topic: " + str(topic, 'utf-8') + ". Message: " + str(message, 'utf-8'))
    status = str(message, 'utf-8')
    # update_status_led()


def mqtt_associate_message_handler(topic, message):
    global associate_status, associate_asked_for_update
    print("Received status message from other Pi: " + str(topic, 'utf-8') + ". Message: " + str(message, 'utf-8'))
    # /meeting-status contains info about the associates status
    if "status" in str(topic, 'utf-8'):
        # First time running - ignore it, the update LED method will be called at the end of startup configuration
        if associate_status == "UNKNOWN":
            associate_status = str(message, 'utf-8')  # Just update the status
            return
        else:
            associate_status = str(message, 'utf-8')
            update_associate_status_led()
    # /status-check-result is the sub-topic that we use to request a status update or 'ping' for status
    elif "request-update" in str(topic, 'utf-8'):
        if not associate_asked_for_update:
            associate_asked_for_update = True


def update_status_led():
    global associate_asked_for_update
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
    if associate_asked_for_update:
        associate_asked_for_update = False


def update_associate_status_led():
    print("Updating Associate Status LED")
    print("Status is: " + associate_status)
    global asked_for_associate_update
    if asked_for_associate_update:
        asked_for_associate_update = False

    if associate_status == "AVAILABLE":
        keypad[3, 3].color = GREEN
    elif associate_status == "MODERATE":
        keypad[3, 3].color = YELLOW
    elif associate_status == "UNAVAILABLE":
        keypad[3, 3].color = RED
    else:
        print("Unknown other_status: " + associate_status)
        keypad[3, 3].color = LED_OFF


def publish_status(new_status):
    client_status_mqtt_client.publish(mqtt_status_pub_topic_path, new_status, True)


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
    client_status_mqtt_client.ping()


def request_associate_status_update():
    global asked_for_associate_update
    print("Sending 'please update status' message to associate")
    client_status_mqtt_client.publish(mqtt_request_associate_update_path, 'requesting-update')
    # flash_associate_status_light()
    if asked_for_associate_update is False:
        asked_for_associate_update = True


def flash_status_light(timer):
    global associate_asked_for_update, client_status_light_on
    if associate_asked_for_update:
        client_status_light_on = not client_status_light_on
        keypad[0, 3].brightness = client_status_light_on
    elif associate_asked_for_update is False and client_status_light_on is False:
        client_status_light_on = True
        keypad[0, 3].brightness = client_status_light_on


def flash_associate_status_light(timer):
    global associate_status_light_on
    if asked_for_associate_update:
        associate_status_light_on = not associate_status_light_on
        keypad[3, 3].brightness = associate_status_light_on
    elif asked_for_associate_update is False and associate_status_light_on is False:
        associate_status_light_on = True
        keypad[3, 3].brightness = associate_status_light_on


# endregion


# Configure Wi-Fi and other shit
# region Startup Config
led = Pin("LED", Pin.OUT)
led.off()  # Base state
# Setup Keypad and set color to white to indicate 'startup'
keypad = RGBKeypad()
keypad.brightness = 0.25
keypad.color = WHITE

# User override to enable Debug Mode is to press and hold key 3, 3 on startup
if APP_DEBUG_ACTIVE or keypad[3, 3].is_pressed():
    APP_DEBUG_ACTIVE = True
    keypad.get_key(0, 0).color = GREEN
# A shitty way to wait for user to boot
# Perhaps should only happen when a debug flag is set or something...
while APP_DEBUG_ACTIVE:
    if keypad.get_key(0, 0).is_pressed():
        keypad.color = GREEN
        break
    else:
        time.sleep_ms(200)

# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(config['WiFi']['name'], config['WiFi']['password'])
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
    # Get our client's last known status based on the persist bit set on status updates
    init_status_mqtt_client = MQTTClient(client_id, mqtt_server, keepalive=120)
    init_status_mqtt_client.connect()
    init_status_mqtt_client.publish("availability-app/pi-status", client_id + " is alive inside!")
    init_status_mqtt_client.set_callback(mqtt_this_client_availability_handler)
    init_status_mqtt_client.subscribe(mqtt_status_pub_topic_path)
    print("Waiting last message... Should get last status of this client soon")
    # Warning: Blocking call if needed, use check_msg instead but might require startup changes since it would be async
    init_status_mqtt_client.wait_msg()
    # Got last status, close this connection as it will be re-opened later for updates
    init_status_mqtt_client.disconnect()
    init_status_mqtt_client = None
    print("Got this client's previous availability status. Now getting other client status")
    client_status_mqtt_client = MQTTClient(client_id, mqtt_server, keepalive=120)
    client_status_mqtt_client.set_callback(mqtt_associate_message_handler)
    client_status_mqtt_client.connect()
    client_status_mqtt_client.subscribe(mqtt_associate_status_sub_path)
    # Get the last status of the associate
    client_status_mqtt_client.wait_msg()
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
update_associate_status_led()

# Configure a timer to ping and watch the status of the other client MQTT feed
mqtt_server_ping_timer = Timer(mode=Timer.PERIODIC, period=30000, callback=ping)
# Watchers for the flashing lights
status_light_watcher = Timer(mode=Timer.PERIODIC, period=1000, callback=flash_status_light)
associate_status_light_watcher = Timer(mode=Timer.PERIODIC, period=1000, callback=flash_associate_status_light)

# region Main
while True:
    for key in keypad.keys:
        client_status_mqtt_client.check_msg()
        # print(micropython.mem_info())
        if key.is_pressed():
            if key.x == 0 and key.y == 0 and (associate_asked_for_update or status != "AVAILABLE"):
                status = "AVAILABLE"
                publish_status("AVAILABLE")
                update_status_led()
                time.sleep_ms(200)
            elif key.x == 1 and key.y == 0 and (asked_for_associate_update or status != "MODERATE"):
                status = "MODERATE"
                publish_status("MODERATE")
                update_status_led()
                time.sleep_ms(200)
            elif key.x == 2 and key.y == 0 and (asked_for_associate_update or status != "UNAVAILABLE"):
                status = "UNAVAILABLE"
                publish_status("UNAVAILABLE")
                update_status_led()
                time.sleep_ms(200)
            elif key.x == 3 and key.y == 3:
                request_associate_status_update()
                time.sleep_ms(200)

# endregion
