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

def remove_zero(number):
    """ Remove zero from beggining of the number string """
    if number[0] == "0":
        number = number[1:]
    if number[0] == "0":
        number = number[1:]
    return number

def extract_number(raw_string):
    """ Extract numbers from a raw string """
    raw_string = raw_string.replace(".mp3", "")
    raw_string = filter(lambda num:num, raw_string)
    my_lest = list(raw_string)
    numbers = ""
    for char in my_lest:
        if char.isnumeric():
            numbers += char
    numbers = remove_zero(numbers)
    return numbers


def generate_short_code(zip_file_name, folder_name):
    """
        ** Call it before zipping folder **
        Generate short code for wordpress to display proper content;
        Save file as short_code.txt
        Return Boolean as a result
    """
    codes = ""
    codes += f'[download link="{config.SITE_URL}{folder_name}/{zip_file_name}"]\n'
    codes += '[table_start]\n'
    # for each mp3 file in folder create new [quran] shortcode
    current_path = os.getcwd()
    quran_files = os.listdir(current_path)
    regex = r"(.mp3)"
    for file in quran_files:
        if re.search(regex, file):
            file_name = os.path.join(current_path, file)
            number = extract_number(file_name)
            codes += f'[quran src="{folder_name}/{file}" number="{number}"]\n'
    codes += '[table_end]\n'
    try:
        file = open('short_code.txt','w')
        file.write(codes)
        file.close()
    except Exception as error:
        raise("There is some error in writing chortcode in file...")


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
    REMOVE PREVIOUS METADATA AND EMBED NEW ONE
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
            mp3_file = the_mp3.load(path)
            mp3_file.delete()
            mp3_file.tag.artist(QARI_NAME)
            mp3_file.tag.album("Qurandl")
            mp3_file.tag.title(title.FILE_TITLES[i])
            mp3_file.tag.track_num = i
            mp3_file.tag.images.set(3, open('cover.jpg', 'rb').read(), 'image/jpeg')
            mp3_file.tag.save()
        except:
            continue
    generate_short_code(QARI + ".zip",QARI)
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
    # TODO: Extract zip file (on server side)
    # TODO: Move zip file into extracted folder (on server side)
    file.close()
    ftp.close()
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
