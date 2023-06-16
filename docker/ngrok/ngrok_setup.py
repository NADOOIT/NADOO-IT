import requests
import json
import os
import time  # <-- Add this import


def get_public_url():
    while True:  # <-- Add this loop
        try:
            res = requests.get("http://localhost:4040/api/tunnels")
            res.raise_for_status()
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
            print("Waiting for ngrok to become active...")
            time.sleep(1)  # <-- Add this sleep
        else:
            res_dict = json.loads(res.text)
            return res_dict["tunnels"][0]["public_url"]


def main():
    public_url = get_public_url()
    print(f"Public URL: {public_url}")


if __name__ == "__main__":
    main()
