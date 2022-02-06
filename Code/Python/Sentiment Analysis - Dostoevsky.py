#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import sys
import pandas as pd
import numpy as np

from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel


# In[2]:


Start_Message_Id=int(sys.argv[1:][0])
print(Start_Message_Id)
End_Message_Id=int(sys.argv[1:][1])
print(End_Message_Id)
Part=int(sys.argv[1:][2])
print(Part)


# In[3]:


Data='/home/kate/Projects/eva/Data'
Messages_filename='Messages.csv'
Messages_full_filename=os.path.join(Data, Messages_filename)

sa_filename='SentimentAnalysis/Dostoevsky/sa_dostoevsky_%s.csv'%Part
sa_full_filename=os.path.join(Data, sa_filename)


# In[4]:


Messages = pd.read_csv(Messages_full_filename, error_bad_lines=False, index_col=False, usecols=['Message_Id','message'])


# In[5]:


SubsetToAnalyze=Messages[Start_Message_Id:End_Message_Id+1:1].copy(deep=True)


# In[6]:


SubsetToAnalyze['dostoevsky']=''


# In[7]:


del Messages


# In[8]:


tokenizer = RegexTokenizer()
model = FastTextSocialNetworkModel(tokenizer=tokenizer)


# In[9]:


SubsetToAnalyze['message']=SubsetToAnalyze['message'].fillna(' ')


# In[10]:


results = model.predict(SubsetToAnalyze['message'].tolist(), k=2)
sentiment_list = list()
for sentiment in results:
    sentiment_list.append(list(sentiment.keys())[0] )


# In[11]:


SubsetToAnalyze['dostoevsky']=sentiment_list


# In[12]:


SubsetToAnalyze.to_csv(sa_full_filename, header=True, index=False)

