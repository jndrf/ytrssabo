#!/usr/bin/env python3
'''
This is free software. You may use, modify and distribute it under the
GNU General Public License, version 3 or, at your choice, any later version.

A copy of the license should be included in this distribution. If not, you can
view it at https://www.gnu.org/licenses/gpl-3.0.html.
'''

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


def download_channel(name, feed_url, base_folder='./', archive_folder='./', download_options={}):
    '''download all videos from a channel feed to the folder name

    returns the number of downloaded videos
    '''
    urls = get_video_urls(feed_url)

    try:
        # directory will be created later if it doesn't exist
        nfiles = len(os.listdir(f'./{name}'))
    except FileNotFoundError:
        nfiles = 0

    channel_folder = os.path.normpath('/'.join([base_folder, name]))
    channel_folder = os.path.expanduser(channel_folder)

    download_options['paths'] = {'home': channel_folder}
    download_options['download_archive'] = os.path.normpath('/'.join([archive_folder, name]))
    ydl = yt_dlp.YoutubeDL(params=download_options)
    retcode = ydl.download(urls[:1])
    if retcode != 0:
        raise RuntimeError(f'Download attempt resulted in error {retcode}')

    nfiles_new = len(os.listdir(channel_folder))

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

    # ensure that archive folder exists
    xdg_data_home = os.getenv('XDG_DATA_HOME', default='~/.local/share/')
    try:
        archive_dir = os.path.join(xdg_data_home, 'ytrssabo', 'archives')
        archive_dir = os.path.expanduser(archive_dir)
        os.makedirs(archive_dir)
        print('created archive folder at ', archive_dir)
    except FileExistsError:
        pass

    # read download options
    if config.has_section('DownloaderOptions'):
        # yt-dlp expects a dict for the path option,
        # configparser supports only strings as option values
        downloader_options = dict(config['DownloaderOptions'])
    else:
        downloader_options = {}

    notify2.init('ytrssabo.py')

    for name, feed_url in config['Channels'].items():
        base_dir = config.get('General', 'output_folder', fallback='~/Videos/ytrssabo/')
        nvid = download_channel(name, feed_url, base_dir, archive_dir, downloader_options)
        if nvid > 0:
            n = notify2.Notification(f'Downloaded {nvid} videos of channel {name}.')
            n.show()
