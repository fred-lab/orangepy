import requests
import json


class LiveBox:
    headers = {
        "Authorization": "X-Sah-Login",
        "Content-Type": "application/x-sah-ws-4-call+json",
        "Connection": "close"
    }

    def __init__(self, password, ip_livebox="192.168.1.1", username="admin"):
        self.lb_api = f"http://{ip_livebox}/ws"
        self.username = username
        self.password = password
        self.context = {}
        self.cookies = {}

    def __enter__(self):
        self.get_context()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        print('logout')
        return self

    def get_context(self):
        try:
            print("Connect to Livebox....")
            self.cookies.clear()
            self.context.clear()

            body = json.loads(
                '{"service":"sah.Device.Information","method":"createContext","parameters":{"applicationName":"webui","username":"admin","password":"fPiYkMJ2"}}')
            response = requests.post(
                self.lb_api, data=json.dumps(body), headers=self.headers)
            data = response.json()

            if("errors" in data):
                print(data)
                for error in data["errors"]:
                    message = error["description"]
                    raise Exception(f"LiveBox API : {message}")
                return
            else:
                print(
                    f"Livebox authentication success ! Username : {data['data']['username']}")
                self.cookies = response.cookies.get_dict()
                self.context = data
        except ConnectionError as e:
            print(e)

    def get_wan_info(self):
        print('Get WAN info ...')
        try:
            if("contextID" in self.context['data']):
                body = json.loads(
                    '{"service":"NMC","method":"getWANStatus","parameters":{}}')
                contextID = self.context['data']['contextID']
                sessionCookies = self.cookies

                self.headers.update({
                    "X-Context": contextID,
                    "Authorization": "X-Sah " + contextID,
                })

                response = requests.post(self.lb_api, data=json.dumps(
                    body), headers=self.headers, cookies=self.cookies)

                self.wan_info = response.json()

        except ConnectionError as e:
            print(f"Error : {e}")

    def get_ip_wan(self):
        try:
            self.get_context()
            self.get_wan_info()
            return self.wan_info['data']['IPAddress']
        except Exception as e:
            print(e)
