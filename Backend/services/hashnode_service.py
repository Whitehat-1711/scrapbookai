"""
Hashnode Publishing Service
============================
Integrates with Hashnode GraphQL API to publish blogs directly.
"""

import logging
import httpx
from typing import Optional, Dict, Any

# Handle imports with fallback for different module contexts
try:
    from backend.core.config import HASHNODE_API_TOKEN, HASHNODE_PUBLICATION_ID
except ImportError:
    from ..core.config import HASHNODE_API_TOKEN, HASHNODE_PUBLICATION_ID

logger = logging.getLogger("blogy")

HASHNODE_API_URL = "https://gql.hashnode.com"


class HashnodePublishError(Exception):
    """Raised when Hashnode publishing fails"""
    pass


async def publish_to_hashnode(
    title: str,
    content: str,
    slug: str,
    meta_description: str,
    tags: Optional[list[str]] = None,
    featured_image_url: Optional[str] = None,
    is_draft: bool = False,
) -> Dict[str, Any]:
    """
    Publish a blog post to Hashnode.
    
    Args:
        title: Blog post title
        content: Blog post content (Markdown)
        slug: URL-friendly slug (lowercase, hyphens only)
        meta_description: Meta description for SEO
        tags: List of tags (max 5 recommended)
        featured_image_url: URL to featured image
        is_draft: If True, publishes as draft; if False, publishes immediately
    
    Returns:
        Dictionary with:
        - success (bool): Whether publishing succeeded
        - hashnode_id (str): Hashnode post ID if successful
        - hashnode_url (str): Full URL to the post if successful
        - message (str): Status message
        - error (str): Error message if failed
    
    Raises:
        HashnodePublishError: If API token or publication ID not configured
    """
    
    if not HASHNODE_API_TOKEN:
        raise HashnodePublishError(
            "HASHNODE_API_TOKEN not configured. "
            "Add it to your .env file."
        )
    
    if not HASHNODE_PUBLICATION_ID:
        raise HashnodePublishError(
            "HASHNODE_PUBLICATION_ID not configured. "
            "Add it to your .env file."
        )
    
    # Sanitize slug
    slug = slug.lower().replace(" ", "-").replace("_", "-")
    
    # Limit tags to 5
    if tags and len(tags) > 5:
        logger.warning(f"Tags limited to 5. Received {len(tags)}, using first 5.")
        tags = tags[:5]
    
    # Escape strings for GraphQL
    title_escaped = escape_graphql_string(title)
    subtitle_escaped = escape_graphql_string(meta_description)
    content_escaped = escape_graphql_string(content)
    
    # Build tags array input
    tags_input = ""
    if tags:
        # Tags in Hashnode must be objects with both slug and name fields to create new tags
        tags_list = ", ".join([f'{{slug: "{escape_graphql_string(tag)}", name: "{escape_graphql_string(tag)}"}}' for tag in tags])
        tags_input = f', tags: [{tags_list}]'
    
    # Build featured image input
    featured_image_input = ""
    if featured_image_url:
        featured_image_escaped = escape_graphql_string(featured_image_url)
        featured_image_input = f', coverImageOptions: {{coverImageUrl: "{featured_image_escaped}"}}'
    
    # Build the mutation with proper GraphQL syntax
    mutation = f"""
    mutation PublishPost {{
        publishPost(input: {{
            publicationId: "{HASHNODE_PUBLICATION_ID}"
            title: "{title_escaped}"
            subtitle: "{subtitle_escaped}"
            contentMarkdown: "{content_escaped}"
            slug: "{slug}"{tags_input}{featured_image_input}
        }}) {{
            post {{
                id
                slug
                url
                title
            }}
        }}
    }}
    """
    
    logger.debug(f"GraphQL Mutation:\n{mutation}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                HASHNODE_API_URL,
                json={"query": mutation},
                headers={"Authorization": f"Bearer {HASHNODE_API_TOKEN}"},
            )
            
            # Log the response for debugging
            logger.debug(f"Hashnode Response Status: {response.status_code}")
            logger.debug(f"Hashnode Response: {response.text}")
            
            response.raise_for_status()
            data = response.json()
            
            # Check for GraphQL errors
            if "errors" in data and data["errors"]:
                error_message = data["errors"][0].get("message", "Unknown error")
                logger.error(f"Hashnode GraphQL Error: {error_message}")
                return {
                    "success": False,
                    "message": "Failed to publish to Hashnode",
                    "error": error_message,
                }
            
            # Extract post data
            post_data = data.get("data", {}).get("publishPost", {}).get("post", {})
            
            if not post_data:
                logger.error("No post data in Hashnode response")
                return {
                    "success": False,
                    "message": "No post data returned from Hashnode",
                    "error": "Unknown Hashnode response format",
                }
            
            hashnode_id = post_data.get("id")
            hashnode_url = post_data.get("url")
            
            logger.info(f"✅ Blog published to Hashnode: {hashnode_url}")
            
            return {
                "success": True,
                "hashnode_id": hashnode_id,
                "hashnode_url": hashnode_url,
                "message": "Successfully published to Hashnode",
                "error": None,
            }
    
    except httpx.HTTPError as e:
        logger.error(f"HTTP error publishing to Hashnode: {e}")
        error_detail = str(e)
        try:
            if hasattr(e, 'response') and e.response:
                error_detail = f"{e}\nResponse: {e.response.text}"
        except:
            pass
        return {
            "success": False,
            "message": "HTTP error publishing to Hashnode",
            "error": error_detail,
        }
    
    except Exception as e:
        logger.error(f"Unexpected error publishing to Hashnode: {e}")
        return {
            "success": False,
            "message": "Unexpected error publishing to Hashnode",
            "error": str(e),
        }


def escape_graphql_string(s: str) -> str:
    """Escape special characters for GraphQL string input"""
    return (
        s.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )


def format_graphql_multiline(text: str) -> str:
    """Format multiline text for GraphQL mutation"""
    # Escape and quote for GraphQL
    escaped = escape_graphql_string(text)
    return f'"{escaped}"'


async def get_hashnode_user_info() -> Optional[Dict[str, Any]]:
    """
    Get authenticated user info from Hashnode (for testing/validation).
    
    Returns:
        User info dict or None if unable to retrieve
    """
    if not HASHNODE_API_TOKEN:
        logger.warning("HASHNODE_API_TOKEN not configured")
        return None
    
    query = """
    query {
        me {
            id
            name
            username
            publications(first: 10) {
                edges {
                    node {
                        id
                        displayTitle
                        slug
                    }
                }
            }
        }
    }
    """
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                HASHNODE_API_URL,
                json={"query": query},
                headers={"Authorization": f"Bearer {HASHNODE_API_TOKEN}"},
            )
            
            response.raise_for_status()
            data = response.json()
            
            if "errors" in data and data["errors"]:
                logger.warning(f"Hashnode error: {data['errors'][0]['message']}")
                return None
            
            return data.get("data", {}).get("me")
    
    except Exception as e:
        logger.warning(f"Failed to get Hashnode user info: {e}")
        return None
