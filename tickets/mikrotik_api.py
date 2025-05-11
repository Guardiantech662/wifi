from librouteros import connect
from librouteros.exceptions import LibRouterosError
import socket

def connect_router(host, username, password, port=8728):
    try:
        api = connect(
            username=username,
            password=password,
            host=host,
            port=port
        )
        print(f"Successfully connected to router {host}.")
        return api
    except socket.timeout as e:
        print(f"Connection timed out: {e}")
        return None
    except socket.gaierror as e:
        print(f"Address resolution error: {e}")
        return None
    except LibRouterosError as e:
        print(f"RouterOS API error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
