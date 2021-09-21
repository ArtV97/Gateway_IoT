import socket
import time
import requests
import sys

HOST = ''
PORT = 5555
HTTP = "https://shrouded-wave-12457.herokuapp.com/"
#HTTP = "http://localhost:3000/"
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
        destination = f"{HTTP}insert?sensor_id={sensor_id}&temperatura={average}&timestamp={begin_ts}"

        print("Fazendo request para: " + destination)
        BUFFER[local_ip].clear()
    r = requests.get(destination)
    if r.status_code != 200: print("Erro ao enviar para o servidor!")

def get_public_ip():
    endpoint = 'https://ipinfo.io/json'
    response = requests.get(endpoint, verify = True)

    if response.status_code != 200:
        print('Status:', response.status_code, 'Problem with the request. Exiting.')
        sys.exit(1)

    data = response.json()

    return data['ip']

def main(delta_time=30):
    public_ip = get_public_ip()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:  
        s.bind((HOST, PORT))
        print("Delta Time =", delta_time)
        print('Aguardando dados...' )
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

            if current_ts - begin_ts >= delta_time:
                begin_ts = None
                send_to_server(public_ip)

if __name__ == "__main__":
    argv = sys.argv[1:]
    if len(argv) == 1: main(int(argv[0]))
    else: main()
