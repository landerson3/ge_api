filename = '/Users/landerson2/Downloads/CurvedBurlPanelDouble_DoorSideboard_CamelOak_prod25140356_E817834854_Top.jpg'


import pyexiv2
import json

metadata = pyexiv2.ImageMetadata(filename)
metadata.read()
userdata={'Category':'Human',
          'Physical': {
              'skin_type':'smooth',
              'complexion':'fair'
              },
          'Location': {
              'city': 'london'
              }
          }
metadata['Exif.Photo.UserComment']=json.dumps(userdata)
metadata.write()