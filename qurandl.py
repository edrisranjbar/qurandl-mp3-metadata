import os
import eyed3 as the_mp3
from mutagen.mp3 import MP3
import title
from selenium import webdriver
import wget

def display_menu():
    """
        DISPLAY A MENU OF WHAT USER CAN DO
    """
    selected = input("""WHICH ONE? (1-2)
    1) DOWNLOAD MP3 QURAN FILES IN A WEBPAGE
    2) MODIFY NAME AND METADATA
    PLEASE SPECIFIE WITH A NUMBER: 
    """)
    if selected == "1":
        url = input("Type your url: ")
        download_all_mp3_files(url)

    elif selected == "2":
        modify_metatag()

    else:
        print("PLEASE CHOOSE AGAIN!")
        display_menu()

def download_all_mp3_files(url):
    """
        DOWNLOAD ALL MP3 FILE IN A WEBPAGE
    """
    browser = webdriver.Chrome(executable_path='{}/chromedriver'.format(os.curdir))
    browser.get(url)
    links = browser.find_elements_by_link_text('اضغط هنا للتحمیل')
    for link in links:
        try:
            href = link.get_attribute("href")
            print("DOWNLOADING {}".format(href))
            wget.download(href)
        except:
            print("Can't download {}".format(link))
    print("Download Completed!")
    modify_metatag()
    return True

def modify_metatag():
    """
    REMOVE PREVIOUS METADATA AND EMBED
    OUR META DATA TO MP3 FILES.
    """
    QARI_NAME = input("Enter qari name: ").title()
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
    return True


if __name__ == "__main__":
    display_menu()