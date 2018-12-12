"""
Add Cover Art:
This application will find the .mp3 files in your computer.
Then it will automatically scrape a suitable cover from google images and apply
it as a cover art to the mp3 file.
"""

import re
import os
import argparse
from urllib.error import HTTPError,URLError
import tkinter as tk

from scrape_image_from_google_images import scrape_google_image
from PIL import ImageTk, Image
import eyed3

    

def tkinter_window(location, audiofile):
    inputs={}
    def get_entry():
        inputs['song_query']=song_query.get()
        window.destroy()
    window = tk.Tk()
    window.title("Add cover art")
    window.geometry("300x250")
    name = tk.Label(window, text='Do you want this images as cover art')
    path = location
    img = ImageTk.PhotoImage(Image.open(path).resize((150, 150), Image.ANTIALIAS))
    panel = tk.Label(window, image=img)
    song_query_question = tk.Label(window, text='Enter text to search')
    song_query = tk.Entry(window)
    OK = tk.Button(window, text="Okay", command=add_image(location, audiofile))

    Cancel = tk.Button(window, text="Cancel", command=window.destroy)
    Search = tk.Button(window, text="Search", command=get_entry)

    name.grid(column=0, row=0, columnspan=6)
    panel.grid(column=0, row=1, columnspan=3, rowspan=3)
    OK.grid(column=0, row=4, columnspan=2)
    Search.grid(column=2, row=4)
    song_query_question.grid(column=3, row=1, columnspan=3)
    song_query.grid(column=3, row=2, columnspan=3)
    Cancel.grid(column=4, row=4, columnspan=2)

    window.mainloop()


    return inputs


def add_image(location, audiofile):
    if (audiofile.tag is None):
        audiofile.initTag()
    print(audiofile.tag.album_artist)
    audiofile.tag.images.set(3, open(location, 'rb').read(), 'image/jpeg')
    audiofile.tag.save()


def extract_query(file_path):
    song_name=os.path.split(file_path)[-1]                          # Get songs name from file path
    song_name=song_name.lstrip("0123456789.- ")                     # Strip track no and numbers from the song names using lstrip
    song_name="".join(song_name.split('.')[:-1])                    # Remove extension from song names
    song_name=song_name.replace("-", " ").replace("_", " ")
    song_name=re.sub(r"\d\d\d\s*kbps", " ", song_name, flags=re.I)
    song_name=re.sub(r"[\(\[].*?[\)\]]", "", song_name)             # Replace '-','_','320','Kbps','kbps' sign with ' '
    song_name=re.sub(" +", " ", song_name)                         # Remove anything in between (),[],{} and replace multiple spaces
    return song_name


if __name__ == '__main__':


    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?', default=os.getcwd())
    parser.add_argument('--no-gui', action='store_true',help='dont use a gui, automatically add cover art')
    args=parser.parse_args()

    song_paths = []
    if os.path.isdir(args.file):
        print("Finding all .mp3 files in:", args.file)
        for root, dirs, files in os.walk(args.file):
            for file in files:
                if file.endswith('.mp3'):
                    song_paths.append(os.path.join(root, file))
    elif os.path.isfile(args.file) and args.file.endswith('.mp3'):
        print("Finding:", args.file)
        song_paths.append(os.path.abspath(args.file))

    for song_path in song_paths:
        audiofile = eyed3.load(song_path)
        song_query = extract_query(song_path)
        try:
            song_directory = scrape_google_image(song_query+" song cover art", name=song_query,max_num=1)
        except (HTTPError,URLError):
            print ('Unable to Download the images')
            continue
        song_filename = os.path.join(song_directory, os.listdir(song_directory)[0])
        Image.open(song_filename)
        if args.no_gui:
            add_image(song_filename,audiofile)
        else:
            while True:
                inputs=tkinter_window(song_filename, audiofile)
                if inputs:
                    try:
                        song_directory = scrape_google_image(inputs['song_query'] + " song cover art", name=inputs['song_query'] ,
                                                        max_num=1)
                    except (HTTPError,URLError):
                        print ('Unable to Download the images')
                        continue
                    song_filename = os.path.join(song_directory, os.listdir(song_directory)[0])
                else:
                    break
                    
