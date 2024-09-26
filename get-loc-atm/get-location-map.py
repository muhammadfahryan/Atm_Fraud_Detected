from datetime import datetime

import googlemaps

# Masukkan API Key Google Maps Anda
apiKey = 


# Masukkan API Key Google Maps Anda
gmaps = googlemaps.Client(key=apiKey)

# Keyword yang akan dicari
keyword= ['atm', 'bank', 'ATM', 'BSI']

# Menyimpan hasil pencarian
array_atm = []
for i in keyword:
    places_result = gmaps.places_nearby(
        location='5.5611009, 95.2936828', radius=100000, keyword=i, language='id')

    # menampilkan hasil pencarian
    for place in places_result['results']:
        # mencari latitude dan longitude
        lat = place['geometry']['location']['lat']
        long = place['geometry']['location']['lng']

        # menyimpan nama dan koordinat
        origin = (lat, long)
        nama_tempat = place['name']
        array_tempat = [nama_tempat, origin]

        # menambahkan ke array
        array_atm.append(array_tempat)


# Mode transportasi
modes = ['driving', 'walking']

# Membuka file output.txt
f = open("output.txt", "a")
for nama_atm in array_atm:
    for nama_atm2 in array_atm:
        if nama_atm != nama_atm2:
            origin = nama_atm[1]
            destination = nama_atm2[1]
            departure_time = datetime.now()
            for mode in modes:
                result = gmaps.distance_matrix(origin, destination, mode=mode, departure_time=departure_time)
                try:
                    time = result['rows'][0]['elements'][0]['duration']['text']
                    distance = result['rows'][0]['elements'][0]['distance']['text']
                    if mode == 'driving':
                        mode = 'mobil'
                    else :
                        mode = 'jalan kaki'

                    # outut to file and add new line
                    f.write("dari " + nama_atm[0] + str(nama_atm[1]) + 
                            " ke " + nama_atm2[0]+ str(nama_atm2[1]) +
                            " dengan "+ mode + " waktu tempuh " + time + 
                            " dan jarak " + distance +"\n" )

                except :
                    f.write("dari " + nama_atm[0] + str(nama_atm[1]) + 
                            " ke " + nama_atm2[0]+ str(nama_atm2[1]) +
                            " dengan "+ mode + " tidak bisa dilalui"+"\n")

f.close()