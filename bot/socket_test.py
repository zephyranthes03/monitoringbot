import socket

def service_check(host:str, port:int) -> bool:
    # if type == "http" or type == "https":

    # elif type=="tcp":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)  # 1초 타임아웃 설정
        try:
            s.connect((host, port))
            s.close()
            return True
        except (socket.timeout, socket.error):
            return False
        
def alive_check(host:str="localhost", port:int=8080) -> bool:
    return service_check(host, port, "tcp" )

if __name__ == "__main__":
    print(alive_check())
    print(service_check("127.0.0.1", 443))
    print(service_check("proxy2.wynd.network", 4444))