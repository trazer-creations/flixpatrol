import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from typing import List, Dict


class FlixPatrolScraper:
    def __init__(self):
        self.base_url = "https://flixpatrol.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        # List of platforms to scrape
        self.platforms = [
            "netflix",
            "hbo",
            "disney",
            "apple-tv",
            "hulu",
            "amazon-prime",
            "paramount-plus"
        ]

    def get_page_content(self, url: str) -> BeautifulSoup:
        """Fetch and parse page content"""
        try:
            # Add delay to be respectful to the server
            time.sleep(2)
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'lxml')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def scrape_platform_shows(self, platform: str) -> List[Dict]:
        """Scrape top shows for a specific platform"""
        shows = []
        soup = self.get_page_content(self.base_url)

        if not soup:
            return shows

        # Find the card with "Top shows" text and platform name
        platform_cards = soup.find_all('div', class_='card')

        for card in platform_cards:
            # Check if this card is for top shows
            top_shows_header = card.find(
                'div', text='Top shows', class_='text-gray-500')
            if not top_shows_header:
                continue

            # Check if this card is for the current platform
            platform_link = card.find(
                'a', href=lambda x: x and f'/top10/{platform}/' in x)
            if not platform_link:
                continue

            # Found the correct card, extract shows
            show_links = card.find_all(
                'a', href=lambda x: x and '/title/' in x)

            for idx, link in enumerate(show_links, 1):
                show_title = link.get('title', link.text.strip())
                show_url = f"{self.base_url}{link['href']}"

                shows.append({
                    'platform': platform,
                    'rank': idx,
                    'title': show_title,
                    'url': show_url
                })

            # Break after finding the correct card
            break

        return shows

    def scrape_all_platforms(self) -> pd.DataFrame:
        """Scrape top shows from all platforms"""
        all_shows = []

        for platform in self.platforms:
            print(f"Scraping {platform}...")
            platform_shows = self.scrape_platform_shows(platform)
            all_shows.extend(platform_shows)
            print(f"Found {len(platform_shows)} shows for {platform}")

        return pd.DataFrame(all_shows)


def main():
    scraper = FlixPatrolScraper()

    # Scrape all platforms
    df = scraper.scrape_all_platforms()

    # Save to CSV with timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f'top_shows_{timestamp}.csv'
    df.to_csv(filename, index=False)

    # Print summary
    print("\nScraping Summary:")
    print(df.groupby('platform').size())
    print(f"\nResults saved to {filename}")

    # Display first few rows
    print("\nSample of scraped data:")
    print(df.head())


if __name__ == "__main__":
    main()
