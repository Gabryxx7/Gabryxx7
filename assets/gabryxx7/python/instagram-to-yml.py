import json
import os
from datetime import datetime
import oyaml as yaml

class InstaPhoto:
    def __init__(self, title, filepath, caption, taken_at, location, url):
        self.title = title
        self.file = filepath
        self.caption = caption
        # self.taken_at = taken_at
        self.location = None
        self.timestamp = taken_at
        # self.timestamp = datetime.fromisoformat(taken_at)
        self.url = url
    def __str__(self):
        return str(self.file)

date_to_filter = datetime.fromisoformat("2017-01-01T00:00:00+00:00")
root_folder = "./content"
# root_folder = "."
json_file = "posts_1.json"
print("TEST") 
insta_photos = [];
try:
    with open(root_folder+'/'+json_file, encoding = 'cp850') as media:
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
                exif_data = ""
                if "media_metadata" in post_data and "photo_metadata" in post_data["media_metadata"]:
                    exif_data = str(post_data["media_metadata"]["photo_metadata"]["exif_data"])
                insta_photos.append(InstaPhoto("", files, str(post_data["title"]),
                post_data["creation_timestamp"], exif_data, "https://www.instagram.com/gabryxx7/"))
            except Exception as e:
                print(f"Exception: {e}")
                break
except FileNotFoundError: # parent of IOError, OSError *and* WindowsError where available
    print(f"No {json_file} in {root_folder}")

insta_photos_filtered = list(filter(lambda x: x.timestamp >  date_to_filter.timestamp(), insta_photos))
insta_photos_filtered = list(filter(lambda x: len(x.caption.strip()) > 1, insta_photos_filtered))
insta_photos_filtered.sort(key=lambda x: x.timestamp, reverse=True)
insta_photos_filtered_dict = [x.__dict__ for x in insta_photos_filtered]

with open("photos_new.yml", "w+", encoding = 'utf-8') as yml_file:
    yaml.safe_dump(insta_photos_filtered_dict, yml_file)

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

exit(1)