import os
import subprocess
import time
from dotenv import load_dotenv
import requests
from liveboxapi import LiveBox
from cloudflare import Cloudflare


def print_ip(ip):

    filename = "/tmp/wan_ip.txt"
    f = open(filename, "w")
    f.write(ip)
    f.close()


def get_ip_from_file():
    filename = "/tmp/wan_ip.txt"
    if (os.path.exists(filename)):
        f = open(filename, "r")
        ip = f.read()
        f.close()
        return ip
    return False


def main():
    load_dotenv()
    password = os.getenv('PASSWORD')
    livebox_ip_lan = os.getenv('LIVEBOX_IP_LAN')

    api_token = os.getenv('CLOUDFLARE_API_TOKEN')
    api_email = os.getenv('CLOUDFLARE_API_EMAIL')
    domain = os.getenv('CLOUDFLARE_API_DOMAIN')

    try:
        is_live = requests.get(
            "http://"+livebox_ip_lan, headers={"Connection": "close"}).status_code == 200
    except ConnectionError as e:
        print(e)

    if(is_live):
        print("Livebox is Up !")
        print("Get WAN IP...")
        livebox = LiveBox(password)
        current_ip = livebox.get_ip_wan()
        print(f"Current WAN IP : {current_ip}")
        registered_ip = get_ip_from_file()

        if(current_ip == None):
            print('Livebox did not return a valid IP !')
            return False

        if(registered_ip != current_ip):
            try:
                cloudflare = Cloudflare(api_token, api_email, domain)
                zone = cloudflare.get_zone()
                dns_records = cloudflare.get_dns_record(zone)

                print("Check the IP for each DNS Record...")
                for record in dns_records:
                    if(record['content'] != current_ip and current_ip != None and record['type'] == 'A'):
                        print(
                            f"DNS {record['name']} not up-to-date with current IP. Start update...")
                        cloudflare.update_dns_record(
                            zone, record, current_ip)
                    else:
                        print(
                            f"DNS {record['name']} up-to-date with current IP.")
            except:
                print("Error occured while updating Cloudflare API")

            print('DNS records from Cloudflare are up-to-date :) ')

            print("Update registered WAN IP....")
            print_ip(current_ip)
            registered_ip = get_ip_from_file()
            print(f"Registered WAN IP is now : {registered_ip}")
        else:
            print(
                "Registered WAN IP and current WAN IP are the same. Nothing to update.")
    else:
        print("Livebox is Down. Wait for livebox to boot....")

    print("Wait for change...")


if __name__ == "__main__":
    main()
