import requests
import json

class Cloudflare:
    def __init__(self, api_token, api_email, domain):
        self.api_url = "https://api.cloudflare.com/client/v4/"
        self.api_token = api_token
        self.api_email = api_email
        self.domain = domain
        self.headers = {
            "Content-Type": "application/json",
            "X-Auth-Key": self.api_token,
            "X-Auth-Email": self.api_email,
        }

    def get_zone(self):
        endpoint = "zones"
        response = requests.get(self.api_url + endpoint,
                                headers=self.headers)

        zone = response.json()['result'][0]['id']
        return zone

    def get_dns_record(self, zone):

        endpoint = "zones/"

        url = f'{self.api_url}{endpoint}{zone}/dns_records'

        response = requests.get(url, headers=self.headers)

        return response.json()["result"]

    def update_dns_record(self, zone, record, ip):
        if(record['type'] == 'A'):
            endpoint = "zones/"
            url = f'{self.api_url}{endpoint}{zone}/dns_records/{record["id"]}'

            params = {
                "content": ip
            }

            response = requests.patch(
                url, data=json.dumps(params), headers=self.headers)

            if(response.status_code == 200):
                print(f"Record : {record['name']} updated successfully with ip {ip}")
            else:
                print(f"Record : {record['name']} failed to update with ip {ip}")
        else:
            print(f"Record : {record['name']} is type 'A'. Don't update.")

    def update_dns_records(self, zone, records, ip):
        for record in records:
            if(record['type'] == 'A'):
                self.update_dns_record(zone, record, ip)
