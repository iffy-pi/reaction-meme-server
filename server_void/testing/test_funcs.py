import requests


def getServerURL() -> str:
    return 'http://127.0.0.1:5000'

def makeServerRoute(route:str) -> str:
    return f'{getServerURL()}/{route}'


def isServerReachable(serverURL) -> bool:
    try:
        resp = requests.get(serverURL)
        return resp.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
