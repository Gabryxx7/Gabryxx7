from instagram_to_yml import *
from logger import Logger
from datetime import datetime
import traceback


def main():
    with open("/home/gabryxx7/repos/blog/_data/photos-list.yml", "r") as f:
        photo_list = yaml.safe_load(f)
    with open("insta_config.no_commit", "r") as f:
        config_data = yaml.safe_load(f)
    
    logger = Logger(f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log", config_data)
    try:
        scraper_bot = ScraperBot(metadata_path=config_data["metadata_path"], export_path=config_data["export_path"], logger=logger)
        scraper_bot.scrape_profile("gabryxx7", {'cookie':config_data['cookie']}, config_data["query_hash"], max_pages=0)
        scraper_bot.update_photo_list(photo_list)
    except Exception as e:
        logger.e(f"Exception in the main loop: {e}\n{traceback.format_exc()}")
    logger.close()


if __name__ == "__main__":
    # get_insta_cookies()
    main()
