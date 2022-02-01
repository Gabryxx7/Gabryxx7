import json
import os
from datetime import datetime
import oyaml as yaml
from geopy.geocoders import Nominatim
from geopy.adapters import AioHTTPAdapter

class InstaPhoto:
    using_geolocator = 0
    max_geolocators = 10
    geolocators = []
    for i in range(0, max_geolocators):            
        geolocators.append(Nominatim(user_agent=f"insta-gabryxx7-geocoding-{i}"))
    zoom = 17

    def __init__(self, title, filepath, caption, taken_at, exif_data, url):
        self.title = title
        self.file = filepath
        self.caption = caption
        self.exif_data = exif_data
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
        self.timestamp = taken_at
        self.datetime = str(datetime.fromtimestamp(self.timestamp).isoformat())
        self.url = url
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
                    post_data["creation_timestamp"], exif_data, "https://www.instagram.com/gabryxx7/"))
                    print(f"Processed: {insta_photos[-1].datetime}")
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

def main():
    date_to_filter = datetime.fromisoformat("2017-01-01T00:00:00+00:00")
    insta_photos = extract_data("./content", "posts_1.json")
    excluded_keys = []
    export_to_yaml(insta_photos, date_to_filter)

if __name__ == "__main__":
    main()