import json
import os
from datetime import datetime

class InstaPhoto:
  def __init__(self, title, filepath, caption, taken_at, url):
    self.title = title
    self.filepath = filepath
    self.caption = caption
    self.taken_at = taken_at
    self.timestamp = datetime.fromisoformat(taken_at)
    self.url = url

date_to_filter = datetime.fromisoformat("2017-01-01T00:00:00+00:00")
print("TEST") 
instaphotos = [];
for f in os.scandir("."):
  if f.is_dir():
    print(f.path) 
    try:
      with open(f.path+'\media.json', encoding = 'cp850') as media:
        data = json.load(media)
        for photo_data in data["photos"]:                
          instaphotos.append(InstaPhoto("TEST", str(photo_data["path"]), str(photo_data["caption"]), photo_data["taken_at"], "https://www.instagram.com/gabryxx7/"))
    except FileNotFoundError: # parent of IOError, OSError *and* WindowsError where available
      print('No media.json in '+f.path)

instaphotos_filtered = list(filter(lambda x: x.timestamp >  date_to_filter, instaphotos))
instaphotos_filtered = list(filter(lambda x: len(x.caption.strip()) > 1, instaphotos_filtered))
instaphotos_filtered.sort(key=lambda x: x.timestamp, reverse=True)

with open("photos.yml", "w+", encoding = 'cp850') as yml_file:
  yml_file.write("preview_folder: /assets/gabryxx7/img/photos/\nfull_folder: /assets/gabryxx7/img/photos/\nphotos:")
  for photo in instaphotos_filtered:
    yml_file.write("\n  - file: "+str(photo.filepath.split("/",1)[1]))             
    yml_file.write("\n    title: TEST")                       
    yml_file.write("\n    caption: |\n     "+str(photo.caption.replace("\n", "\n     ")))                         
    yml_file.write("\n    date: "+str(photo.timestamp.isoformat()))                        
    yml_file.write("\n    url: "+str(photo.url))  

exit(1)