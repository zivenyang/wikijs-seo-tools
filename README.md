# wikijs-seo-tools

## Clone the respository
```bash
git clone https://github.com/zivenyang/wikijs-seo-tools.git
cd wikijs-seo-tools
```

## Updated `docker-compose.yaml`

```yaml
version: '3.8'

services:
  sitemap-service:
    build: .
    ports:
      - "8000:8000"
    environment:
      - WIKIJS_BASE_URL=https://example.com
      - WIKIJS_API_URL=https://example.com/graphql
      - WIKIJS_API_TOKEN=your-api-token
```

## Build and Run

```bash
docker-compose up --build -d
```

## Access Sitemap:

[http://localhost:8000/sitemap](http://localhost:8000/sitemap)


## Example Sitemap Output

Assuming `WIKIJS_BASE_URL=https://example.com`, the generated Sitemap might look like this:
```xml
<?xml version="1.0" encoding="utf-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/zh/home</loc>
    <lastmod>2025-02-25T13:33:43Z</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://example.com/en/home</loc>
    <lastmod>2025-02-25T12:46:06Z</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://example.com/zh/blog/2022/03/02/docker-compose-wordpress</loc>
    <lastmod>2025-02-25T12:56:54Z</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>
```
