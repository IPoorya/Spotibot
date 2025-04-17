import asyncio, logging, os
from playwright.async_api import async_playwright, Error as PlaywrightError


# Configure logging
os.makedirs("log", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('log/spotify_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SpotifyScraper:
    def __init__(self):
        self.browser = None
        self.page = None
        self.playwright = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch()
        self.page = await self.browser.new_page()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.browser.close()
        await self.playwright.stop()

    async def scrape_playlist(self, url): 
        logging.info(f"Openning URL: {url}")
        try:
            self.page.set_default_timeout(50000)
            await self.page.goto(url)
            await self.page.locator('a[data-testid="internal-track-link"]').first.wait_for()
            logging.info("Playlist page loaded.")

            # Scroll down to load all tracks
            last_count = 0
            track_ids = dict()
        
            while True:
                track_links_locator = self.page.locator('div[data-testid="playlist-tracklist"] a[data-testid="internal-track-link"]')
                current_count = await track_links_locator.count()
            
                for i in range(current_count):
                    href = await track_links_locator.nth(i).get_attribute('href')
                    track_id = href.split('/')[-1]
                    track_ids[track_id] = None
    
                logging.info(f"Loaded {current_count} tracks so far.") 
            
                if current_count == last_count:
                    break

                last_count = current_count
                await track_links_locator.nth(current_count - 1).scroll_into_view_if_needed()
                await self.page.wait_for_timeout(1000)

            logging.info(f"Scraping finished. Total tracks: {len(track_ids)}")
            return {"status": "success", "track_ids": track_ids, "count": len(track_ids)}
        
        except PlaywrightError as e:
            logging.error(f"Unexpected error occured: {e}")
            return {"status": "error", "message": str(e)}


