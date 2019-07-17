import pandas as pd
from sklearn.naive_bayes import GaussianNB
import numpy as np
import requests

comments = pd.read_csv('comments.csv')
comments = comments.loc[:1000]
print("The file was read")
X = comments[['len', 'likes', 'replies']]
Y = comments['ver']
columns = ['len', 'likes', 'replies', 'ver']

model = GaussianNB()
model.fit(X, Y)
comments = 0
# test
video_id = "AUF_LFWjbTY"
cols = ['id', 'text', 'likes', 'replies']
comments = pd.DataFrame(columns=cols)
url = "https://www.googleapis.com/youtube/v3/commentThreads?key=AIzaSyBr_BgEe0seUVLdY3EHMwCEE2H_c9BSWpU&textFormat=plainText&part=snippet&videoId=" + video_id + "&maxResults=50"
headers = {'Accept': 'application/json'}
r = requests.get(url, headers=headers)
d = r.json()
if 'items' in d:
    print(1)
    ndata = pd.DataFrame.from_dict(d['items'], orient='columns')
    thislist = []
    for i in range(len(ndata)):
        comment = ndata['snippet'][i]['topLevelComment']['snippet']
        comments.loc[len(comments)] = [ndata['snippet'][i]['topLevelComment']['id'], comment['textDisplay'],
                                       comment['likeCount'], ndata['snippet'][i]['totalReplyCount']]
    if 'nextPageToken' in d:
        nt = d['nextPageToken']
        while nt:
            url = "https://www.googleapis.com/youtube/v3/commentThreads?key=AIzaSyBr_BgEe0seUVLdY3EHMwCEE2H_c9BSWpU&textFormat=plainText&part=snippet&videoId=" + video_id + "&maxResults=50" + '&pageToken=' + nt
            headers = {'Accept': 'application/json'}
            r = requests.get(url, headers=headers)
            d = r.json()
            if 'items' in d:
                d['items']
                ndata = pd.DataFrame.from_dict(d['items'], orient='columns')
                thislist = []
                for i in range(len(ndata)):
                    comment = ndata['snippet'][i]['topLevelComment']['snippet']
                    comments.loc[len(comments)] = [ndata['snippet'][i]['topLevelComment']['id'],
                                                   comment['textDisplay'], comment['likeCount'],
                                                   ndata['snippet'][i]['totalReplyCount']]
                if d['pageInfo']['totalResults'] == 50:
                    if 'nextPageToken' in d:
                        nt = d['nextPageToken']
                    else:
                        break
                else:
                    break
        keywords = pd.read_csv('./verification-keywords')
        kw = keywords.columns
        comments['s_text'] = comments['text'].apply(lambda x: x.split(' '))
        lm = comments['likes'].max()
        rm = comments['replies'].max()
        if lm != 0:
            comments['likes'] = comments['likes'] / lm
        if rm != 0:
            comments['replies'] = comments['replies'] / rm
        comments['sum'] = comments['likes'] + comments['replies']
        comments = comments.sort_values('sum', ascending=False)
        comments = comments.reset_index(drop=True)
        ver_kw = pd.read_csv('./verification-keywords')
        ver_kw = ver_kw.columns
        comments['ver'] = 0
        for com in range(len(comments)):
            ver = 0
            for word in comments.loc[com, 's_text']:
                if word in ver_kw:
                    ver = 1
            comments.loc[com, 'ver'] = ver
        comments.sort_values('ver', ascending=False)
        comments['len'] = comments['text'].apply(len)
            # The file which contains the data of the comments(panda):
            # if file does not exist write header

X_test = comments[['len', 'likes', 'replies']]
Y_test = comments['ver']

print(model.predict(X_test))
print(model.predict_proba(X_test))
pred = model.predict_proba(X_test)
pred = pd.DataFrame(pred)
comments['result'] = pred

