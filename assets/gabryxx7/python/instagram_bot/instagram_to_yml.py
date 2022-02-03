import json
import os
from datetime import datetime
import oyaml as yaml
from geopy.geocoders import Nominatim
from geopy.adapters import AioHTTPAdapter
import requests #to make TMDB API calls
import urllib.parse
import os
import selenium
from seleniumwire import webdriver
# from selenium import webdriver
from selenium.webdriver.firefox.options import Options as firefox_options
from selenium.webdriver.chrome.options import Options as chrome_options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located, element_to_be_clickable
from selenium.common.exceptions import ElementClickInterceptedException
import time
import io
import calendar
import pickle
import traceback
import shutil
import re


class Post:
    def __init__(self, timestamp=None, caption=None, post_id=None, location=None, shortcode=None, comments_count=None,likes_count=None, url=None, file=None, exif_data=None, bot_added=False):
        self.timestamp = timestamp
        self.datetime_obj = None
        self.datetime = None
        self.caption = caption
        self.id = post_id
        self.location = location
        self.shortcode = shortcode
        self.comments_count = comments_count
        self.likes_count = likes_count
        self.url = url
        self.file = file
        self.exif_data = exif_data
        self.bot_added = bot_added
        if self.timestamp is not None:
            self.datetime_obj = datetime.fromtimestamp(self.timestamp)
            self.datetime = str(self.datetime_obj.isoformat())

    def __str__(self):
        return f"Post: [time:{self.timestamp}, datetime:{self.datetime} caption:{self.caption}]"
    

class ScraperBot:
    class Geolocator:
        def __init__(self, max_geolocators=10):
            self.max_geolocators = max_geolocators
            self.geolocator_index = 0
            self.geolocators = []
            for i in range(0, self.max_geolocators):            
                self.geolocators.append(Nominatim(user_agent=f"insta-gabryxx7-geocoding-{i}"))
            self.geolocator = self.geolocators[self.geolocator_index]
            self.zoom = 17

        def geolocate(self, exif_data):
            self.geolocator = self.geolocators[self.geolocator_index]
            self.using_geolocator = self.using_geolocator + 1 if self.using_geolocator < self.max_geolocators-1 else 0
            if exif_data is not None:
                try:
                    location = self.geolocator.reverse([exif_data[0]["latitude"], exif_data[0]["longitude"]], zoom=self.zoom)
                    return location
                except Exception as e:
                    print(f"Exception geolocating coordinates from exif_data {exif_data[0]}\n{e}")                
                    return None

    def __init__(self, metadata_path="", export_path="", logger=None):
        self.logger = logger
        self.geolocator = ScraperBot.Geolocator()
        self.edges_list = []
        self.exported_data = None
        self.export_path=export_path    
        self.metadata_path=metadata_path    
        try:
            with open(f"{self.export_path}/content/posts_1.json", "r") as f:
                self.exported_data = json.load(f)     
            print(f"Total edges: {len(self.exported_data)}")
        except Exception as e:
            print(f"No export json file!\nException: {e}")

        try:
            with open(f"{self.metadata_path}/scraped_data.json", "r") as f:
                self.edges_list = json.load(f)     
            print(f"Total edges: {len(self.edges_list)}")
        except Exception as e:
            print(f"No metadata json file! You can get it by going to 'https://www.instagram.com/<ig_username>/?__a=1'\nException: {e}")
            

    def get_post_metadata(self, data, keys_path):
        try:
            for key in keys_path:
                data = data[key]
            return data
        except Exception as e:
            self.logger.e(f"Exception getting key {key} from {keys_path}: {e}")
            return None

    def find_post_metadata(self, post):
        for edge in self.edges_list:
            node = edge["node"]
            if "taken_at_timestamp" in node and int(node["taken_at_timestamp"]) == int(post.timestamp):
                print(f"Found new metadata for {node['shortcode']} taken at {post.timestamp}")
                return node
        return None

    def post_from_metadata(self, metadata, photo_folder="."):
        post = Post(timestamp=metadata['taken_at_timestamp'], bot_added=True)
        post = self.update_post_metadata(post, metadata=metadata, photo_folder=photo_folder)
        return post
            
    def update_post_metadata(self, post, metadata=None, photo_folder="."):
        if metadata is None:
            if len(self.edges_list) > 0:
                metadata = self.find_post_metadata(post)
        if metadata is not None:
            post.caption = self.get_post_metadata(metadata, ["edge_media_to_caption","edges",0, "node","text"])
            post.timestamp = self.get_post_metadata(metadata, ["taken_at_timestamp"])
            post.datetime_obj = datetime.fromtimestamp(post.timestamp)
            post.datetime = str(post.datetime_obj.isoformat())
            post.id = self.get_post_metadata(metadata, ["id"])
            post.location = self.get_post_metadata(metadata, ['location','name'])
            post.shortcode = self.get_post_metadata(metadata, ['shortcode'])
            post.comments_count = self.get_post_metadata(metadata, ['edge_media_to_comment', 'count'])
            post.likes_count = self.get_post_metadata(metadata, ['edge_media_preview_like', 'count'])
            post.url = f"https://www.instagram.com/p/{post.shortcode}/"
            post.file = self.download_post_images(metadata, root_folder=f"{photo_folder}/", base_path=f"{post.datetime_obj.year:02d}{post.datetime_obj.month:02d}")
            self.logger.i(f"Post updated {post}")     
        return post

    def download_post_images(self, metadata, root_folder, base_path):
        files_paths = []
        files_paths.append(self.download_image(self.get_post_metadata(metadata, ["display_url"]), root_folder, base_path))
        if "edge_sidecar_to_children" in metadata:
            first_skipped = False
            for edge in metadata["edge_sidecar_to_children"]["edges"]:
                if not first_skipped:
                    first_skipped = True
                else:
                    sub_node = edge["node"]
                    files_paths.append(self.download_image(self.get_post_metadata(sub_node, ["display_url"]), root_folder,  base_path))
        return files_paths

    def download_image(self, url, root_folder, base_path):
        response = requests.get(url, stream=True)
        match = re.search(r"s[0-9]{1,5}x[0-9]{1,5}\/(.*)\?", url)
        filename = match.group(1)
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        with open(root_folder+base_path+'/'+filename, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
        return base_path+'/'+filename

    def read_exported_data(self):
        self.logger.i("START!")
        posts_list = [];
        for post in self.exported_data:         
            try:
                if len(post["media"]) <= 1:
                    post_data = post["media"][0]
                else:
                    post_data = post
                files = []
                for photo_data in post["media"]:
                    files.append(str(photo_data["uri"]).split("/",2)[2])
                exif_data = None
                if "media_metadata" in post_data and "photo_metadata" in post_data["media_metadata"]:
                    exif_data = post_data["media_metadata"]["photo_metadata"]["exif_data"]
                    new_post = InstaPhoto(files, str(post_data["title"]),post_data["creation_timestamp"], exif_data)
                    new_post.update_from_metadata()
                    posts_list.append(new_post)
                # print(f"Processed: {posts_list[-1].datetime}")
            except Exception as e:
                self.logger.e(f"Exception in reading exported data: {e}")
                break
        return posts_list

    def filter_sort_photos(self, posts_list, date_to_filter=None, excluded_keys=None):
        excluded_keys = [] if excluded_keys is None else excluded_keys
        filtered_list = []
        for photo in posts_list:
            if date_to_filter is None:
                filtered_list.append(photo.__dict__)
            elif photo.timestamp > date_to_filter.timestamp() and len(photo.caption.strip()) > 1:
                filtered_list.append(photo.__dict__)
        for photo_dict in filtered_list:
            for key in excluded_keys:
                photo_dict.pop(key)
        filtered_list.sort(key=lambda x: x["timestamp"], reverse=True)
        return filtered_list

    def export_to_yaml(self, posts_list, filename):
        with open(filename, "w+", encoding = 'utf-8') as yml_file:
            yaml.safe_dump(posts_list, yml_file)

    def update_photo_list(self, photo_list_path, photo_folder="."):
        try:
            with open(photo_list_path, "r") as f:
                photo_list = yaml.safe_load(f)
        except Exception as e:
            self.logger.e(f"Error opening photo list yaml file at {photo_list_path}:\n{e}")
        new_posts_list = []
        last_post = photo_list["photos"][0]
        last_timestamp = last_post["timestamp"]
        for edge in self.edges_list:
            node = edge["node"]
            if "taken_at_timestamp" in node and int(node["taken_at_timestamp"]) > int(last_timestamp):
                self.logger.i(f"Found new post! {node['taken_at_timestamp']} {self.get_post_metadata(node, ['location','name'])}")
                new_post = self.post_from_metadata(node, photo_folder)                
                new_posts_list.append(new_post)
        if len(new_posts_list) > 0:
            filtered_list = self.filter_sort_photos(new_posts_list)
            self.logger.i(f"New posts to add {len(filtered_list)}")
            for i in reversed(range(0, len(filtered_list)-1)):       
                photo_list["photos"].insert(0, filtered_list[i])
            self.export_to_yaml(photo_list, photo_list_path)
            self.logger.i(f"Updated file {photo_list_path}")
            self.logger.s(f"Added {len(filtered_list)} new instagram posts to your website! {str(filtered_list)}")
            os.system("sudo JEKYLL_ENV=production bundle exec jekyll build")
        else:
            self.logger.s(f"All up to date!")
        return photo_list

    # max_pages: -1 for all of them, 0 only for the first one (so __a1) etc...
    def scrape_profile(self, ig_username, cookies, query_hash, max_pages=-1):
        edges = []
        starting_url = f"https://www.instagram.com/{ig_username}/?__a=1"
        query_url = 'https://www.instagram.com/graphql/query?query_hash={query_hash}&variables='
        # Get your cookie by navigating to your profile e.g https://www.instagram.com/gabryxx7/
        # Open Chrome inspector and open the tab "Network" to start recording
        # Then scroll down to load the next posts in the timeline
        # Filter the requests ny "?query", click one of them
        # On the panel on the right, go to the "Headers" tab
        # Scroll down until you see "cookie", then right click -> copy

        # if cookies is None:
        #     cookies = get_insta_cookies();

        first_page_data = requests.get(starting_url, cookies=cookies)
        first_page = first_page_data.json()
        user_data = first_page["graphql"]["user"]
        edges.extend(user_data["edge_owner_to_timeline_media"]["edges"])
        total = user_data["edge_owner_to_timeline_media"]["count"]
        token = user_data["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]
        vars_template = "{'id':"+user_data['id']+",'first':12,'after':'<token>'}"

        page_n = 0
        while token is not None:
            self.logger.i(f"Retreiving page {page_n}")
            if max_pages >= 0:
                if page_n >= max_pages:
                    print(f"Reached max_pages {max_pages}")
                    break
            vars_url_encoded = urllib.parse.quote(vars_template.replace("<token>", token).encode('utf8'))
            request_url = query_url+vars_url_encoded
            self.logger.i(f"Sending request with token: {token}\n{request_url}")
            result = requests.get(request_url, cookies=cookies).json()
            try:
                edges.extend(result["data"]["user"]["edge_owner_to_timeline_media"]["edges"])
            except Exception as e:
                self.logger.e(f"Error in retreiving edges list: {e}")

            token = None
            self.logger.i(f"\nTOTAL {len(edges)}/{total}")
            try:
                has_next_page = result["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["has_next_page"]
                if has_next_page:
                    token = result["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]
            except Exception as e:
                self.logger.e(f"Error in retreiving token: {e}")
            page_n += page_n
        return edges

    def get_insta_cookies(self):
        # login_url = "https://www.instagram.com/accounts/login/"
        login_url = "https://www.instagram.com/gabryxx7/?__a=1"
        # login_url = "https://www.google.com"
        options = firefox_options()
        # options = chrome_options()
        options.headless = True
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36")
        print(f"Options created") 
        driver = selenium.webdriver.Firefox(options=options)
        # driver = selenium.webdriver.Firefox(options=options)
        print(f"WebDriver created") 
        wait = WebDriverWait(driver, 10)
        print(f"Opening Firefox and navigating to {login_url}")
        try:
            driver.get(login_url)
            ##  Print request headers
            # for request in driver.requests:
            #     print(request.url) # <--------------- Request url
            #     print(request.headers) # <----------- Request headers
            #     print(request.response.headers) # <-- Response headers
            print(f"Waiting for redirection...") 
            time.sleep(5)
            with open("login_page.html", "w") as f:
                f.write(driver.page_source)
            print(f"Waiting for clickable username field...") 
            username_field = wait.until(element_to_be_clickable(By.CSS_SELECTOR, "input[name='username']"))
            username_field.clear()
            username_field.send_keys(login_data["username"])
            print(f"Waiting for clickable password field...") 
            password_field = wait.until(element_to_be_clickable(By.CSS_SELECTOR, "input[name='password']"))
            password_field.clear()
            password_field.send_keys(login_data["password"])
            print(f"Waiting for clickable submit button...") 
            wait.until(element_to_be_clickable((By.XPATH, "//button[@type='submit'"))).click()
            with open("login_page.html", "w") as f:
                f.write(driver.page_source)
            pickle.dump( driver.get_cookies() , open("cookies.pkl","wb"))
        except Exception as e:
            print(f"Exception in getting cookies: {e}")
            traceback.print_exc()
            driver.quit()
    
def main():
    with open("instagram_login.no_commit", "r") as f:
        login_data = yaml.safe_load(f)
    cookies = {'cookie':login_data['cookie']}
    InstaPhoto.init()
    InstaPhoto.nodes = scrape_instagram_data(0, cookies)
    with open('scraped_data.json', 'w') as f:
        json.dump(edges, f)
    # date_to_filter = datetime.fromisoformat("2017-01-01T00:00:00+00:00")
    # insta_photos = extract_data("./content", "posts_1.json")
    # filtered_list = filter_sort_photos(posts_list, date_to_filter, excluded_keys=["bot_added"])
    # export_to_yaml(insta_photos, date_to_filter)

if __name__ == "__main__":
    # get_insta_cookies()
    main()