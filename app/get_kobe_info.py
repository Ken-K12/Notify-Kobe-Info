import os
import re
import csv

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

url_list = ['https://www.feel-kobe.jp/event/']

def send_line(message, token):
    url = 'https://notify-api.line.me/api/notify'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    data = {
        'message': message
    }
    response = requests.post(url, headers=headers, data=data)
    return response.status_code

def write_csv(href):
    with open('event_url.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([])

def main():
    for i in range(len(url_list)):

        response = requests.get(url_list[i])
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('title').text
            a_tags = soup.find_all('a')
            
            url_pattern = re.compile(r'/event/\d{1,10}')
            
            for a_tag in a_tags:
                href = a_tag.get('href')
                if href and url_pattern.search(href):
                    print(href)

        else:
            print(f"Failed to retrieve content. Status code: {response.status_code}")

if __name__ == "__main__":

    main()
    # load_dotenv()
    # access_token = os.getenv('LINE_NOTIFY_TOKEN')
    # message = "Hello from Python! This is a test message."

    # status_code = send_line(message, access_token)

    # if status_code == 200:
    #     print('message sent successfuly.')
    # else:
    #     print('failed to send message. Status code: {status_code}')
