import pandas as pd

dataset=pd.read_csv("D:\ProjectX-Emotion\dataset\data_moods.csv")

dataset['mood']=dataset['mood'].apply(lambda x:x.lower())

def get_song(emotion):
    
    df=dataset[dataset.mood==emotion].sample(n=1)
    
    res=df.iloc[0]['name']
    
    return str(res)

