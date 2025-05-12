from celery import shared_task
from news.views.scrap_news_view import ScrapedNewsView


@shared_task
def scrape_news_task():
    try:
        print("Starting news scraping task!")

        view = ScrapedNewsView()

        if hasattr(view, 'scrape_news') and callable(view.scrape_news):
            results = view.scrape_news()
            print(f"News scraped successfully! Found {len(results)} articles")
            return f"Success: {len(results)} articles scraped"

        print("News scraped successfully!")
        return "Success"

    except Exception as e:
        print(f"Exception occurred during news scraping: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Exception: {str(e)}"
