from googleapiclient.discovery import build
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.parse import urlparse
import sys, os

import json

############## ADD YOUTUBE API KEY ###########
DEVELOPER_KEY = 'YOUTUBE API KEY'

##### Video Object ############
######### The metadata that are available by YouTube API
######### https://developers.google.com/youtube/v3/docs/videos

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE_METADATA_URL = 'https://www.googleapis.com/youtube/v3/videos'

YOUTUBE_COMMENT_URL = 'https://www.googleapis.com/youtube/v3/commentThreads'



def openURL(url, parms):
    # print(url)
    # print(urlencode(parms))
    f = urlopen(url + '?' + urlencode(parms))
    data = f.read()
    f.close()
    matches = data.decode("utf-8")
    return matches


def get_video_id(url):
    """
    Examples:
    - http://youtu.be/SA2iWivDJiE
    - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    - http://www.youtube.com/embed/SA2iWivDJiE
    - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    """
    o = urlparse(url)
    if o.netloc == 'youtu.be':
        return o.path[1:]
    elif o.netloc in ('www.youtube.com', 'youtube.com'):
        if o.path == '/watch':
            id_index = o.query.index('v=')
            return o.query[id_index + 2:id_index + 13]
        elif o.path[:7] == '/embed/':
            return o.path.split('/')[2]
        elif o.path[:3] == '/v/':
            return o.path.split('/')[2]
    return None  # fail?


def get_channel_data(channel_id):
    print('Begin')
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
    max_results = 50

    parms = {
        'part': 'brandingSettings,contentDetails,contentOwnerDetails,id,invideoPromotion,localizations,snippet,statistics,status,topicDetails',
        'channelId': "UCHTK-2W11Vh1V4uwofOfR4w",
        'maxResults': max_results,
        'key': DEVELOPER_KEY
    }
    results = youtube.channels().list(
        part="statistics",
        id=channel_id,
    ).execute()
    return results


def get_video_metadata(video_id):
    print('get metadata')

    parms = {
        'part': 'snippet,statistics,status,topicDetails,contentDetails,recordingDetails',
        'id': video_id,
        'key': DEVELOPER_KEY
    }

    matches = openURL(YOUTUBE_METADATA_URL, parms)

    search_response = json.loads(matches)
    # print(search_response)
    # print(self.video_id)

    videos = []
    for search_result in search_response.get("items", []):

        if 'snippet' in search_result:
            print('video publishedAt {}'.format(search_result['snippet']['publishedAt']))
            print('Channel id .{}'.format(search_result['snippet']['channelId']))

        if 'thumbnails' in search_result['snippet']:

            if 'default' in search_result['snippet']['thumbnails']:
                print('Default thumbnail {}'.format(search_result['snippet']['thumbnails']['default']['url']))

        if 'statistics' in search_result:
            print('View count {}'.format(search_result['statistics']['viewCount']))


def load_comments(mat):
            try:
                counter = 0
                ver_counter = 0
                for item in mat["items"]:
                    comment_id = item["id"]
                    comment = item["snippet"]["topLevelComment"]
                    date = comment["snippet"]["publishedAt"]
                    text = comment["snippet"]["textDisplay"]
                    print("Comment by {} {}: {}: {}".format(comment_id, text, date))
                    counter = counter + 1

            except KeyboardInterrupt:
                print("User Aborted the Operation")

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                print("Cannot Open URL or Fetch comments at a moment " + str(e))

            return counter, ver_counter


def get_comments(video_id):
    parms = {
        'part': 'snippet,replies',
        'maxResults': 50,
        'videoId': video_id,
        'textFormat': 'plainText',
        'key': DEVELOPER_KEY
    }

    try:
        matches = openURL(YOUTUBE_COMMENT_URL, parms)

        mat = json.loads(matches)
        nextPageToken = mat.get("nextPageToken")

        load_comments(mat)
        while nextPageToken:
            parms.update({'pageToken': nextPageToken})
            matches = openURL(YOUTUBE_COMMENT_URL, parms)
            mat = json.loads(matches)
            nextPageToken = mat.get("nextPageToken")

            load_comments(mat)

        print(' END 1')
        return 'done'
    except KeyboardInterrupt:
        print("User Aborted the Operation")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print("Cannot Open URL or Fetch comments at a moment " + str(e))

if __name__ == '__main__':
    video_url = ''
    video_id = get_video_id(video_url)
    get_video_metadata(video_id)
