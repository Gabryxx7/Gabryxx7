import json
import os
from datetime import datetime
import oyaml as yaml
from geopy.geocoders import Nominatim
from geopy.adapters import AioHTTPAdapter
import requests #to make TMDB API calls
import urllib.parse


class InstaPhoto:
    using_geolocator = 0
    max_geolocators = 10
    geolocators = []
    for i in range(0, max_geolocators):            
        geolocators.append(Nominatim(user_agent=f"insta-gabryxx7-geocoding-{i}"))
    zoom = 17
    profile_metadata_json = "scraped_data.json"
    metadata = {}
    found_metadata = 0
    nodes = []
    try:
        with open(profile_metadata_json, "r") as f:
            nodes = json.load(f)     
        print(f"Total nodes: {len(nodes)}")
    except Exception as e:
        print(f"No metadata json file! You can get it by going to 'https://www.instagram.com/<ig_username>/?__a=1'\nException: {e}")
        metadata = None

    def geolocate(self, exif_data):
        geolocator = InstaPhoto.geolocators[InstaPhoto.using_geolocator]
        InstaPhoto.using_geolocator = InstaPhoto.using_geolocator + 1 if InstaPhoto.using_geolocator < InstaPhoto.max_geolocators-1 else 0
        if exif_data is not None:
            try:
                location = geolocator.reverse([exif_data[0]["latitude"], exif_data[0]["longitude"]], zoom=17)
                self.location = str(location)
                self.location_raw = location.raw
            except Exception as e:
                print(f"Exception getting location {exif_data[0]}: {e}")                
                self.location = None

    def get_metadata(self, data, keys_path):
        try:
            for key in keys_path:
                data = data[key]
            return data
        except Exception as e:
            print(f"Exception getting key {key}: {e}")
            return None


    def fill_in_metadata(self, timestamp):
        print(f"Getting metadata for {timestamp} from {len(InstaPhoto.nodes)} nodes")
        for node_obj in InstaPhoto.nodes:
            node = node_obj["node"]
            if "taken_at_timestamp" in node and int(node["taken_at_timestamp"]) == int(timestamp):
                print(f"{InstaPhoto.found_metadata} - Found metadata for {timestamp}")
                self.location = self.get_metadata(node, ['location','name'])
                self.shortcode = self.get_metadata(node, ['shortcode'])
                self.comments_count = self.get_metadata(node, ['edge_media_to_comment', 'count'])
                self.likes_count = self.get_metadata(node, ['edge_media_preview_like', 'count'])
                self.url = f"https://www.instagram.com/p/{self.shortcode}/"
                InstaPhoto.found_metadata = InstaPhoto.found_metadata + 1                
                break


    def __init__(self, title, filepath, caption, timestamp, exif_data):
        self.title = title
        self.file = filepath
        self.caption = caption
        self.exif_data = exif_data        
        self.timestamp = timestamp
        self.datetime = str(datetime.fromtimestamp(self.timestamp).isoformat())
        self.url = ""
        if InstaPhoto.metadata is not None:
            self.fill_in_metadata(self.timestamp)

    def __str__(self):
        return str(self.file)

def extract_data(root_folder, json_file):
    print("START!")
    insta_photos = [];
    try:
        with open(root_folder+'/'+json_file, encoding = 'utf-8') as media:
            data = json.load(media)
            for post in data:         
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
                    insta_photos.append(InstaPhoto("", files, str(post_data["title"]),
                    post_data["creation_timestamp"], exif_data))
                    # print(f"Processed: {insta_photos[-1].datetime}")
                except Exception as e:
                    print(f"Exception: {e}")
                    break
    except FileNotFoundError: # parent of IOError, OSError *and* WindowsError where available
        print(f"No {json_file} in {root_folder}")
    return insta_photos

def filter_sort_photos(insta_photos, date_to_filter, excluded_keys=None):
    excluded_keys = [] if excluded_keys is None else excluded_keys
    insta_photos_filtered = []
    for photo in insta_photos:
        if photo.timestamp >  date_to_filter.timestamp() and len(photo.caption.strip()) > 1:
            photo_dict = photo.__dict__
            for key in excluded_keys:
                photo_dict.pop(key)
            insta_photos_filtered.append(photo_dict)
    insta_photos_filtered.sort(key=lambda x: x["timestamp"], reverse=True)
    return insta_photos_filtered

def export_to_yaml(insta_photos, date_to_filter, excluded_keys=None):
    insta_photos_filtered = filter_sort_photos(insta_photos, date_to_filter, excluded_keys)
    with open("photos_new.yml", "w+", encoding = 'utf-8') as yml_file:
        yaml.safe_dump(insta_photos_filtered, yml_file)

def export_to_yaml_custom(insta_photos, excluded_keys=None):
    insta_photos_filtered = filter_sort_photos(insta_photos, date_to_filter, excluded_keys)
    # with open("photos.yml", "w+", encoding = 'utf-8') as yml_file:
    #     yml_file.write("preview_folder: /assets/gabryxx7/img/photos/\nfull_folder: /assets/gabryxx7/img/photos/\nphotos:")
    #     for photo in insta_photos_filtered:
    #         # print(photo.file)
    #         if not isinstance(photo.file, list):
    #             yml_file.write("\n -file: "+str(photo.file.split("/",2)[2]))          
    #         else:
    #             yml_file.write("\n -files: ")    
    #             for photo_file in reversed(photo.file):
    #                 yml_file.write("\n   -"+str(photo_file.split("/",2)[2]))    
    #         yml_file.write("\n title: " +str(photo.title))                       
    #         yml_file.write("\n caption: |\n  "+str(photo.caption.replace("\n", "\n     ")))                         
    #         yml_file.write("\n timestamp: "+ str(photo.timestamp))                  
    #         yml_file.write("\n date: "+str(datetime.fromtimestamp(photo.timestamp).isoformat())) 
    #         if len(str(photo.location)) > 1:                                         
    #             yml_file.write("\n exif: "+str(photo.location))                        
    #         yml_file.write("\n url: "+str(photo.url))  

def scrape_instagram_data():
    edges = []
    insta_start = "https://www.instagram.com/gabryxx7/?__a=1"
    insta_request = 'https://www.instagram.com/graphql/query?query_hash=8c2a529969ee035a5063f2fc8602a0fd&variables='
    # Get your cookie by navigating to your profile e.g https://www.instagram.com/gabryxx7/
    # Open Chrome inspector and open the tab "Network" to start recording
    # Then scroll down to load the next posts in the timeline
    # Filter the requests ny "?query", click one of them
    # On the panel on the right, go to the "Headers" tab
    # Scroll down until you see "cookie", then right click -> copy
    cookies = {'cookie':'mid=YZ85PgAEAAFtL_SbS8UxVNumcZ1r; ig_did=646D2F74-769B-4ECF-A37A-7E1753980E77; ig_nrcb=1; fbm_124024574287414=base_domain=.instagram.com; shbid="10635\05434070871\0541675137017:01f729c92e01c614253fd4fef19b5dd1d9e43d3e32b0a2dfe1015ca30470f7a0a457e1c1"; shbts="1643601017\05434070871\0541675137017:01f72a131de9c768e4094383b626f26c06c8e421dd5be94d7e1dbe793ae6ed2706b5cc7b"; csrftoken=s51d3SFVz6noMHrbALm0hxeeDhMmZy7r; ds_user_id=34070871; sessionid=34070871%3A7SWMMpNuPRkyjC%3A21; fbsr_124024574287414=qXWvc0Crdq3RUeBAFGQCVn5jn-11AX2odzDfckYEvjI.eyJ1c2VyX2lkIjoiMTAwMDA3MDA3ODMzNDA2IiwiY29kZSI6IkFRQkl2U3VhbDE2S3Q5ZHZZc0NfaHdJRHZzZ3VhNjM5NEtlU3l1UzdyRXhjMW81MDV1cVFWZzNYLXBpT3ZpSlFnNDFjeEZwTndvSFJTeTBKZ09ZbDNXUmIyb0ZtbnVfUlhwaGpwR0dIMlR2a1ZXS3FOMDBBZXZEcmNCelEzSlFXNTJOaEkyS3V3ekx6LWpzQmE4dm5yNmhBQzg5b0lncEhkSmlxT21RbjFteW9QMGlmOXdCQmc5UjQxM1RLai13d2hyeEdMMGVUZnJmQ2k4cVV6d3gyQl9jM1E3M2lfYk10R3RXRndEWmNWYnVmVEpfWkE5NjRMX1Vtb0NZMVJZNzI5dVVXS01fRlIzaGc0bDFHQWFWeWllRG1Ddms1OWdWa0FJSmhtM3FCclBKcTlZYndRbVE4dW4tUnBMSnNoNFdTX21wNHlnTmFMaGpYbnB3dF8zQzFCTXVvIiwib2F1dGhfdG9rZW4iOiJFQUFCd3pMaXhuallCQUdGczRaQWhMMXJPMGhnSU9MM004RWt0bmNRWkFtcFpDdXB6R3l5aEpaQXVhYVRaQzlsZFRwRFhaQjBYa1JZSzhxTVJJUURnc1laQ1JPRkU3M0pQTkFHcW56WkJ5VkNuZTZQa1BvTnlRbFhYclpCblZveWJNVjZEcFNRSnprT2wybkl3OUxmbmZ6V3VmQWE3WkFUWkNWd0lTTmpaQXpZMHJVN0h0bERnSWZMYlhNTkIiLCJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImlzc3VlZF9hdCI6MTY0MzcxNzQ2OH0; fbsr_124024574287414=qXWvc0Crdq3RUeBAFGQCVn5jn-11AX2odzDfckYEvjI.eyJ1c2VyX2lkIjoiMTAwMDA3MDA3ODMzNDA2IiwiY29kZSI6IkFRQkl2U3VhbDE2S3Q5ZHZZc0NfaHdJRHZzZ3VhNjM5NEtlU3l1UzdyRXhjMW81MDV1cVFWZzNYLXBpT3ZpSlFnNDFjeEZwTndvSFJTeTBKZ09ZbDNXUmIyb0ZtbnVfUlhwaGpwR0dIMlR2a1ZXS3FOMDBBZXZEcmNCelEzSlFXNTJOaEkyS3V3ekx6LWpzQmE4dm5yNmhBQzg5b0lncEhkSmlxT21RbjFteW9QMGlmOXdCQmc5UjQxM1RLai13d2hyeEdMMGVUZnJmQ2k4cVV6d3gyQl9jM1E3M2lfYk10R3RXRndEWmNWYnVmVEpfWkE5NjRMX1Vtb0NZMVJZNzI5dVVXS01fRlIzaGc0bDFHQWFWeWllRG1Ddms1OWdWa0FJSmhtM3FCclBKcTlZYndRbVE4dW4tUnBMSnNoNFdTX21wNHlnTmFMaGpYbnB3dF8zQzFCTXVvIiwib2F1dGhfdG9rZW4iOiJFQUFCd3pMaXhuallCQUdGczRaQWhMMXJPMGhnSU9MM004RWt0bmNRWkFtcFpDdXB6R3l5aEpaQXVhYVRaQzlsZFRwRFhaQjBYa1JZSzhxTVJJUURnc1laQ1JPRkU3M0pQTkFHcW56WkJ5VkNuZTZQa1BvTnlRbFhYclpCblZveWJNVjZEcFNRSnprT2wybkl3OUxmbmZ6V3VmQWE3WkFUWkNWd0lTTmpaQXpZMHJVN0h0bERnSWZMYlhNTkIiLCJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImlzc3VlZF9hdCI6MTY0MzcxNzQ2OH0; rur="EAG\05434070871\0541675253611:01f787ce707ac0f5f533e81724059f173023167fc438d03f2dab633cf27fc5c6a67657a9"'}

    first_page = requests.get(insta_start, cookies=cookies).json()
    edges.extend(first_page["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"])
    total = first_page["graphql"]["user"]["edge_owner_to_timeline_media"]["count"]
    token = first_page["graphql"]["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]
    # token = "QVFDQ2xwRlpvc3pYR0tSOGJKTmdvUXZyLV85TFp2c2ctZzlQUmdpWENCaVVaemxyTnJOREF6b1Rfb1d1U0J6Y1FRdDRXZW95dG5UczN4SXh0QVl2cnp5ag=="
    # print(f"First token: {token}")
    variables_template = '{"id":"34070871","first":12,"after":"<token>"}'


    while token is not None:     
        variables_url_encoded = urllib.parse.quote(variables_template.replace("<token>", token).encode('utf8'))
        print(f"Sending request with token: {token}\n{insta_request+variables_url_encoded}")
        result = requests.get(insta_request+variables_url_encoded, cookies=cookies).json()
        try:
            edges.extend(result["data"]["user"]["edge_owner_to_timeline_media"]["edges"])
        except Exception as e:
            print(f"Error in retreiving edges list: {e}")
        token = None
        print(f"\n- TOTAL {len(edges)}/{total}")
        try:
            has_next_page = result["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["has_next_page"]
            if has_next_page:
                token = result["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]
        except Exception as e:
            print(f"Error in retreiving token: {e}")

    with open('scraped_data.json', 'w') as f:
        json.dump(edges, f)

    return edges

def main():
    # InstaPhotos.nodes = scrape_instagram_data()
    date_to_filter = datetime.fromisoformat("2017-01-01T00:00:00+00:00")
    insta_photos = extract_data("./content", "posts_1.json")
    excluded_keys = []
    export_to_yaml(insta_photos, date_to_filter)

if __name__ == "__main__":
    main()