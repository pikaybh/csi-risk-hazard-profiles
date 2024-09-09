from playwright.sync_api import TimeoutError
from functools import wraps
import logging
import time

# logger
logger = logging.getLogger('risk_factor_profile')


def retry_on_timeout(retries=10, delay=2, restart_browser_every=5):
    """
    A decorator to retry a function if a TimeoutError occurs. Restarts the browser on every `restart_browser_every` retry.

    Args:
        retries (int): Number of retry attempts. Defaults to 10.
        delay (int): Delay between retries in seconds. Defaults to 2.
        restart_browser_every (int): Restarts the browser on every Nth retry. Defaults to 5.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            browser = kwargs.get('browser')
            while attempt < retries:
                try:
                    return func(*args, **kwargs)
                except TimeoutError as e:
                    attempt += 1
                    if attempt % restart_browser_every == 0 and browser:
                        logger.warning(f"Restarting browser after {attempt} failed attempts.")
                        # Close the existing browser and start a new one
                        browser.close()
                        playwright = kwargs.get('playwright')
                        browser = playwright.chromium.launch(headless=True)
                        page = browser.new_page()
                        kwargs['browser'] = browser
                        kwargs['page'] = page

                    if attempt < retries:
                        logger.warning(f"TimeoutError encountered in {func.__name__}. Retrying {attempt}/{retries}...")
                        time.sleep(delay)
                    else:
                        logger.error(f"TimeoutError in {func.__name__} after {retries} retries.")
                        raise e
        return wrapper
    return decorator