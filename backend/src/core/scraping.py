import urllib.robotparser
from urllib.parse import urlparse
import requests
from backend.src.core.logging import get_logger

logger = get_logger(__name__)

class RobotsChecker:
    def __init__(self, user_agent="JobCrawlAgent/1.0"):
        self.user_agent = user_agent
        self.parsers = {}

    def can_fetch(self, url: str) -> bool:
        """
        Checks if the given URL can be fetched according to the site's robots.txt.
        """
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"

        if robots_url not in self.parsers:
            parser = urllib.robotparser.RobotFileParser()
            parser.set_url(robots_url)
            try:
                parser.read()
                self.parsers[robots_url] = parser
            except Exception as e:
                logger.warning(f"Could not read robots.txt from {robots_url}: {e}")
                return False
        
        parser = self.parsers.get(robots_url)
        if parser:
            return parser.can_fetch(self.user_agent, url)
        
        return False

class Scraper:
    def __init__(self):
        self.robots_checker = RobotsChecker()

    def retrieve_content(self, query: str) -> list[str]:
        """
        Given a search query, retrieves a list of URLs.
        This is a placeholder and does not perform a real search yet.
        """
        logger.info(f"Simulating search for: {query}")
        # Placeholder URLs
        return [
            "http://example.com/page1",
            "http://example.com/page2",
            "http://example.com/disallowed",
        ]

    def get_page_content(self, url: str) -> str:
        """
        Fetches the text content of a single page, respecting robots.txt.
        """
        if not self.robots_checker.can_fetch(url):
            logger.info(f"Skipping {url} due to robots.txt")
            return ""
        
        try:
            response = requests.get(url, headers={'User-Agent': self.robots_checker.user_agent})
            response.raise_for_status()
            # In a real implementation, we would parse the HTML here.
            return response.text[:500] # Return a snippet for now
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return ""

# Singleton instances
robots_checker = RobotsChecker()
scraper = Scraper()
