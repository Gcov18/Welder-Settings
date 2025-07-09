import requests
from bs4 import BeautifulSoup
import csv
import os


def gather_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return [], []

    soup = BeautifulSoup(response.text, "html.parser")

    data = []
    # Example: Extracting data from a table
    table = soup.find("table", {"id": "welder-settings"})
    if table is None:
        print(f"No table found at {url}")
        return [], []

    headers = [header.text.strip() for header in table.find_all("th")]
    headers.append("Image Path")  # Add a new header for image paths

    for row in table.find_all("tr")[1:]:  # Skip the header row
        cols = row.find_all("td")
        row_data = [col.text.strip() for col in cols]

        # Example: Extracting image URL from the row
        img_tag = row.find("img")
        img_url = img_tag["src"] if img_tag else None
        img_path = download_image(img_url) if img_url else "No image"
        row_data.append(img_path)

        data.append(row_data)

    return headers, data


def download_image(url):
    if not url:
        return "No image"

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error downloading image {url}: {e}")
        return "No image"

    # Create images directory if it doesn't exist
    os.makedirs("images", exist_ok=True)
    img_name = os.path.basename(url)
    img_path = os.path.join("images", img_name)

    with open(img_path, "wb") as img_file:
        img_file.write(response.content)

    return img_path


def save_to_csv(headers, data, filename):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for row in data:
            writer.writerow(row)


def main():
    urls = [
        "https://weldguru.com/mig-welder-settings/",
        "https://weldguru.com/wp-content/uploads/wire-selection-settings-chart-large.jpg/",
        # Add more URLs as needed
    ]
    all_data = []
    headers = []
    for url in urls:
        url_headers, data = gather_data(url)
        if not headers and url_headers:
            headers = url_headers
        all_data.extend(data)

    if headers and all_data:
        save_to_csv(headers, all_data, "welder_settings.csv")
    else:
        print("No data to save.")


if __name__ == "__main__":
    main()
