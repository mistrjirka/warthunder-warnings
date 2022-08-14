import requests
from requests.exceptions import HTTPError
from time import sleep
url="http://localhost:8111/state"
url2="http://localhost:8111/indicators"
aoa_treshold = 10
gear_speed_treshold = 300
g_treshold = 8
speed_treshold = 1100
flaps_treshold = 700
altitude_treshold = 200
pitch_treshold = 10

def check_aoa(json_tel):
    if json_tel["AoA, deg"] > aoa_treshold:
        return True
    else: 
        return False

def check_gear_speed(json_tel):
    if json_tel["gear, %"] > 0 and json_tel["TAS, km/h"]>gear_speed_treshold:
        return True
    else: 
        return False

def check_speed(json_tel):
    if json_tel["TAS, km/h"]>speed_treshold:
        return True
    else: 
        return False
def check_flaps_speed(json_tel):
    if json_tel["flaps, %"] > 0 and json_tel["TAS, km/h"]>flaps_treshold:
        return True
    else: 
        return False

def check_altitude(json_tel):
    if json_tel["altitude_min"]<altitude_treshold and json_tel["aviahorizon_pitch"] > pitch_treshold:
        return True
    else: 
        return False
yell_warnings = [{
    "check": check_aoa,
    "playing": False,
    "sound": "" #path to sound file

},
{
    "check": check_gear_speed,
    "playing": False,
    "sound": "" #path to sound file
},{
    "check":check_speed,
    "playing": False,
    "sound": "" #path to sound file
},{
    "check": check_flaps_speed,
    "playing": False,
    "sound": "" #path to sound file
},
{
    "check": check_altitude,
    "playing": False,
    "sound": "" #path to sound file
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
        print("Entire JSON response")
        print(telemetry)

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    sleep(0.5)