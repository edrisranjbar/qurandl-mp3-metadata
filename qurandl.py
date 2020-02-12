import os
import eyed3 as mp3
#import title
QARI_NAME = input("Enter qari name: ")
for i in range(1,115):
    try:
        i = str(i)
        i = i.zfill(3)
        # Renaming file name
        ## INSTEAD OF SPACE IN QARI NAME WE SHOULD HAVE DASH.
        QARI = QARI.replace(" ","-")
        path = QARI + "-" + i + ".mp3"
        os.rename(i+".mp3",path)
        # Setting Metadata
        mp3.load(path)
        mp3.tag.artist(QARI_NAME)
        mp3.tag.album("Qurandl")
        mp3.tag.title(title[i])
        mp3.tag.track_num = i
        mp3.tag.images.set(3, open('cover.jpg','rb').read(),'image/jpeg')
        mp3.tag.save()
    except:
        continue
