"""Confluence connector implementation."""
import requests
from typing import List, Dict, Any
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from connectors.base_connector import BaseConnector, Document
from utils.logger import get_logger
from utils.retry import retry_with_backoff

logger = get_logger(__name__)


class ConfluenceConnector(BaseConnector):
    """Connector for Atlassian Confluence."""
    
    def __init__(
        self,
        base_url: str,
        username: str,
        api_token: str,
        space_keys: List[str]
    ):
        """
        Initialize Confluence connector.
        
        Args:
            base_url: Confluence base URL (e.g., https://yourcompany.atlassian.net/wiki)
            username: Confluence username/email
            api_token: Confluence API token
            space_keys: List of space keys to sync
        """
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.api_token = api_token
        self.space_keys = space_keys
        self.session = None
        
    def connect(self) -> None:
        """Establish connection to Confluence."""
        self.session = requests.Session()
        self.session.auth = (self.username, self.api_token)
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
        
        # Test connection
        try:
            response = self._make_request("/rest/api/space")
            logger.info(f"Successfully connected to Confluence at {self.base_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Confluence: {str(e)}")
            raise
    
    @retry_with_backoff(max_retries=3, exceptions=(requests.RequestException,))
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make a request to Confluence API.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response
        """
        # Remove leading slash from endpoint to work properly with urljoin
        endpoint = endpoint.lstrip("/")
        url = urljoin(self.base_url + "/", endpoint)
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def fetch_all_documents(self) -> List[Document]:
        """
        Fetch all documents from configured Confluence spaces.
        
        Returns:
            List of Document objects
        """
        documents = []
        
        for space_key in self.space_keys:
            logger.info(f"Fetching pages from Confluence space: {space_key}")
            try:
                space_docs = self._fetch_space_documents(space_key)
                documents.extend(space_docs)
                logger.info(f"Fetched {len(space_docs)} pages from space {space_key}")
            except Exception as e:
                logger.error(f"Error fetching from space {space_key}: {str(e)}")
                continue
        
        logger.info(f"Total documents fetched from Confluence: {len(documents)}")
        return documents
    
    def _fetch_space_documents(self, space_key: str) -> List[Document]:
        """Fetch all documents from a specific space."""
        documents = []
        start = 0
        limit = 50
        
        while True:
            params = {
                "spaceKey": space_key,
                "start": start,
                "limit": limit,
                "expand": "body.storage,version,history,metadata.labels"
            }
            
            try:
                response = self._make_request("/rest/api/content", params)
                results = response.get("results", [])
                
                if not results:
                    break
                
                for page in results:
                    try:
                        doc = self._parse_page(page, space_key)
                        if doc:
                            documents.append(doc)
                    except Exception as e:
                        logger.warning(f"Failed to parse page {page.get('id')}: {str(e)}")
                        continue
                
                # Check if there are more pages
                links = response.get("_links", {})
                if "next" not in links:
                    break
                
                start += limit
                
            except Exception as e:
                logger.error(f"Error fetching pages from space {space_key}: {str(e)}")
                break
        
        return documents
    
    def _parse_page(self, page: Dict[str, Any], space_key: str) -> Document:
        """Parse a Confluence page into a Document object."""
        page_id = page.get("id", "")
        title = page.get("title", "Untitled")
        
        # Extract HTML content
        body = page.get("body", {}).get("storage", {}).get("value", "")
        
        # Convert HTML to plain text
        content = self._html_to_text(body)
        
        # Build URL
        url = urljoin(
            self.base_url,
            f"/spaces/{space_key}/pages/{page_id}"
        )
        
        # Get metadata
        version = page.get("version", {})
        history = page.get("history", {})
        
        author = (
            history.get("createdBy", {}).get("displayName", "Unknown") or
            version.get("by", {}).get("displayName", "Unknown")
        )
        
        created_date = history.get("createdDate", "")
        modified_date = version.get("when", "")
        
        # Extract labels/tags
        labels = page.get("metadata", {}).get("labels", {}).get("results", [])
        tags = [label.get("name", "") for label in labels]
        
        return Document(
            id=f"confluence_{page_id}",
            title=title,
            content=content,
            url=url,
            author=author,
            source="confluence",
            created_date=created_date,
            modified_date=modified_date,
            tags=tags,
            metadata={
                "space_key": space_key,
                "page_id": page_id,
                "version": version.get("number", 1)
            }
        )
    
    @staticmethod
    def _html_to_text(html: str) -> str:
        """Convert HTML content to plain text."""
        if not html:
            return ""
        
        try:
            soup = BeautifulSoup(html, "html.parser")
            
            # Remove script and style elements
            for element in soup(["script", "style"]):
                element.decompose()
            
            # Get text
            text = soup.get_text(separator="\n", strip=True)
            
            # Clean up whitespace
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            return "\n".join(lines)
            
        except Exception as e:
            logger.warning(f"Error parsing HTML: {str(e)}")
            return html
    
    def get_source_name(self) -> str:
        """Get the source name."""
        return "confluence"

