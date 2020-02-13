import os
import eyed3
import title
import sys
import codecs
from mutagen.mp3 import MP3
QARI_NAME = input("Enter qari name: ")
for i in range(1,115):
    try:
        i = str(i)
        i = i.zfill(3)
        # Renaming file name
        ## INSTEAD OF SPACE IN QARI NAME WE SHOULD HAVE DASH.
        QARI = QARI_NAME.replace(" ","-")
        path = QARI + "-" + i + ".mp3"
        os.rename(i+".mp3",path)
        # Rmove previous metadata
        mp3 = MP3(path)
        try:
           mp3.delete()
           mp3.save()
        # Setting Metadata
        eyed3.load(path)
        eyed3.delete()
        eyed3.tag.artist(QARI_NAME)
        eyed3.tag.album("Qurandl")
        eyed3.tag.title(title[i])
        eyed3.tag.track_num = i
        eyed3.tag.images.set(3, open('cover.jpg','rb').read(),'image/jpeg')
        eyed3.tag.save()
    except:
        continue
