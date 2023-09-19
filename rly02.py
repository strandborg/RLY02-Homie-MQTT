import os
import serial
import time
from homie.device_base import Device_Base
from homie.node.node_base import Node_Base

from homie.node.property.property_switch import Property_Switch

# Get MQTT broker configuration from environment variables

mqtt_settings = {
    'MQTT_BROKER' : os.environ.get("MQTT_BROKER_HOST", "localhost"),
    'MQTT_PORT' : int(os.environ.get("MQTT_BROKER_PORT", 1883)),
    'MQTT_USERNAME' : os.environ.get("MQTT_BROKER_USER", None),
    'MQTT_PASSWORD' : os.environ.get("MQTT_BROKER_PASS", None)
}

device_id = os.environ.get("MQTT_DEVICE_ID", "rly02")
device_name = os.environ.get("MQTT_DEVICE_NAME", "USB Relay RLY-02")

ser_port = os.environ.get("RELAY_DEVICE", "/dev/ttyRELAY")
mqtt_publish_interval = os.environ.get("MQTT_PUBLISH_INTERVAL", 120)


def control_relay(serial_port, relay_number, action):
    # Map relay numbers to command bytes
    relay_commands = {
        1: 0x65 if action == "ON" else (0x6F if action == "OFF" else 0x5B),
        2: 0x66 if action == "ON" else (0x70 if action == "OFF" else 0x5B),
    }

    try:
        # Send the appropriate relay control or query command
        if relay_number in relay_commands:
            # Create a serial connection
            ser = serial.Serial(serial_port, baudrate=9600, timeout=1)

            command_byte = relay_commands[relay_number]
            ser.write(bytes([command_byte]))

            if action == "query":
                # Read the response
                response = int.from_bytes(ser.read(1), 'big')
                response = (response >> (relay_number - 1)) & 0x1

                return 'ON' if response == 1 else 'OFF'

            # Close the serial connection
            ser.close()

        else:
            print(f"Invalid relay number: {relay_number}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

class USB_Relay(Device_Base):
    def __init__(
        self,
        device_id=None,
        name=None,
        homie_settings=None,
        mqtt_settings=None,
    ):

        super().__init__(device_id, name, homie_settings, mqtt_settings)

        node = Node_Base(self, "controls", "Controls", "controls")
        self.node = node
        self.add_node(node)

        self.relay1 = Property_Switch(self.node, id="port01", name="Relay Port 1", set_value=lambda newVal: control_relay(ser_port, 1, newVal))
        self.node.add_property(self.relay1)
        self.relay2 = Property_Switch(self.node, id="port02", name="Relay Port 2", set_value=lambda newVal: control_relay(ser_port, 2, newVal))
        self.node.add_property(self.relay2)

        self.start()    

    def update(self):
        self.relay1.value = control_relay(ser_port, 1, "query")
        self.relay2.value = control_relay(ser_port, 2, "query")


def main():

    relay = USB_Relay(name=device_name, device_id=device_id, mqtt_settings=mqtt_settings)

    while True:
        relay.update()
        time.sleep(mqtt_publish_interval)

if __name__ == "__main__":
    main()
