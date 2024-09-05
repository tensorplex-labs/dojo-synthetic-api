import asyncio

from pyppeteer import launch
from pyppeteer.browser import Browser
from pyppeteer.page import Page


async def visit_page():
    browser: Browser = await launch()
    page: Page = await browser.newPage()
    await page.goto("http://localhost:3000", {"waitUntil": "networkidle0"})
    await browser.close()


asyncio.get_event_loop().run_until_complete(visit_page())
