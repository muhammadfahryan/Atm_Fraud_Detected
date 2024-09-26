import csv,re
from geopy.geocoders import Nominatim

def get_street_name_from_coordinates(latitude, longitude):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.reverse((latitude, longitude), exactly_one=True)

    if location:
        address = location.raw.get("address", {})
        street_name = address.get("road")
        return street_name

    return None
def read_file(file_name):
    with open(file_name, 'r') as f:
        return f.readlines()

if __name__ == '__main__':
    f = open('C:/Users/Sakuragi Hanamichi/Documents/FraudDetection_ATMACEH-main/get-loc-atm/output.txt', 'r')
    lines = f.readlines()

    nama_atm_pattern = r'ATM\s([^\(]+)'
    lokasi_atm_pattern = r'\(([\d\.,\s]+)\)'

    array_atm_line_to_csv = []
    for idx, line in enumerate(lines):
        if idx == 158:
            break
        # line remove \n
        line = line.strip()
        if idx % 2 == 0:
            line = line.split('ke ')[1]
            nama_atm_match = re.search(nama_atm_pattern, line)
            lokasi_atm_match = re.search(lokasi_atm_pattern, line)
            if nama_atm_match and lokasi_atm_match:
                nama_atm = nama_atm_match.group(1)
                lokasi_atm = lokasi_atm_match.group(1)
                # Replace space with none
                lokasi_atm = lokasi_atm.replace(' ', '')
                lokasi_atm = lokasi_atm.split(',')
                latitude = lokasi_atm[0]
                longitude = lokasi_atm[1]
                nama_jalan = get_street_name_from_coordinates(latitude, longitude)
                if nama_jalan:
                    array_atm_line_to_csv.append([latitude,longitude,nama_atm,nama_jalan])
                else:
                    array_atm_line_to_csv.append([latitude,longitude,nama_atm,''])

    with open('C:/Users/Sakuragi Hanamichi/Documents/FraudDetection_ATMACEH-main/get-loc-atm/output.txt', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(array_atm_line_to_csv)