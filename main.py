import requests
from requests.exceptions import HTTPError
import pygame.mixer
from time import sleep
from typing import Callable

# Initialize pygame mixer
pygame.mixer.init()
pygame.init()
SOUND_CHANNEL = pygame.mixer.Channel(0)  # Use single channel for all warnings

# Configuration
CONFIG = {
    'aoa_threshold': 20,
    'gear_speed_threshold': 500,
    'g_threshold': 8,
    'flaps_threshold': 700,
    'altitude_threshold': 600,
    'altitude_terrain': 400,
    'pitch_threshold': 10,
    'flaps_threshold_percent': 0.6,
    'minimum_speed_threshold': 333,
    'high_speed_low_alt': {
        'speed': 1300,
        'altitude': 1500
    },
    'speed_altitude_ranges': [
        {'min_alt': 0, 'max_alt': 1500, 'max_speed': 1280},
        {'min_alt': 1500, 'max_alt': 3000, 'max_speed': 1500},
        {'min_alt': 3000, 'max_alt': 5000, 'max_speed': 1700},
        {'min_alt': 5000, 'max_alt': 15000, 'max_speed': 2200}
    ]
}

class Warning:
    def __init__(self, check: Callable, sound_file: str):
        self.check = check
        self.sound_file = sound_file
        self._sound = None

    def play_sound(self):
        if SOUND_CHANNEL.get_busy():  # Check if channel is currently playing
            return
        if not self._sound:
            self._sound = pygame.mixer.Sound(self.sound_file)
        SOUND_CHANNEL.play(self._sound)

def check_aoa(data):
    return data["AoA, deg"] > CONFIG['aoa_threshold'] and data["TAS, km/h"] > 50

def check_gear_speed(data):
    return data["gear, %"] > 0.5 and data["TAS, km/h"] > CONFIG['gear_speed_threshold']

def check_flaps_speed(data):
    return (data["flaps"] > CONFIG['flaps_threshold_percent'] and 
            data["TAS, km/h"] > CONFIG['flaps_threshold'])

def check_terrain(data):
    return (feet_to_meters(data["altitude_hour"]) < CONFIG['altitude_terrain'] and 
            data["aviahorizon_pitch"] > CONFIG['pitch_threshold'])

def check_altitude(data):
    return (feet_to_meters(data["altitude_hour"]) < CONFIG['altitude_threshold'] and 
            data["aviahorizon_pitch"] > CONFIG['pitch_threshold'])

def check_g(data):
    return data["g_meter"] > CONFIG['g_threshold']

def check_minimum_speed(data):
    return (data["gear, %"] < 0.6 and 
            data["TAS, km/h"] < CONFIG['gear_speed_threshold'])

def check_speed_by_altitude(data):
    altitude = feet_to_meters(data["altitude_hour"])
    speed = data["TAS, km/h"]
    
    print(f"DEBUG: Checking speed {speed:.0f} at altitude {altitude:.0f}m", end='\r')
    
    for range_config in CONFIG['speed_altitude_ranges']:
        if range_config['min_alt'] <= altitude < range_config['max_alt']:
            print(f"\nDEBUG: In range {range_config['min_alt']}-{range_config['max_alt']}m, limit: {range_config['max_speed']} km/h")
            if speed > range_config['max_speed']:
                print(f"Altitude speed check triggered: {speed:.0f} > {range_config['max_speed']} at altitude {altitude:.0f}m")
                return True
    return False

warnings = [
    Warning(check_speed_by_altitude, "./sounds/MaximumSpeed.wav"),  # Move to first position
    Warning(check_aoa, "./sounds/AngleOfAttackOverLimit.wav"),
    Warning(check_gear_speed, "./sounds/GearUp.wav"),
    Warning(check_flaps_speed, "./sounds/MaximumSpeed.wav"),
    Warning(check_altitude, "./sounds/altitude.wav"),
    Warning(check_terrain, "./sounds/pullup.wav"),
    Warning(check_g, "./sounds/OverG.wav"),
    Warning(check_minimum_speed, "./sounds/minimumspeed.wav")
]

def feet_to_meters(feet):
    return 0.3048 * feet

def get_telemetry():
    state = requests.get("http://localhost:8111/state").json()
    indicators = requests.get("http://localhost:8111/indicators").json()
    indicators.update(state)
    return indicators

def main():
    while True:
        try:
            telemetry = get_telemetry()
            if "altitude_min" in telemetry:
                altitude = feet_to_meters(telemetry["altitude_hour"])
                print(f"TAS: {telemetry.get('TAS, km/h', 0):.0f} km/h, IAS: {telemetry.get('IAS, km/h', 0):.0f} km/h, ALT: {altitude:.0f}m", end='\r')
                
                for warning in warnings:
                    if warning.check(telemetry):
                        print()  # New line for debug messages
                        warning.play_sound()
                        break
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        sleep(0.5)

if __name__ == "__main__":
    main()
