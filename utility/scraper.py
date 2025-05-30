import requests
from bs4 import BeautifulSoup
import logging
import json
from django.utils import timezone
from uuid import uuid4
import re

logger = logging.getLogger(__name__)


def scrape_digiato_news(page_number=1, topic="tech"):
    """
    Scrape news from Digiato.com website using both JSON-LD data and HTML parsing

    Args:
        page_number: Page number to scrape (default: 1)
        topic: Topic to scrape (default: "tech")

    Returns:
        List of news items with full text content
    """
    url = f"https://digiato.com/topic/{topic}/page/{page_number}"
    logger.info(f"Starting to scrape: {url}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml',
        'Accept-Language': 'fa,en-US;q=0.9,en;q=0.8',
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        article_urls = extract_urls_from_jsonld(response.text)

        if article_urls:
            logger.info(f"Found {len(article_urls)} articles from JSON-LD")
            return fetch_articles_details(article_urls)
        else:

            logger.info("JSON-LD extraction failed, falling back to HTML parsing")
            return extract_from_html(response.text)

    except requests.RequestException as e:
        logger.error(f"Error scraping Digiato: {e}")
        return []

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return []


def extract_urls_from_jsonld(html_content):
    """
    Extract article URLs from JSON-LD data in the HTML

    Args:
        html_content: HTML content of the page

    Returns:
        List of article URLs
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        json_ld_scripts = soup.find_all('script', type='application/ld+json')

        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)

                if data.get('@type') == 'ItemList' and 'itemListElement' in data:
                    urls = []
                    for item in data['itemListElement']:
                        if item.get('@type') == 'ListItem' and 'url' in item:
                            urls.append(item['url'])

                    if urls:
                        return urls
            except (json.JSONDecodeError, AttributeError):
                continue

        return []

    except Exception as e:
        logger.error(f"Error extracting URLs from JSON-LD: {e}")
        return []


def fetch_articles_details(urls):
    """
    Fetch details for each article URL

    Args:
        urls: List of article URLs

    Returns:
        List of news items with details
    """
    news_items = []

    for url in urls:
        try:
            article_data = extract_article_data(url)
            if article_data:
                news_items.append(article_data)
        except Exception as e:
            logger.error(f"Error fetching article {url}: {e}")

    return news_items


def extract_article_data(url):
    """
    Extract article data from a single URL

    Args:
        url: URL of the article

    Returns:
        Article data as a dictionary
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        title_elem = soup.find('h1', class_='b-post__title')
        if not title_elem:
            title_elem = soup.find('h1')
        title = title_elem.get_text().strip() if title_elem else ''

        full_text = extract_full_article_content(soup)

        date_elem = soup.select_one('.b-post__time')
        published_date_str = date_elem.get_text().strip() if date_elem else None

        published_at = timezone.now()

        # Create news item
        if title:
            return {
                'id': str(uuid4()),
                'title': title,
                'text': full_text,
                'source': url,
                'published_at': published_at,
            }

        return None

    except Exception as e:
        logger.error(f"Error extracting article data from {url}: {e}")
        return None


def extract_full_article_content(soup):
    """
    Extract full article content from BeautifulSoup object

    Args:
        soup: BeautifulSoup object of the article page

    Returns:
        Full content of the article as text
    """
    try:
        article_content = soup.select_one('.b-content')

        if not article_content:
            article_content = soup.select_one('.entry-content')

        if not article_content:
            article_content = soup.select_one('article .post-content')

        if not article_content:
            article_tags = soup.find_all(['div', 'section'],
                                         class_=lambda c: c and ('content' in c.lower() or 'article' in c.lower()))
            for tag in article_tags:
                if len(tag.find_all('p')) > 3:
                    article_content = tag
                    break

        if not article_content:
            article_content = soup.select_one('main') or soup.select_one('article')

        if not article_content:
            all_paragraphs = soup.find_all('p')
            if all_paragraphs:
                text_parts = [p.get_text().strip() for p in all_paragraphs if
                              p.get_text().strip() and len(p.get_text().strip()) > 30]
                if text_parts:
                    return "\n\n".join(text_parts)
            return "محتوای مقاله یافت نشد."

        # حذف المان‌های زائد
        for elem in article_content.select(
                '.ads-container, .b-advert, script, .b-shortcode, .b-post__share, .b-post__tags, .navigation, .related-posts, .comments, aside, nav, footer, header, .sidebar'):
            elem.decompose()

        paragraphs = []
        for p in article_content.find_all(['p', 'h2', 'h3', 'h4', 'ul', 'ol', 'blockquote']):
            text = p.get_text().strip()
            if text and len(text) > 10:
                paragraphs.append(text)

        if paragraphs:
            return "\n\n".join(paragraphs)
        else:
            cleaned_text = article_content.get_text()
            # حذف فاصله‌های اضافه و خطوط خالی
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
            cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)
            return cleaned_text.strip()

    except Exception as e:
        logger.error(f"Error extracting full article content: {e}")
        return "خطا در استخراج محتوای مقاله."


def extract_from_html(html_content):
    """
    Extract articles from HTML content as a fallback method

    Args:
        html_content: HTML content of the page

    Returns:
        List of news items
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        news_items = []

        articles = soup.select('.b-archive-posts article')

        if not articles:
            articles = soup.select('.b-post-box')

        if not articles:
            articles = soup.select('article')

        logger.info(f"Found {len(articles)} articles from HTML")

        for article in articles:
            try:
                link_elem = article.find('a', class_='b-post-box__link') or article.find('a')
                if not link_elem:
                    continue

                href = link_elem.get('href', '')
                if not href:
                    continue

                title_elem = article.find(class_='b-post-box__title') or article.find(['h1', 'h2', 'h3'])
                title = title_elem.get_text().strip() if title_elem else ''

                excerpt_elem = article.find(class_='b-post-box__excerpt') or article.find('p')

                if title and len(title) > 3 and href:
                    if not href.startswith('http'):
                        href = f"https://digiato.com{href}"

                    try:
                        article_response = requests.get(href, headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        }, timeout=10)
                        article_soup = BeautifulSoup(article_response.text, 'html.parser')
                        full_text = extract_full_article_content(article_soup)
                    except Exception as e:
                        logger.error(f"Error fetching full article content: {e}")
                        full_text = "خطا در دریافت متن کامل مقاله"

                    news_item = {
                        'id': str(uuid4()),
                        'title': title,
                        'text': full_text,
                        'source': href,

                    }

                    news_items.append(news_item)
                    logger.info(f"Added article from HTML: {title}")

            except Exception as e:
                logger.error(f"Error processing HTML article: {e}")
                continue

        return news_items

    except Exception as e:
        logger.error(f"Error extracting from HTML: {e}")
        return []
