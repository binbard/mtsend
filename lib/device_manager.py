import globals
from globals import mprint
from models.device import Device, DeviceType
import time
import threading

class DeviceManager():
    def __init__(self):
        self.devices: dict[str, Device] = {}
        self.on = True
    
    def add_device(self, ip, name, admin=False):
        if admin:
            self.devices[ip] = Device(ip, name, DeviceType.ADMIN, 0)
        else:
            self.devices[ip] = Device(ip, name, DeviceType.CLIENT, 0)
    
    def remove_device(self, ip: str):
        del self.devices[ip]
    
    def get_devices(self):
        return self.devices.values()
    
    def device_updater(self, ip, name):
        if ip in self.devices:
            self.devices[ip].name = name
            self.devices[ip].last_seen = time.time()
        else:
            self.add_device(ip, name)
    
    def device_remove_listener(self):
        while self.on:
            for device in self.devices.values():
                if device.last_seen < time.time() - globals.DEVICE_ONLINE_TIMEOUT:
                    self.remove_device(device.ip)
    
    def start(self):
        device_remove_thread = threading.Thread(target=self.device_remove_listener)
        device_remove_thread.start()
    
    def close(self):
        self.on = False
        globals.mprint('DeviceManager has been closed')