from insta_scraper import *
from pylogger import *
from datetime import datetime
import traceback
from bs4 import BeautifulSoup

def update_github_feed(readme_path, photo_list):
    soup = ""
    with open(readme_path, "r", encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
        index = 0
        for img in soup.select('.github-feed .github-insta-feed img'):
            post = photo_list['photos'][index]
            img['src'] = f"{photo_list['full_folder']}{post['file'][0]}"
            index += 1
    with open(readme_path, "w", encoding='utf-8') as f:
        print(f"Writing to {readme_path}")
        f.write(str(soup))


def main():
    with open("/home/gabryxx7/repos/blog/assets/gabryxx7/python/instagram_bot/insta_config.no_commit.yaml", "r") as f:
        config_data = yaml.safe_load(f)    
    
    pb_token = config_data.get("pushbullet_token", "")
    log = Log(config_data["logs_folder"])
    log.init_pushbullet(pb_access_token=pb_token)
    log.set_pb_logging_level(levels_list=["s"])
    try:          
        scraper_bot = ScraperBot(metadata_path=config_data["metadata_path"], export_path=config_data["export_path"],
        tmp_files_folder=config_data["tmp_files_folder"], log=log)
        profile_metadata = scraper_bot.scrape_profile_metadata("gabryxx7", {'cookie':config_data['cookie']}, config_data["query_hash"], max_pages=-0)
        photo_list = scraper_bot.update_photo_list(edges_list=profile_metadata["posts_data"], photo_list_path=config_data["photo_list_filepath"], photo_folder=config_data["photo_base_path"])
        update_github_feed(config_data["github_readme_path"], photo_list)
    except Exception as e:
        log.e("main", f"Exception in the main loop: {e}\n{traceback.format_exc()}")
    log.stop()


if __name__ == "__main__":
    # get_insta_cookies()
    main()
