import pandas as pd
import requests
from sklearn.svm import SVC
import pickle

def deEmojify(inputString):
    return inputString.encode('utf-8', 'ignore').decode('utf-8')


def preprocessing():
    yt_df_meta = pd.read_json("./yt_meta.json")
    for index,row in yt_df_meta.iterrows():
        print(row["_id"])
        if row["_id"] != "CE0Q904gtMI" and row["_id"] != "AUF_LFWjbTY" and row["_id"] != "XkLhPditpy8" :
            video_id= row["_id"]
            cols=['id','text','likes','replies']
            comments=pd.DataFrame(columns=cols)
            url="https://www.googleapis.com/youtube/v3/commentThreads?key=AIzaSyBwVBaYAjsSyj19TLXmDuNoliSsKmA6oK0&textFormat=plainText&part=snippet&videoId="+video_id+"&maxResults=50"
            headers={'Accept':'application/json'}
            r=requests.get(url,headers=headers)
            d=r.json()
            if 'items' in d:
                ndata =pd.DataFrame.from_dict(d['items'],orient='columns')
                thislist=[]
                for i in range(len(ndata)):
                    comment=ndata['snippet'][i]['topLevelComment']['snippet']
                    comments.loc[len(comments)]=[ndata['snippet'][i]['topLevelComment']['id'],comment['textDisplay'],comment['likeCount'],ndata['snippet'][i]['totalReplyCount']]
                if 'nextPageToken' in d:
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
                print(comments['text'])
                comments['text'] = deEmojify(str(comments['text']))
                comments['s_text']=comments['text'].apply(lambda x :x.split(' '))
                lm=comments['likes'].max()
                rm=comments['replies'].max()
                if lm != 0:
                    comments['likes']=comments['likes']/lm
                if rm != 0:
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
                comments['len']=comments['text'].apply(len)
    # The file which contains the data of the comments(panda):
    comments.to_csv("comments.csv")

    X = comments[['len','likes','replies']]
    Y = comments['ver']
    columns = ['len','likes','replies','ver']

    # RBF kernel with gamma 1
    model = SVC(kernel='rbf', gamma=0.01, C=1.0)
    model.fit(X, Y)
    filename = 'finalized_model.sav'
    pickle.dump(model, open(filename, 'wb'))

if __name__ == "__main__":
    # load the metadata responses of the training and testing set (video title, desciption, channel created time etc.)
    preprocessing()

#loaded_model = pickle.load(open(filename, 'rb'))
#result = loaded_model.score(X_test, Y_test)
#print(result)