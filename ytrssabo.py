#!/usr/bin/env python3

import argparse
import configparser
import os

import notify2
import requests
import yt_dlp

from bs4 import BeautifulSoup


def get_video_urls(feed_url):
    '''extracts the video URLS inside a youtube RSS feed'''
    video_urls = []

    feed = requests.get(feed_url)

    soup = BeautifulSoup(feed.text, features='xml')

    for entry in soup.find_all('entry'):
        vid = entry.link['href']
        video_urls.append(vid)

    return video_urls


def download_channel(name, feed_url):
    '''download all videos from a channel feed to the folder name

    returns the number of downloaded videos
    '''
    urls = get_video_urls(feed_url)

    try:
        # directory will be created later if it doesn't exist
        nfiles = len(os.listdir(f'./{name}'))
    except FileNotFoundError:
        nfiles = 0

    ydl = yt_dlp.YoutubeDL(params={
        'paths': {'home': f'./{name}'},
        'download_archive': f'./{name}/archive.txt'
    })
    retcode = ydl.download(urls[:1])
    if retcode != 0:
        raise RuntimeError(f'Download attempt resulted in error {retcode}')

    nfiles_new = len(os.listdir(f'./{name}'))

    return nfiles_new - nfiles


if __name__ == '__main__':

    parser = argparse.ArgumentParser('Tool to automatically download new videos of select Youtube channels')
    parser.add_argument('--config', help='Configuration file', default=None)
    
    args = parser.parse_args()

    if args.config is None:
        xdg_config_home = os.getenv('XDG_CONFIG_HOME', default='~/.config/')
        args.config = f'{xdg_config_home}/ytrssabo/ytrssabo.cfg'

    config = configparser.ConfigParser()
    config.optionxform = lambda option: option     # preserve case of channel names
    args.config = os.path.expandvars(args.config)  # path may contain env variables
    args.config = os.path.expanduser(args.config)  # or start with ~/
    if not os.path.exists(args.config):
        raise FileNotFoundError(f'cannot find configuration file {args.config}')
    config.read(args.config)

    notify2.init('ytrssabo.py')

    for name, feed_url in config['Channels'].items():
        nvid = download_channel(name, feed_url)
        if nvid > 0:
            n = notify2.Notification(f'Downloaded {nvid} videos of channel {name}.')
            n.show()
