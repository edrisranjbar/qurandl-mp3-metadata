import os
import re
import shutil
from ftplib import FTP
import platform

import eyed3 as the_mp3
import wget
from mutagen.mp3 import MP3
from selenium import webdriver

import config
import title


class Colors:
    """ IN ORDER TO USE COLORS OR SOME STYLING OPTIONS WE SHOULD USE THESE CONTANTS EASILY! """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class FtpUploadTracker:
    """ HERE WE'RE LOGGING UPLOAD STATUS """
    size_written = 0
    total_size = 0
    last_shown_percent = 0

    def __init__(self, total_size):
        """ INITIALIZING TOTAL SIZE OF FILE TO UPLOAD """
        self.total_size = total_size

    def handle(self, block):
        """ HANDLE FTP UPLOAD PROGRESS """
        self.size_written += 1024
        percent_complete = round((self.size_written / self.total_size) * 100, 1)

        if self.last_shown_percent != percent_complete:
            self.last_shown_percent = percent_complete
            clear()
            print(f"{Colors.OKGREEN}{str(percent_complete)} percent uploaded{Colors.ENDC}")


def generate_short_code(zip_file_name,folder_name):
    """
        ** Call it before zipping folder **
        Generate short code for wordpress to display proper content;
        Save file as short_code.txt
        Return Boolean as a result
    """
    codes = ""
    codes += f'[download link="{config.SITE_URL}{folder_name}/{zip_file_name}"]'
    codes += '[table_start]'
    # for each mp3 file in folder create new [quran] shortcode
    current_path = os.getcwd()    
    quran_files = os.listdir(current_path + "/" + folder_name)
    regex = r"(.mp3)"
    for file in quran_files:
        if re.search(regex, file):
            file_name = os.path.join(current_path, file)
            i = null          
            codes += f'[quran src="{folder_name}/{file_name}" number="{i}"]'
    codes += '[table_end]'
    pass

def display_menu():
    """
        DISPLAY A MENU OF WHAT USER CAN DO
    """
    print(f"{Colors.HEADER}{Colors.BOLD}************************************************{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}*****  Quran Download - Alsalamo Alaykom  ******{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}************************************************{Colors.ENDC}")
    selected = input(f"""{Colors.WARNING}WHICH ONE? (1-2) {Colors.ENDC}
    1) DOWNLOAD MP3 QURAN FILES IN A WEBPAGE
    2) MODIFY NAME AND METADATA
    3) UPLOAD
    PLEASE SPECIFIE WITH A NUMBER: 
    """)
    if selected == "1":
        url = input(f"Type your url: {Colors.WARNING}{Colors.BOLD}(Enter b to back) {Colors.ENDC}")
        if url == "b":
            display_menu()
        else:
            download_all_mp3_files(url)

    elif selected == "2":
        modify_metatag()
    elif selected == "3":
        filename = input(f"ENTER FILE NAME: {Colors.WARNING}{Colors.BOLD}(Enter b to back) {Colors.ENDC}")
        if filename == "b":
            display_menu()
        else:
            upload(filename, config.SERVER, config.USERNAME, config.PASSWORD)
    else:
        clear()
        print(f"{Colors.FAIL}{Colors.BOLD}PLEASE CHOOSE AGAIN!{Colors.ENDC}")
        display_menu()


def download_all_mp3_files(url):
    """
        DOWNLOAD ALL MP3 FILE IN A WEBPAGE
    """
    if platform.system() == "Windows":
        browser = webdriver.Chrome(executable_path='{}/chromedriver.exe'.format(os.curdir))
    elif platform.system() == "Linux":
        browser = webdriver.Chrome(executable_path='{}/chromedriver'.format(os.curdir))
    browser.get(url)
    links = browser.find_elements_by_link_text('دانلود کنید')
    for link in links:
        try:
            href = link.get_attribute("href")
            print("DOWNLOADING {}".format(href))
            file_name  = wget.filename_from_url(href)

            # download only if file does not exist
            if not os.path.exists(file_name):
                wget.download(href)
        except:
            print("Can't download {}".format(link))
        finally:
            browser.close()
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
    """ MOVE MP3 FILES TO A SUB FOLDER AND ZIP THEME ALL TOGETHER IN A DIRECTORY """
    # Make a directory
    current_path = os.getcwd()
    try:
        os.mkdir(folder_name)
        os.chdir(current_path + "/" + folder_name)
        os.mkdir(folder_name)
        os.chdir('..')
    except FileExistsError:
        print(f"{Colors.FAIL}Folder already exists!{Colors.ENDC}")
    # Move all mp3 files to subfolder
    files = os.listdir(current_path)
    regex = r"(.mp3)"
    for file in files:
        if re.search(regex, file):
            file = os.path.join(current_path, file)
            shutil.move(file, current_path + "/" + folder_name + "/" + folder_name)
    print(f"{Colors.OKGREEN}mp3 files moved into sub folder!{Colors.ENDC}")
    # Zip subfolder
    print("Zipping files...")
    shutil.make_archive(folder_name, 'zip',folder_name)
    print(f"{Colors.OKGREEN}Zipping process completed!{Colors.ENDC}")
    # Remove subfolder
    shutil.rmtree(folder_name)
    print(f"{Colors.OKGREEN}Folder removed!{Colors.ENDC}")

def upload(filename, server, username, password):
    """ Upload .zip file to dl.qurandl.com and returns True or False """
    total_size = os.path.getsize(filename)
    upload_tracker = FtpUploadTracker(int(total_size))
    ftp = FTP(host=server, user=username, passwd=password)
    try:
        ftp.login(user=username, passwd=password)
    except:
        pass
    ftp.cwd("public_html")
    # print(ftp.retrlines("LIST"))
    # Upload file
    with open(filename, 'rb') as file:
        ftp.storbinary("STOR " + filename, file, 1024, upload_tracker.handle)
        # TODO: Extract zip file
        # TODO: Move zip file into extracted folder
    file.close()
    ftp.quit()
    # Move file locally to parent directory
    shutil.move(file, "..")
    return True

def clear():
    """ CLEAR THE TERMINAL SCREEN """
    if platform.system() == "Windows":
        os.system('cls')
    elif platform.system() == "Linux":
        os.system('clear')


if __name__ == "__main__":
    while True:
        display_menu()
