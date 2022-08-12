#!/usr/bin/env python3

import sys
import time
import os

from os import listdir
from os.path import isfile, join

from pytube import YouTube
import eyed3


def getVideoUrls():
    videos = []

    f = open("data/youtubeURL_LL_2.txt", "r")
    for x in f:
        videos.append(x.strip('\n'))

    if videos:
        print("Found", len(videos), "videos in playlist.")
        return videos
    else:
        print('No videos found.')
        exit(1)


# function added to get audio files along with the video files from the playlist
def download_Video(path, vid_url):
    try:
        yt = YouTube(vid_url)
    except Exception as e:
        print("Error:", str(e), "- Skipping Video '" + vid_url + "'.")
        return

    try:
        video = yt.streams.filter(adaptive=True, only_audio=True).first()
    except Exception as e:
        print("Error:", str(e), "- Skipping Video with title '" + yt.title + "'.")
        return

    try:
        video.download(path)
        print("Successfully downloaded", yt.title)
    except OSError:
        print(yt.title, "already exists in this directory! Skipping video...")


def transform_Audio(path):
    files = [os.path.splitext(f)[0] for f in listdir(path) if isfile(join(path, f)) and f.lower().endswith('.mp4')]
    for i, f in enumerate(files):
        print("Transforming to audio ", f)
        try:
            vid = path + '/' + f + '.mp4'
            id_vid = path + '/' + str(i) + '.mp4'
            aud = path + '/' + f + '.mp3'

            os.rename(vid, id_vid)
            os.system('ffmpeg -loglevel quiet -i "' + id_vid + '" "' + aud + '"')
            os.remove(id_vid)

            name = f.replace('–', '-')
            is_remix = "remix" in name.casefold() or "mashup" in name.casefold() or "bootleg" in name.casefold()
            has_several_hyphen = name.count('-') > 1
            has_no_hyphen = name.count('-') == 0

            split_name = name.split(' - ')
            artist = ""
            title = ""

            if has_no_hyphen:
                artist = "ID"
                title = name
            elif has_several_hyphen:
                artist = split_name[0]
                for x in split_name[1:]: title += x + " "
            else:
                artist = split_name[0]
                title = split_name[1]

            audiofile = eyed3.load(aud)
            audiofile.tag.artist = artist
            audiofile.tag.title = title
            audiofile.tag.genre = "Other" if is_remix else "Dance"
            audiofile.tag.save()
        except Exception as e:
            print("\tError with the transformation of", f)
            print(e)


def update_MP3(path):
    files = [os.path.splitext(f)[0] for f in listdir(path) if isfile(join(path, f)) and f.lower().endswith('.mp4')]
    for f in files:
        print("Transforming to audio ", f)
        try:
            aud = path + '/' + f + '.mp3'
            name = f.replace('–', '-')
            is_remix = "remix" in name.casefold() or "mashup" in name.casefold() or "bootleg" in name.casefold()
            has_several_hyphen = name.count('-') > 1
            has_no_hyphen = name.count('-') == 0

            split_name = name.split(' - ')
            artist = ""
            title = ""

            if has_no_hyphen:
                artist = "ID"
                title = name
            elif has_several_hyphen:
                artist = split_name[0]
                for x in split_name[1:]: title += x + " "
            else:
                artist = split_name[0]
                title = split_name[1]

            audiofile = eyed3.load(aud)
            audiofile.tag.artist = artist
            audiofile.tag.title = title
            audiofile.tag.genre = "Other" if is_remix else "Dance"
            audiofile.tag.save()
        except Exception as e:
            print("\tError with the transformation of", f)
            print(e)


if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print('USAGE: python yt.py destPath --tags-only --audio-only')
        exit(1)
    else:
        tags_only = sys.argv.count('--tags-only') > 0
        audio_only = sys.argv.count('--audio-only') > 0
        directory = sys.argv[1]

        if tags_only:
            update_MP3(directory)
        elif audio_only:
            transform_Audio(directory)
        else:
            # make directory if dir specified doesn't exist
            try:
                os.makedirs(directory, exist_ok=True)
            except OSError as e:
                print(e.reason)
                exit(1)

            vid_urls = getVideoUrls()

            for vid_name_url in vid_urls:
                download_Video(directory, vid_name_url)
                time.sleep(1)

            transform_Audio(directory)

# Last video was DayNight - Turn The Beat (BROHOUSE)
# https://www.youtube.com/watch?v=HAQ6xaY7E4g

# (\/watch\?v=.*&amp;list=LL&amp;index=\d+).*title="(.*)" --> select videos and titles
