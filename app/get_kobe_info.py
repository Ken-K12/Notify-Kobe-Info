import os
import re
import csv
import logging
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from functools import wraps

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

url_list = ['https://www.feel-kobe.jp/event/']
access_token = os.getenv('LINE_NOTIFY_TOKEN')

# Decorator for logging function entry and exit
def log_decorator(func):
    @wraps(func)
    def wrapper(*args, **kargs):
        logger.info(f'Start {func.__name__}')
        result = func(*args, **kargs)
        logger.info(f'End {func.__name__}')
        return result
    return wrapper


class LineNotify:
    def __init__(self, token):
        self.token = token

    @log_decorator
    def send_line(self, message):
        url = 'https://notify-api.line.me/api/notify'
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        data = {
            'message': message
        }
        response = requests.post(url, headers=headers, data=data)
        return response.status_code


class CSVOperation:
    def __init__(self, filename):
        self.filename = filename

    @log_decorator
    def write_csv(self, href):
        with open(self.filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([href])
    
    @log_decorator
    def check_url_in_csv(self, url):
        
        with open(self.filename, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                logger.info(f'row: {row}, url: {url}')
                if url in row:
                    return False
        return True

@log_decorator
def main():
    message = ''
    lineNotify = LineNotify(access_token)
    csv_operation = CSVOperation('event.csv')

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
                    response = requests.get(href)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title = soup.find('title').text
                    message = f'Title: {title}\n'
                    message += f'URL : {href}\n'
                    
                    if csv_operation.check_url_in_csv(href):
                        csv_operation.write_csv(href)
                        lineNotify.send_line(message)

        else:
            print(f"Failed to retrieve content. Status code: {response.status_code}")

if __name__ == "__main__":
    main()
