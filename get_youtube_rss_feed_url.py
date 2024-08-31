#!/usr/bin/env python3

import argparse
import requests

import re


def main(channel):
    '''Return the URL to the RSS feed of a Youtube Channel

    :param channel: URL of the channel page
    '''
    channel_page = requests.get(channel)

    if channel_page.status_code != 200:
        raise RuntimeError(f'Requesting {channel} failed, status code {channel_page.status_code}')

    # The RSS url is contained in some long blob of JSON, which is part of some
    # script inside the HTML of the page. E.g
    # "rssUrl":"https://www.youtube.com/feeds/videos.xml?channel_id=UCtM5z2gkrGRuWd0JQMx76qA"
    pattern = re.compile('"rssUrl":"[^"]*"')
    pair = pattern.findall(channel_page.text)
    pair = pair[0]              # 
    rssURL = pair.split('":"')[1].strip('"')

    return rssURL


if __name__ == '__main__':

    parser = argparse.ArgumentParser('Find link to RSS feed for a Youtube Channel')
    parser.add_argument('channel', help='Link to the channel page')

    args = parser.parse_args()

    rssURL = main(args.channel)
    print(rssURL)
