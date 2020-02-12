import os
import eyed3 as mp3
#import title
QARI_NAME = input("Enter qari name: ")
for i in range(1,115):
    try:
        i = str(i)
        i = i.zfill(3)
        # Renaming file name
        ## TODO: INSTEAD OF SPACE IN QARI NAME WE SHOULD HAVE DASH.
        path = QARI_NAME + "-" + i + ".mp3"
        os.rename(i+".mp3",path)
        # Setting Metadata
        mp3.load(path)
        mp3.tag.artist(QARI_NAME)
        mp3.tag.album("Qurandl")
        title = ""
        mp3.tag.title(title)
        mp3.tag.track_num = i
    except:
        continue
