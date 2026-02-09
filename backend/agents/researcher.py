import os
import re
import time
import hashlib
import requests
from bs4 import BeautifulSoup
from typing import Optional, List, Dict

CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'cache', 'docs')
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

class ResearchAgent:
    """
    ResearchAgent fetches and searches official documentation for supported libraries.
    It uses simple web scraping with caching to avoid repeated downloads.

    Supported docs:
    - LangChain (https://python.langchain.com/en/latest/)
    - Next.js (https://nextjs.org/docs)
    - React (https://react.dev)
    - Tailwind CSS (https://tailwindcss.com/docs)
    - FastAPI (https://fastapi.tiangolo.com)
    - Python 3 (https://docs.python.org/3/)
    - Node.js (https://nodejs.org/en/docs/)
    - React-Native (https://reactnative.dev/docs/getting-started)
    - Fly.io (https://fly.io/docs/)
    - Github (https://docs.github.com/en)
    """

    DOC_SITES = {
        'langchain': 'https://python.langchain.com/en/latest/',
        'nextjs': 'https://nextjs.org/docs',
        'react': 'https://react.dev',
        'tailwindcss': 'https://tailwindcss.com/docs',
        'fastapi': 'https://fastapi.tiangolo.com/en/latest/',
        'python': 'https://docs.python.org/3/',
        'nodejs': 'https://nodejs.org/en/docs/',
        'react-native': 'https://reactnative.dev/docs/getting-started',
        'flyio': 'https://fly.io/docs/',
        'github': 'https://docs.github.com/en',
    }

    def __init__(self):
        self.session = requests.Session()

    def _cache_path(self, url: str) -> str:
        # Use a hash of the url for cache filename
        h = hashlib.sha256(url.encode('utf-8')).hexdigest()
        return os.path.join(CACHE_DIR, f'{h}.html')

    def _fetch_url(self, url: str) -> Optional[str]:
        cache_file = self._cache_path(url)
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                return f.read()
        try:
            resp = self.session.get(url, timeout=10)
            if resp.status_code == 200:
                content = resp.text
                with open(cache_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                time.sleep(1)  # polite delay
                return content
        except Exception as e:
            print(f"ResearchAgent: Failed to fetch {url}: {e}")
        return None

    def _extract_text(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        # Remove script and style
        for script in soup(['script', 'style', 'noscript']):
            script.decompose()
        text = soup.get_text(separator=' ')
        # Collapse whitespace
        text = re.sub(r'\s+', ' ', text)
        return text

    def search(self, library: str, query: str, max_results: int = 3) -> List[str]:
        """
        Search the documentation of the given library for the query.
        Returns a list of text snippets containing the query.
        """
        library = library.lower()
        if library not in self.DOC_SITES:
            raise ValueError(f"Unsupported library for research: {library}")

        base_url = self.DOC_SITES[library]

        # For simplicity, fetch the base doc page and search text
        html = self._fetch_url(base_url)
        if not html:
            return []

        text = self._extract_text(html).lower()
        query_lower = query.lower()

        # Find all occurrences of query in text and extract snippets
        snippets = []
        for match in re.finditer(re.escape(query_lower), text):
            start = max(match.start() - 50, 0)
            end = min(match.end() + 50, len(text))
            snippet = text[start:end].strip()
            snippets.append(snippet)
            if len(snippets) >= max_results:
                break

        return snippets

    def fetch_page(self, library: str, page_path: str) -> Optional[str]:
        """
        Fetch a specific documentation page by relative path.
        Example: page_path='getting-started' for Next.js docs.
        """
        library = library.lower()
        if library not in self.DOC_SITES:
            raise ValueError(f"Unsupported library for research: {library}")

        base_url = self.DOC_SITES[library].rstrip('/')
        if not page_path.startswith('/'):
            page_path = '/' + page_path
        url = base_url + page_path
        return self._fetch_url(url)

    def clear_cache(self):
        """Clear all cached documentation pages."""
        for filename in os.listdir(CACHE_DIR):
            if filename.endswith('.html'):
                os.remove(os.path.join(CACHE_DIR, filename))

    def research_before_build(self, task_description: str) -> Dict[str, List[str]]:
        """
        Parse the task description to extract relevant core stack technologies and
        search their documentation for relevant snippets.

        Args:
            task_description: The textual description of the task.

        Returns:
            Dictionary mapping each detected library to a list of relevant snippets.
        """
        # Define keywords for core stack technologies
        core_tech_keywords = {
            'python': r'\bpython\b',
            'fastapi': r'\bfastapi\b',
            'langchain': r'\blangchain\b',
            'nextjs': r'\bnext\.js\b|\bnextjs\b',
            'react': r'\breact\b',
            'tailwindcss': r'\btailwind\b|\btailwindcss\b',
            'nodejs': r'\bnode\.js\b|\bnodejs\b',
            'react-native': r'\breact[- ]native\b',
            'flyio': r'\bfly\.io\b|\bflyio\b',
            'github': r'\bgithub\b',
        }

        detected_tech = []
        lower_desc = task_description.lower()

        for tech, pattern in core_tech_keywords.items():
            if re.search(pattern, lower_desc):
                detected_tech.append(tech)

        results = {}
        for tech in detected_tech:
            snippets = self.search(tech, task_description, max_results=3)
            results[tech] = snippets

        return results
