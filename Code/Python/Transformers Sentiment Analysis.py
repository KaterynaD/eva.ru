#!/usr/bin/env python
# coding: utf-8

# In[2]:


import sys
import os
import datetime
import pandas as pd
import numpy as np


# In[3]:


import tensorflow as tf


# In[4]:


from transformers import pipeline




# In[ ]:


Model=sys.argv[1:][0]
column_name=sys.argv[1:][1]
Start_Message_Id=int(sys.argv[1:][2])
End_Message_Id=int(sys.argv[1:][3])
Part=int(sys.argv[1:][4])


# In[ ]:


print('Starting Sentiment Analysis using model %s'%Model)
print('The result will be saved in %s column'%column_name)
print('Starting from message number: %s'%Start_Message_Id)
print('Ending with message number: %s'%End_Message_Id)
print('Result will be saved in %s part'%Part)


# In[10]:


Data='/home/kate/Projects/eva/Data'
Messages_filename='Messages.csv'
Messages_full_filename=os.path.join(Data, Messages_filename)

sa_filename='SentimentAnalysis/%s/sa_%s_%s.csv'%(column_name, column_name, Part)
sa_full_filename=os.path.join(Data, sa_filename)


# In[11]:


Messages = pd.read_csv(Messages_full_filename,  index_col=False, usecols=['Message_Id','message'])


# In[ ]:


SubsetToAnalyze=Messages[Start_Message_Id:End_Message_Id+1:1].copy(deep=True)


# In[ ]:


del Messages


# In[12]:


SubsetToAnalyze['message']=SubsetToAnalyze['message'].fillna(' ')


# In[13]:


SubsetToAnalyze[column_name]=''


# In[ ]:


sentiment_analysis = pipeline('sentiment-analysis',model=Model)


# In[ ]:


print(datetime.datetime.now())
for index, row in SubsetToAnalyze.iterrows():
  #print(row['message'])
    if not(row['message'] != row['message']):
        try:
            sentiment = sentiment_analysis(row['message'])[0]['label']
        except:
            try:
                sentiment = sentiment_analysis(row['message'][0:1000])[0]['label']
            except:
                sentiment = 'N/A'
    else:
        sentiment = 'N/A'
    #print(sentiment)
    SubsetToAnalyze.at[index,column_name]=sentiment
    print('.', end = ' '),
print(datetime.datetime.now())    
SubsetToAnalyze.to_csv(sa_full_filename, header=True, index=False, columns=['Message_Id',column_name])    
print()
print('Processing  complete')

