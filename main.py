import socket
import time
import requests

HOST = ''
PORT = 5555
HTTP = "https://shrouded-wave-12457.herokuapp.com/"
BUFFER_SIZE = 20
BUFFER = {}


def send_to_server(public_ip):
    average = 0
    begin_ts = 0
    
    for local_ip in BUFFER:
        begin_ts = time.strftime('%d-%m-%Y %H:%M:%S', time.gmtime(BUFFER[local_ip][0][0]-10800))
        for data in BUFFER[local_ip]:
            average += data[1]
    
        average /= len(BUFFER[local_ip])

        sensor_id = public_ip + "-" + local_ip
        destination = f"{HTTP}insert?SensorID={sensor_id}&Timestamp={begin_ts}&Temperatura={average}"

        print("Fazendo request para: " + destination)
        BUFFER[local_ip].clear()
    #r = requests.get(destination)
    #if r.status_code != 200: print("Erro ao enviar para o servidor!")

def get_public_ip():
    endpoint = 'https://ipinfo.io/json'
    response = requests.get(endpoint, verify = True)

    if response.status_code != 200:
        return 'Status:', response.status_code, 'Problem with the request. Exiting.'
        exit()

    data = response.json()

    return data['ip']

def main():
    public_ip = get_public_ip()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:  
        s.bind((HOST, PORT))
        print('Aguardando dados ...' )
        begin_ts = None
        while (1):
            message, address = s.recvfrom(8192)
            local_ip = address[0]
            
            if begin_ts is None: begin_ts = int(time.time())

            current_ts = int(time.time())

            message = message.decode("utf-8")
            sensor_data = message.split(",")

            data = (current_ts, float(sensor_data[-1])) # (timestamp, temperatura)

            if local_ip in BUFFER: BUFFER[local_ip].append(data)
            else: BUFFER[local_ip] = [data]

            #if len(BUFFER[local_ip]) == BUFFER_SIZE: send_to_server(local_ip)
            if current_ts - begin_ts >= 5:
                begin_ts = None
                send_to_server(public_ip)

if __name__ == "__main__":
    main()