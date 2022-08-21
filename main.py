import requests
from requests.exceptions import HTTPError
import winsound

from time import sleep
url="http://localhost:8111/state"
url2="http://localhost:8111/indicators"

aoa_treshold = 20
gear_speed_treshold = 340
g_treshold = 8
speed_treshold = 1100
flaps_treshold = 700
altitude_treshold = 600
altitude_terrain = 400
pitch_treshold = 10
flaps_treshhold_percent = 0.6
"""
aoa_treshold = 20
gear_speed_treshold = 280
g_treshold = 5
speed_treshold = 800
flaps_treshold = 350
altitude_treshold = 500
altitude_terrain = 300
pitch_treshold = 15
flaps_treshhold_percent = 0.19
"""
def check_aoa(json_tel):
    if json_tel["AoA, deg"] > aoa_treshold and json_tel["TAS, km/h"]> 50:
        print("AOA")
        return True
    else: 
        return False

def check_gear_speed(json_tel):
    if json_tel["gear, %"] > 0.5 and json_tel["TAS, km/h"]>gear_speed_treshold:
        print("gear speed")
        return True
    else: 
        return False

def check_speed(json_tel):
    if json_tel["TAS, km/h"]>speed_treshold:
        print("speed")
        return True
    else: 
        return False
def check_flaps_speed(json_tel):
    print(json_tel["flaps"],  " ", json_tel["TAS, km/h"])
    if json_tel["flaps"] > flaps_treshhold_percent and json_tel["TAS, km/h"]>flaps_treshold:
        print("flaps speed")
        return True
    else: 
        return False

def check_terrain(json_tel):
    if feetToMeters(json_tel["altitude_hour"])<altitude_terrain and json_tel["aviahorizon_pitch"] > pitch_treshold:
        print("terrain")
        return True
    else: 
        return False
def check_altitude(json_tel):
    print(feetToMeters(json_tel["altitude_hour"]), " ", json_tel["altitude_min"])
    if feetToMeters(json_tel["altitude_hour"])<altitude_treshold and json_tel["aviahorizon_pitch"] > pitch_treshold:
        print("altitude_hour")
        return True
    else: 
        return False
def check_g(json_tel):
    if json_tel["g_meter"]>g_treshold:
        print("gforce")
        return True
    else: 
        return False
def check_fuel(json_tel):
    if json_tel["g_meter"]>g_treshold:
        print("gforce")
        return True
    else: 
        return False
yell_warnings = [{
    "check": check_aoa,
    "playing": False,
    "sound": "./sounds/AngleOfAttackOverLimit.wav" #path to sound file

},
{
    "check": check_gear_speed,
    "playing": False,
    "sound": "./sounds/GearUp.wav" #path to sound file
},{
    "check":check_speed,
    "playing": False,
    "sound": "./sounds/MaximumSpeed.wav" #path to sound file
},{
    "check": check_flaps_speed,
    "playing": False,
    "sound": "./sounds/MaximumSpeed.wav"
},
{
    "check": check_altitude,
    "playing": False,
    "sound": "./sounds/altitude.wav"
},
{
    "check": check_terrain,
    "playing": False,
    "sound": "./sounds/pullup.wav"
},
{
    "check": check_g,
    "playing": False,
    "sound": "./sounds/OverG.wav"
}
]


def feetToMeters(feet):
    return 0.3048 * feet

while True:
    try:
        stateResponse = requests.get(url)
        indicatorsResponse  = requests.get(url2)
        stateResponse.raise_for_status()
        indicatorsResponse.raise_for_status()
        # access JSOn content
        indicators = indicatorsResponse.json()
        state = stateResponse.json()
        indicators.update(state)
        telemetry = indicators
        #print("Entire JSON response")
        #print(telemetry)
        if "altitude_min" in telemetry:
            for warn in yell_warnings:
                if warn["check"](telemetry):
                    print("playing")
                    winsound.PlaySound(warn["sound"], winsound.PlaySound()

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    sleep(0.5)
