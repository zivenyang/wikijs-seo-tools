import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import httpx
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from urllib.parse import urlparse

app = FastAPI()

# Load configuration from environment variables
WIKIJS_BASE_URL = os.getenv("WIKIJS_BASE_URL")
WIKIJS_API_URL = os.getenv("WIKIJS_API_URL")
WIKIJS_API_TOKEN = os.getenv("WIKIJS_API_TOKEN")

# Check if environment variables are set
if not WIKIJS_BASE_URL:
    raise ValueError("Environment variable WIKIJS_BASE_URL is not set")
if not WIKIJS_API_URL:
    raise ValueError("Environment variable WIKIJS_API_URL is not set")
if not WIKIJS_API_TOKEN:
    raise ValueError("Environment variable WIKIJS_API_TOKEN is not set")

# Validate URLs for protocol
for url_var, url_value in [("WIKIJS_BASE_URL", WIKIJS_BASE_URL), ("WIKIJS_API_URL", WIKIJS_API_URL)]:
    parsed_url = urlparse(url_value)
    if not parsed_url.scheme:
        raise ValueError(f"{url_var} is missing a protocol, must start with http:// or https://: {url_value}")
    if parsed_url.scheme not in ["http", "https"]:
        raise ValueError(f"{url_var} has an invalid protocol, only http or https supported: {url_value}")

# Asynchronous function to fetch page data
async def get_pages():
    query = """
    {
      pages {
        list (orderBy: CREATED) {
          id
          path
          locale
          title
          description
          isPublished
          isPrivate
          createdAt
          updatedAt
          tags
        }
      }
    }
    """
    headers = {"Authorization": f"Bearer {WIKIJS_API_TOKEN}"}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(WIKIJS_API_URL, json={"query": query}, headers=headers)
            response.raise_for_status()
            return response.json()["data"]["pages"]["list"]
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise HTTPException(status_code=401, detail="Authentication failed: WIKIJS_API_TOKEN is invalid")
        raise HTTPException(status_code=502, detail=f"GraphQL request failed: {e}")
    except httpx.UnsupportedProtocol:
        raise HTTPException(status_code=500, detail=f"WIKIJS_API_URL format error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# Function to build Sitemap XML
def build_sitemap_xml(base_url: str, pages: list):
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for page in pages:
        if not page["isPublished"] or page["isPrivate"]:
            continue
        url_path = page["path"].strip("/")
        locale = page["locale"]
        # Build full URL using WIKIJS_BASE_URL
        full_url = f"{base_url.rstrip('/')}/{locale}/{url_path}" if url_path else f"{base_url.rstrip('/')}/{locale}"
        url = ET.SubElement(urlset, "url")
        ET.SubElement(url, "loc").text = full_url
        if page["updatedAt"]:
            lastmod = datetime.fromisoformat(page["updatedAt"].replace("Z", "+00:00")).strftime("%Y-%m-%dT%H:%M:%SZ")
            ET.SubElement(url, "lastmod").text = lastmod
        changefreq = ET.SubElement(url, "changefreq")
        priority = ET.SubElement(url, "priority")
        if page["path"] == "home":
            changefreq.text = "daily"
            priority.text = "1.0"
        elif page["path"].startswith("blog/"):
            changefreq.text = "monthly"
            priority.text = "0.8"
        else:
            changefreq.text = "weekly"
            priority.text = "0.5"
    xml_str = ET.tostring(urlset, encoding="utf-8", method="xml")
    return minidom.parseString(xml_str).toprettyxml(indent="  ")

# Sitemap API endpoint
@app.get("/sitemap")
async def generate_sitemap():
    pages = await get_pages()
    xml_content = build_sitemap_xml(WIKIJS_BASE_URL, pages)
    return Response(content=xml_content, media_type="application/xml")

# Timeline endpoint returning raw published pages from GraphQL
@app.get("/timeline")
async def get_timeline():
    pages = await get_pages()
    published_pages = [page for page in pages if page["isPublished"] and not page["isPrivate"]]
    return published_pages

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)