/v1/device/truck/history_location

from tms.openapi.interfaces import G7Interface
queries = {
    'plate_num': '鲁UG2802',
    'from': '2019-05-18 12:00:00',
    'to': '2019-05-19 12:00:00',
    'timeInterval': 
}
data = G7Interface.call_g7_http_interface(
    'VEHICLE_HISTORY_TRACK_QUERY',
    queries=queries
)
print(data)

{'lng': '117.79348935295947', 'lat': '37.72484860629941', 'speed': 76, 'course': 86, 'time': 1558152016000, 'distance': 63946},
{'lng': '117.80069426422479', 'lat': '37.72554070078583', 'speed': 77, 'course': 79, 'time': 1558152046000, 'distance': 64050},
{'lng': '117.80777492352955', 'lat': '37.72687071397355', 'speed': 76, 'course': 73, 'time': 1558152076000, 'distance': 64246},
{'lng': '117.81407633528586', 'lat': '37.72848007798489', 'speed': 58, 'course': 74, 'time': 1558152106000, 'distance': 58469},
{'lng': '117.81537499698462', 'lat': '37.728660813213814', 'speed': 60, 'course': 85, 'time':1558152113000, 'distance': 11643},
{'lng': '117.81594750615949', 'lat': '37.72866681124604', 'speed': 61, 'course': 91, 'time': 1558152116000, 'distance': 5054},
{'lng': '117.81652000330979', 'lat': '37.728622807603244', 'speed': 60, 'course': 97, 'time': 1558152119000, 'distance': 5076},
{'lng': '117.81707852594688', 'lat': '37.72853382682587', 'speed': 59, 'course': 104, 'time': 1558152122000, 'distance': 5026},
{'lng': '117.81761409835491', 'lat': '37.72839988527913', 'speed': 59, 'course': 109, 'time': 1558152125000, 'distance': 4954}, 