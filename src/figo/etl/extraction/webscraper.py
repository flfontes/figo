import asyncio
from pprint import pprint as print

from curl_cffi.requests import AsyncSession, Session
from selectolax.parser import HTMLParser, Node

from figo.logger.config import logger as log


class Scraper:
    def __init__(self) -> None:
        self.blocking: Session = Session()
        self.session: AsyncSession = AsyncSession()

    async def request_async(self, url: str) -> str:
        response = await self.session.get(url, impersonate='firefox135')
        log.debug(f'Fetching {url} asynchronally.')

        if not response.ok:
            log.exception(
                f'Failed request. Response status code: {response.status_code}.'
            )

        log.info(f'Fetch of {url} succeeded.')
        return response.text

    def request_blocking(self, url: str) -> str:
        response = self.blocking.get(url, impersonate='firefox135')
        log.debug(f'Fetching {url} synchronally.')

        if not response.ok:
            log.exception(
                f'Failed request. Response status code: {response.status_code}.'
            )

        log.info(f'Fetch of {url} succeeded.')
        return response.text

    def parse(self, html: str, css_selector: str) -> list[Node]:
        parsed_html = HTMLParser(html)

        css_elements = parsed_html.css(css_selector)

        if not css_elements:
            log.exception('CSS element no found in the HTML page')

        return css_elements

    def extract_links(self, a_node: Node) -> str:
        link = a_node.attributes['href']

        if not link:
            raise Exception('Link not available.')

        return a_node.attributes['href']


if __name__ == '__main__':
    extractor = Scraper()

    response_async = asyncio.run(extractor.request_async('https://example.com'))
    print(response_async)

    response_blocking = extractor.request_blocking('https://example.com')
    print(response_blocking)
