#!/usr/bin/env python3

import argparse
import configparser

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
    '''download all videos from a channel feed to the folder name'''
    urls = get_video_urls(feed_url)

    ydl = yt_dlp.YoutubeDL(params={'paths': {'home': f'./{name}'}})
    ydl.download(urls)


if __name__ == '__main__':

    parser = argparse.ArgumentParser('Tool to automatically download new videos of select Youtube channels')
    parser.add_argument('config', help='Configuration file')

    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config)

    for name, feed_url in config['Channels'].items():
        download_channel(name, feed_url)
