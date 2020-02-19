"""
    REMOVE PREVIOUS METADATA AND EMBED
    OUR META DATA TO MP3 FILES.
"""
import os
import eyed3 as the_mp3
from mutagen.mp3 import MP3
import title
if __name__ == "__main__":
    QARI_NAME = input("Enter qari name: ")
    for i in range(1, 115):
        try:
            i = str(i)
            i = i.zfill(3)
            # Renaming file name
            # INSTEAD OF SPACE IN QARI NAME WE SHOULD HAVE DASH.
            QARI = QARI_NAME.replace(" ", "-")
            path = QARI + "-" + i + ".mp3"
            os.rename(i + ".mp3", path)
            # Remove previous metadata
            remover = MP3(path)
            remover.delete()
            remover.save()
            # Setting Metadata
            the_mp3.load(path)
            the_mp3.delete()
            the_mp3.tag.artist(QARI_NAME)
            the_mp3.tag.album("Qurandl")
            the_mp3.tag.title(title.FILE_TITLES[i])
            the_mp3.tag.track_num = i
            the_mp3.tag.images.set(3, open('cover.jpg', 'rb').read(), 'image/jpeg')
            the_mp3.tag.save()
        except:
            continue
