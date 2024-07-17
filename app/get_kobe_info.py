import os
import re
import csv
import logging
import requests
import boto3
from botocore.exceptions import NoCredentialsError
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from functools import wraps
from io import StringIO

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

url_list = ['https://www.feel-kobe.jp/event/']
access_token = os.getenv('LINE_NOTIFY_TOKEN')
s3_bucket = os.getenv('S3_BUCKET')
s3_key = os.getenv('S3_KEY')
local_csv_file = s3_key

# AWS credentials
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_REGION')

# Initialize S3 Client
s3 = boto3.client('s3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
    )

# Decorator for logging function entry and exit
def log_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f'Start {func.__name__}')
        result = func(*args, **kwargs)
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
    def __init__(self, bucket, key, filepath):
        self.bucket = bucket
        self.key = key
        self.filepath = filepath

    @log_decorator
    def download_csv(self):
        try:
            response = s3.get_object(Bucket=self.bucket, Key=self.key)
            body = response['Body'].read().decode('utf-8')
            with open(self.filepath, mode='w', encoding='utf-8') as file:
                file.write(body)
            logger.info(f'CSV downloaded from S3 to {self.filepath}')
        except s3.exceptions.NoSuchKey:
            logger.warning(f'No such key: {self.key}')
        except NoCredentialsError:
            logger.error('Credentials not available')
        except Exception as e:
            logger.error(f'Error downloading file: {e}')

    @log_decorator
    def check_url_in_csv(self, url):
        try:
            with open(self.filepath, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    logger.info(f'row: {row}, url: {url}')
                    if url in row:
                        return False
            return True
        except FileNotFoundError:
            logger.error('File not found')
            return False
        except Exception as e:
            logger.error(f'Error reading file: {e}')
            return False

    @log_decorator
    def write_csv(self, href):
        try:
            with open(self.filepath, mode='a', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([href])
            logger.info(f'CSV updated with href: {href}')
        except Exception as e:
            logger.error(f'Error writing to file: {e}')

    @log_decorator
    def upload_csv(self):
        try:
            with open(self.filepath, mode='r', encoding='utf-8') as file:
                s3.put_object(Bucket=self.bucket, Key=self.key, Body=file.read())
            logger.info(f'CSV uploaded to {self.bucket}/{self.key}')
        except NoCredentialsError:
            logger.error('Credentials not available')
        except Exception as e:
            logger.error(f'Error uploading file: {e}')

@log_decorator
def main():
    message = ''
    lineNotify = LineNotify(access_token)
    csv_operation = CSVOperation(s3_bucket, s3_key, local_csv_file)

    # First, get csvfile from s3 bucket. Then it starts proccess.
    csv_operation.download_csv()

    for url in url_list:
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            a_tags = soup.find_all('a')
            
            url_pattern = re.compile(r'/event/\d{1,10}')
            
            for a_tag in a_tags:
                href = a_tag.get('href')

                if href and url_pattern.search(href):
                    full_url = requests.compat.urljoin(url, href)
                    response = requests.get(full_url)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        title = soup.find('title').text
                        message = f'Title: {title}\n URL: {full_url}\n'

                        if csv_operation.check_url_in_csv(full_url):
                            csv_operation.write_csv(full_url)
                            lineNotify.send_line(message)
                    else:
                        logger.warning(f'Failed to retrieve content from: {full_url}. Status code: {response.status_code}')

        else:
            logger.error(f'Failed to retrieve content from: {url}. Status code: {response.status_code}')

    # Finaly, upload csv file.
    csv_operation.upload_csv()

if __name__ == "__main__":
    main()
