import urllib.robotparser
from urllib.parse import urlparse

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
                print(f"Could not read robots.txt from {robots_url}: {e}")
                # If we can't read robots.txt, assume we can't fetch.
                return False
        
        parser = self.parsers.get(robots_url)
        if parser:
            return parser.can_fetch(self.user_agent, url)
        
        return False

# Singleton instance
robots_checker = RobotsChecker()
