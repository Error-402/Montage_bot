from __future__ import unicode_literals
from googleapiclient.discovery import build
import youtube_dl
import argparse
from moviepy.editor import *
import os
import string
import random
import shutil


def main(options):
    montage_name = generate_name()
    path = os.path.expanduser("~/Desktop/montageBot/" + montage_name + '/')
    videos_id = create_videos_id_list(options)

    create_directory(path)
    download_videos(path, videos_id)
    create_montage(path, videos_id, montage_name)


def create_montage(path: str, videos_id: list, montage_name: str) -> None:
    clips = create_clips_list(path, videos_id)
    song = clips.pop(0)

    final_clip = concatenate_videoclips(
        clips, method='compose').set_audio(song)
    final_clip = vfx.fadeout(final_clip, duration=2)

    final_clip.write_videofile(
        path + montage_name + '.mp4', codec="libx264")


def create_videos_id_list(options: argparse.Namespace) -> list:
    videos_id = []

    get_videos_id(options.song, videos_id, is_song=True)
    if options.playlist is not None:
        try:
            get_playlist_videos_id(options.playlist, videos_id)
        except:
            print('Sorry, there was an error trying get the playlist')
            exit()
    else:
        get_videos_id(options.topic, videos_id, is_song=False)

    return videos_id


def create_clips_list(path: str, videos_id: list) -> list:
    clips = []
    for count, id in enumerate(videos_id):
        if count == 0:
            clips.append(AudioFileClip(
                path + id + '.m4a').subclip(0, 30))  # accepts secconds
        else:
            clips.append(VideoFileClip(
                path + id + '.mp4').subclip(0, 6).crossfadein(2))
    return clips


def generate_name(size=6, chars=string.ascii_uppercase + string.digits) -> str:
    return 'Montage' + ''.join(random.choice(chars) for _ in range(size))


def create_directory(path: str,) -> None:
    if os.path.isdir(path):
        return
    os.makedirs(path)


def download_videos(path: str, videos_id: list) -> None:
    song_opts = {
        'outtmpl': path + '%(id)s.%(ext)s',
        'format': 'm4a',
    }
    video_opts = {
        'outtmpl': path + '%(id)s.%(ext)s',
        'format': 'mp4',
    }
    for count, id in enumerate(videos_id):
        with youtube_dl.YoutubeDL(song_opts if count == 0 else video_opts) as ydl:
            try:
                ydl.download(['https://www.youtube.com/watch?v=' + id])
            except:
                shutil.rmtree(path)
                print('Sorry, there was an error trying to download a video')
                exit()


def get_videos_id(subject: str, videos_id: list,  is_song: bool) -> None:
    search_response = youtube.search().list(
        q=subject,
        part="id, snippet",
        maxResults=1 if is_song else 10
    ).execute()

    for item in (search_response['items']):
        if item['id']['kind'] != 'youtube#video':
            continue
        videos_id.append(item['id']['videoId'])
        if len(videos_id) == 6:
            break
    return


def get_playlist_videos_id(uploads_list_id: str, videos_id: list) -> None:
    playlistitems_list_request = youtube.playlistItems().list(
        playlistId=uploads_list_id,
        part="snippet",
        maxResults=5
    )

    while playlistitems_list_request:
        playlistitems_list_response = playlistitems_list_request.execute()

        for playlist_item in playlistitems_list_response["items"]:
            videos_id.append(playlist_item["snippet"]["resourceId"]["videoId"])

        playlistitems_list_request = youtube.playlistItems().list_next(
            playlistitems_list_request, playlistitems_list_response)
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Make a automatic montage')
    parser.add_argument(
        '--song', type=str, help='The song you want in the montage', default='Jorge Ben - Chove Chuva (Áudio Oficial)')
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--topic', type=str, help='The topic you want in the montage')
    group.add_argument('--playlist', type=str,
                       help='Playlist of 5 videos that will be used on the montage')

    args = parser.parse_args()
    youtubeApiKey = "API-KEY"
    youtube = build('youtube', 'v3', developerKey=youtubeApiKey)
    main(args)
