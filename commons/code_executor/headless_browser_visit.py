from loguru import logger
from pyppeteer import launch
from pyppeteer.browser import Browser
from pyppeteer.page import Page


async def visit_page():
    try:
        browser: Browser = await launch(headless=True)
        page: Page = await browser.newPage()
        await page.goto("http://localhost:3000", {"waitUntil": "networkidle0"})
    except Exception as e:
        logger.error(f"Error visiting the page: {e}")
    finally:
        await browser.close()
