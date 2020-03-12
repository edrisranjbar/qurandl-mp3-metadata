import os, re, wget, zipfile
import title,config
import shutil
import eyed3 as the_mp3
from mutagen.mp3 import MP3
from selenium import webdriver
from ftplib import FTP


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class FtpUploadTracker:
    sizeWritten = 0
    totalSize = 0
    lastShownPercent = 0

    def __init__(self, totalSize):
        self.totalSize = totalSize

    def handle(self, block):
        self.sizeWritten += 1024
        percentComplete = round((self.sizeWritten / self.totalSize) * 100,2)

        if self.lastShownPercent != percentComplete:
            self.lastShownPercent = percentComplete
            clear()
            print(f"{bcolors.OKGREEN}{str(percentComplete)} percent uploaded{bcolors.ENDC}")


def display_menu():
    """
        DISPLAY A MENU OF WHAT USER CAN DO
    """
    print(f"{bcolors.HEADER}{bcolors.BOLD}************************************************{bcolors.ENDC}")
    print(f"{bcolors.HEADER}{bcolors.BOLD}*****  Quran Download - Alsalamo Alaykom  ******{bcolors.ENDC}")
    print(f"{bcolors.HEADER}{bcolors.BOLD}************************************************{bcolors.ENDC}")
    selected = input(f"""{bcolors.WARNING}WHICH ONE? (1-2) {bcolors.ENDC}
    1) DOWNLOAD MP3 QURAN FILES IN A WEBPAGE
    2) MODIFY NAME AND METADATA
    3) UPLOAD
    PLEASE SPECIFIE WITH A NUMBER: 
    """)
    if selected == "1":
        url = input(f"Type your url: {bcolors.WARNING}{bcolors.BOLD}(Enter b to back) {bcolors.ENDC}")
        if url == "b":
            display_menu()
        else:
            download_all_mp3_files(url)

    elif selected == "2":
        modify_metatag()
    elif selected == "3":
        filename = input(f"ENTER FILE NAME: {bcolors.WARNING}{bcolors.BOLD}(Enter b to back) {bcolors.ENDC}")
        if filename == "b":
            display_menu()
        else:
            upload(filename, config.SERVER, config.USERNAME, config.PASSWORD)
    else:
        clear()
        print(f"{bcolors.FAIL}{bcolors.BOLD}PLEASE CHOOSE AGAIN!{bcolors.ENDC}")
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
    move_to_subfolder(QARI)
    return True


def move_to_subfolder(folder_name):
    # Make a directory
    os.mkdir(folder_name)
    # Move all mp3 files to subfolder
    current_path = os.getcwd()
    files = os.listdir(current_path)
    regex = r"(.mp3)"
    for file in files:
        if (re.search(regex, file)):
            file = os.path.join(current_path, file)
            shutil.move(file, current_path + "/" + folder_name)
    print("mp3 files moved into sub folder!")
    # Zip subfolder
    shutil.make_archive(folder_name, 'zip', folder_name,folder_name) # TODO: check that folder itself is in zip file
    # Remove subfolder
    shutil.rmtree(folder_name)

def upload(filename, server, username, password):
    total_size = os.path.getsize(filename)
    upload_tracker = FtpUploadTracker(int(total_size))
    """ Upload .zip file to dl.qurandl.com and returns True or False """
    ftp = FTP(host=server, user=username, passwd=password)
    try:
        ftp.login(user=username, passwd=password)
    except:
        pass
    ftp.cwd("public_html")
    # print(ftp.retrlines("LIST"))
    # Upload file
    with open(filename, 'rb') as file:
        ftp.storbinary("STOR " + filename, file,1024,upload_tracker.handle)
        # TODO: Extract zip file
        # TODO: Move zip file into extracted folder
    file.close()
    ftp.quit()
    # TODO: move local zip file into parent folder
    return True

def clear():
    os.system('clear')


if __name__ == "__main__":
    clear()
    display_menu()
