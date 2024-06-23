import requests
from bs4 import BeautifulSoup

def main():
    url = 'https://www.example.com'
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title').text
        print(f"Title: {title}")
    else:
        print(f"Failed to retrieve content. Status code: {response.status_code}")

if __name__ == "__main__":
    main()
