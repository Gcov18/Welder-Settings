import pandas as pd
import requests
import os
import csv


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


def parse_excel(file_path):
    df = pd.read_excel(file_path)
    headers = list(df.columns) + ["Image Path"]
    data = []

    for _, row in df.iterrows():
        row_data = list(row)
        img_url = row.get("Image URL")
        img_path = download_image(img_url) if img_url else "No image"
        row_data.append(img_path)
        data.append(row_data)

    return headers, data


def save_to_csv(headers, data, filename):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for row in data:
            writer.writerow(row)


def main():
    excel_file_path = "welder_settings.xlsx"  # Path to your Excel file
    headers, data = parse_excel(excel_file_path)
    if headers and data:
        save_to_csv(headers, data, "welder_settings.csv")
    else:
        print("No data to save.")


if __name__ == "__main__":
    main()
