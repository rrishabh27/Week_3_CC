import requests
from bs4 import BeautifulSoup

# Replace this URL with the target book website
url = 'https://books.toscrape.com/'

# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content of the page using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all the book elements, modify this according to the website structure
    books = soup.find_all('div', class_='book')

    for book in books:
        # Extract title
        title = book.find('h2', class_='title').text.strip()

        # Extract rating
        rating = book.find('span', class_='rating').text.strip()

        # Extract price
        price = book.find('span', class_='price').text.strip()

        # Extract availability
        availability = book.find('span', class_='availability').text.strip()

        # Print or store the extracted information
        print(f"Title: {title}")
        print(f"Rating: {rating}")
        print(f"Price: {price}")
        print(f"Availability: {availability}")
        print("====================")

else:
    print("Failed to retrieve the webpage.")
