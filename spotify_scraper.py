import asyncio
from playwright.async_api import async_playwright

async def run(playlist_url: str) -> dict: 
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        page.set_default_timeout(50000)  # 50 seconds
        await page.goto(
                playlist_url                
        )
        await page.locator('a[data-testid="internal-track-link"]').first.wait_for()

        # Scroll down to load all tracks
        last_count = 0
        links = dict()
        while True:
            # Get current track count
            track_links_locator = page.locator('div[data-testid="playlist-tracklist"] a[data-testid="internal-track-link"]')
            current_count = await track_links_locator.count()
            # Get track ids on each scroll
            for i in range(current_count):
                href = await track_links_locator.nth(i).get_attribute('href')
                track_id = href.split('/')[-1]
                links[track_id] = None

            # If no new tracks were loaded, break the loop
            if current_count == last_count:
                break
                
            # Update last count
            last_count = current_count
            
            # Scroll to the last visible track to trigger loading more
            await track_links_locator.nth(current_count - 1).scroll_into_view_if_needed()
            
            # Wait a bit for potential new tracks to load
            await page.wait_for_timeout(1000)
        
        # Get the last track links
        track_links_locator = page.locator('div[data-testid="playlist-tracklist"] a[data-testid="internal-track-link"]')
        count = await track_links_locator.count()
        
        for i in range(count):
            href = await track_links_locator.nth(i).get_attribute('href')
            # Extract track ID from the URL
            track_id = href.split('/')[-1]
            links[track_id] = None
            
        for link in links.keys():
            print(link)

        print(len(links), ' tracks collected!')

        await browser.close()
        return {"status": "success", "track_ids": links}
