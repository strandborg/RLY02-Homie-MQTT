import os
import serial
import time
from homie.device_switch import Device_Switch

# Get MQTT broker configuration from environment variables

mqtt_settings = {
    'MQTT_BROKER' : os.environ.get("MQTT_BROKER_HOST", "localhost"),
    'MQTT_PORT' : int(os.environ.get("MQTT_BROKER_PORT", 1883)),
    'MQTT_USERNAME' : os.environ.get("MQTT_BROKER_USER", None),
    'MQTT_PASSWORD' : os.environ.get("MQTT_BROKER_PASS", None)
}

device_id = os.environ.get("MQTT_DEVICE_ID", "usb-relay02")
device_name = os.environ.get("MQTT_DEVICE_NAME", "USB Relay02")

ser_port = os.environ.get("RELAY_DEVICE", "/dev/ttyRELAY")
mqtt_publish_interval = os.environ.get("MQTT_PUBLISH_INTERVAL", 120)


def control_relay(serial_port, relay_number, action):
    # Map relay numbers to command bytes
    relay_commands = {
        1: 0x65 if action == "on" else (0x6F if action == "off" else 0x5B),
        2: 0x66 if action == "on" else (0x70 if action == "off" else 0x5B),
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

class My_Relay(Device_Switch):
    def __init__(
        self, relay_index=1, device_id=None, name=None, homie_settings=None, mqtt_settings=None
    ):
        self.relay_index = relay_index
        super().__init__(device_id=device_id, name=name, homie_settings=homie_settings, mqtt_settings=mqtt_settings)
        
    def set_switch(self, onoff):
        if onoff == 'on' or onoff == '1' or onoff == 'ON' or onoff == 'true':
            action = 'on'
        else:
            action = 'off'

        control_relay(ser_port, self.relay_index, action)
        super().set_switch(onoff)

def main():

    relay1 = My_Relay(relay_index=1, name=f"{device_name}-1", device_id=f"{device_id}-1", mqtt_settings=mqtt_settings)
    relay2 = My_Relay(relay_index=2, name=f"{device_name}-2", device_id=f"{device_id}-2", mqtt_settings=mqtt_settings)

    while True:
        relay1.update_switch(control_relay(ser_port, 1, "query"))
        relay2.update_switch(control_relay(ser_port, 2, "query"))
        time.sleep(mqtt_publish_interval)

if __name__ == "__main__":
    main()
