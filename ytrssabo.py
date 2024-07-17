#!/usr/bin/env python3

import argparse
import configparser

import requests

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

if __name__ == '__main__':

    print(get_video_urls('https://www.youtube.com/feeds/videos.xml?channel_id=UCtM5z2gkrGRuWd0JQMx76qA'))
