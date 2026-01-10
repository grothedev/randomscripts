import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os

def extract_article(url, output_filename="extracted_article.html"):
    """
    Extracts the main article content and images from a webpage and saves it to a simplified HTML file.

    Args:
        url: The URL of the article or blog post.
        output_filename: The name of the HTML file to save the extracted content to.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.content, 'html.parser')

        # --- Identify Main Content Area ---
        # This is the trickiest part. You'll likely need to adjust this based on the specific website structure.
        # Common strategies:
        # 1. Look for specific IDs or classes on container elements.
        # 2. Look for the element containing the most text.
        # 3. Manually inspect the HTML source to find the right element.

        # Example: Let's assume the article content is within a <div class="article-content">
        main_content = soup.find('div', class_='article-content')
        if not main_content:
            # Alternative strategy: find the tag containing the most text (crude but sometimes works)
            main_content = max(soup.find_all('div'), key=lambda tag: len(tag.text)) #This will likely require manual adjustment for each site!
            if not main_content:
                print(f"Warning: Could not automatically identify the main content area.  You may need to adjust the selection logic in the script.")
                main_content = soup.body #Use the whole body as last resort

        # --- Extract Images and Update Source URLs ---
        images = main_content.find_all('img')
        for img in images:
            src = img.get('src')
            if src:
                # Make URLs absolute if they are relative
                absolute_url = urljoin(url, src)
                img['src'] = absolute_url  # Update the image source

        # --- Create Stripped-Down HTML ---
        html_content = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Extracted Article</title>
            <style>
                body {{
                    font-family: sans-serif;
                    margin: 20px;
                    line-height: 1.6;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                }}
            </style>
        </head>
        <body>
            {main_content.prettify()}
        </body>
        </html>"""


        # --- Save to File ---
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"Article extracted and saved to {output_filename}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
