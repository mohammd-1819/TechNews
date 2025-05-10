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

        # First try to extract articles from JSON-LD data which is more reliable
        article_urls = extract_urls_from_jsonld(response.text)

        if article_urls:
            logger.info(f"Found {len(article_urls)} articles from JSON-LD")
            return fetch_articles_details(article_urls)
        else:
            # Fallback to HTML parsing if JSON-LD extraction fails
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

        # Find all script tags with type application/ld+json
        json_ld_scripts = soup.find_all('script', type='application/ld+json')

        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)

                # Check if this is the ItemList JSON-LD
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

        # Extract title
        title_elem = soup.find('h1', class_='b-post__title')
        if not title_elem:
            title_elem = soup.find('h1')
        title = title_elem.get_text().strip() if title_elem else ''

        # Extract excerpt/description
        excerpt_elem = soup.find('div', class_='b-post__excerpt')
        description = excerpt_elem.get_text().strip() if excerpt_elem else ''

        # If no excerpt found, try to get the first paragraph
        if not description:
            first_p = soup.select_one('.b-content p')
            if first_p:
                description = first_p.get_text().strip()

        # Extract full article text
        full_text = extract_full_article_content(soup)

        # Extract date
        date_elem = soup.select_one('.b-post__time')
        published_date_str = date_elem.get_text().strip() if date_elem else None

        # For now, use current time - in a real implementation,
        # you'd want to parse the Persian date
        published_at = timezone.now()

        # Create news item
        if title:
            return {
                'id': str(uuid4()),
                'title': title,
                'text': full_text,  # Add full text content
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
        # روش اول: پیدا کردن محتوای اصلی مقاله با کلاس b-content
        article_content = soup.select_one('.b-content')

        # روش دوم: پیدا کردن محتوا با کلاس entry-content
        if not article_content:
            article_content = soup.select_one('.entry-content')

        # روش سوم: پیدا کردن محتوا از طریق article tag
        if not article_content:
            article_content = soup.select_one('article .post-content')

        # روش چهارم: پیدا کردن هر بخشی که حاوی پاراگراف‌های متعدد است
        if not article_content:
            article_tags = soup.find_all(['div', 'section'],
                                         class_=lambda c: c and ('content' in c.lower() or 'article' in c.lower()))
            for tag in article_tags:
                if len(tag.find_all('p')) > 3:  # اگر بیش از 3 پاراگراف دارد
                    article_content = tag
                    break

        # روش پنجم: بررسی المان‌های main یا article
        if not article_content:
            article_content = soup.select_one('main') or soup.select_one('article')

        if not article_content:
            # اگر هیچ کدام از روش‌ها موفق نبود، متن پاراگراف‌های متوالی را استخراج کنیم
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

        # استخراج متن پاراگراف‌ها
        paragraphs = []
        for p in article_content.find_all(['p', 'h2', 'h3', 'h4', 'ul', 'ol', 'blockquote']):
            text = p.get_text().strip()
            if text and len(text) > 10:  # حذف پاراگراف‌های خالی یا بسیار کوتاه
                paragraphs.append(text)

        if paragraphs:
            return "\n\n".join(paragraphs)
        else:
            # اگر هیچ پاراگرافی یافت نشد، کل متن را برگردانیم
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

        # دیجیاتو از کارت‌های خبری استفاده می‌کند
        articles = soup.select('.b-archive-posts article')

        if not articles:
            articles = soup.select('.b-post-box')

        if not articles:
            articles = soup.select('article')

        logger.info(f"Found {len(articles)} articles from HTML")

        for article in articles:
            try:
                # پیدا کردن لینک
                link_elem = article.find('a', class_='b-post-box__link') or article.find('a')
                if not link_elem:
                    continue

                href = link_elem.get('href', '')
                if not href:
                    continue

                # پیدا کردن عنوان
                title_elem = article.find(class_='b-post-box__title') or article.find(['h1', 'h2', 'h3'])
                title = title_elem.get_text().strip() if title_elem else ''

                # پیدا کردن توضیحات/خلاصه
                excerpt_elem = article.find(class_='b-post-box__excerpt') or article.find('p')
                description = excerpt_elem.get_text().strip() if excerpt_elem else 'بدون توضیحات'

                # بررسی آیا عنوان و لینک معتبر است
                if title and len(title) > 3 and href:
                    # اگر URL کامل نیست، URL کامل بساز
                    if not href.startswith('http'):
                        href = f"https://digiato.com{href}"

                    # استخراج متن کامل مقاله با فراخوانی صفحه مقاله
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
                        'text': full_text,  # Add full text content
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
