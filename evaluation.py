import pandas as pd
import requests
from sklearn.svm import SVC
import pickle


def preprocessing():
    test_videos = ["CE0Q904gtMI","AUF_LFWjbTY","XkLhPditpy8"]
    for video_id in test_videos:
        cols=['id','text','likes','replies']
        comments=pd.DataFrame(columns=cols)
        url="https://www.googleapis.com/youtube/v3/commentThreads?key=AIzaSyBwVBaYAjsSyj19TLXmDuNoliSsKmA6oK0&textFormat=plainText&part=snippet&videoId="+video_id+"&maxResults=50"
        headers={'Accept':'application/json'}
        r=requests.get(url,headers=headers)
        d=r.json()
        ndata =pd.DataFrame.from_dict(d['items'],orient='columns')
        thislist=[]
        for i in range(len(ndata)):
            comment=ndata['snippet'][i]['topLevelComment']['snippet']
            comments.loc[len(comments)]=[ndata['snippet'][i]['topLevelComment']['id'],comment['textDisplay'],comment['likeCount'],ndata['snippet'][i]['totalReplyCount']]
        if d['pageInfo']['totalResults']==50:
            nt=d['nextPageToken']
        while nt:
            url="https://www.googleapis.com/youtube/v3/commentThreads?key=AIzaSyBwVBaYAjsSyj19TLXmDuNoliSsKmA6oK0&textFormat=plainText&part=snippet&videoId="+video_id+"&maxResults=50"+'&pageToken='+nt
            headers={'Accept':'application/json'}
            r=requests.get(url,headers=headers)
            d=r.json()
            d['items']
            ndata =pd.DataFrame.from_dict(d['items'],orient='columns')
            thislist=[]
            for i in range(len(ndata)):
                comment=ndata['snippet'][i]['topLevelComment']['snippet']
                comments.loc[len(comments)]=[ndata['snippet'][i]['topLevelComment']['id'],comment['textDisplay'],comment['likeCount'],ndata['snippet'][i]['totalReplyCount']]
            if d['pageInfo']['totalResults']==50:
                nt=d['nextPageToken']
            else:
                break

        keywords=pd.read_csv('./verification-keywords')
        kw=keywords.columns
        comments['s_text']=comments['text'].apply(lambda x :x.split(' '))
        lm=comments['likes'].max()
        rm=comments['replies'].max()
        comments['likes']=comments['likes']/lm
        comments['replies']=comments['replies']/rm
        comments['sum']=comments['likes']+comments['replies']
        comments=comments.sort_values('sum',ascending=False)
        comments=comments.reset_index(drop=True)
        ver_kw = pd.read_csv('./verification-keywords')
        ver_kw=ver_kw.columns
        comments['ver']=0
        for com in range(len(comments)):
            ver=0
            for word in comments.loc[com,'s_text']:
                if word in ver_kw:
                    ver=1
            comments.loc[com,'ver']=ver
        comments.sort_values('ver',ascending=False)
        comments.loc[27,'text']
        comments['len']=comments['text'].apply(len)
    # The file which contains the data of the comments(panda):
    comments.to_csv("commentsTest.csv")

    X = comments[['len','likes','replies']]
    Y = comments['ver']
    columns = ['len','likes','replies','ver']
