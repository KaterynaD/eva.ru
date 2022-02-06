#!/usr/bin/env python
# coding: utf-8

# In[1]:

import sys
from bs4 import BeautifulSoup
import urllib.request
import os
import pandas as pd
import numpy as np

import time


# In[2]:


Start_Message_Id=int(sys.argv[1:][0])
print(Start_Message_Id)
End_Message_Id=int(sys.argv[1:][1])
print(End_Message_Id)
Part=int(sys.argv[1:][2])
print(Part)


# In[3]:


Base_URL='https://eva.ru/forum/topic/message/%s.htm'
Data='/home/kate/Projects/eva/Data'
Messages_filename='Messages.csv'
Messages_full_filename=os.path.join(Data, Messages_filename)
Dates_filename='Dates/Timestamp_%s.csv'%Part
Dates_full_filename=os.path.join(Data, Dates_filename)
attempts=20
delay=60


# In[14]:


def GetMessageDate(Message_Id):
    html_page = urllib.request.urlopen(Base_URL%Message_Id)
    soup = BeautifulSoup(html_page, features='lxml')
    dates = soup.findAll('div', {'class': 'date'})
    for d in dates:
        return d.text.strip().rstrip('\n').lstrip('\n').replace('Дата: ','').replace('Время: ','')[0:14]
    else:
        return ''


# In[5]:


Messages = pd.read_csv(Messages_full_filename, error_bad_lines=False, index_col=False, usecols=['Message_Id'])


# In[6]:


SubsetToDownload=Messages[Start_Message_Id:End_Message_Id+1:1]


# In[15]:


dates_l=list()
for index, row in SubsetToDownload.iterrows():
    print('.', end = ' '),
    cnt=0
    while cnt<attempts:
        try:
            dates_l.append(GetMessageDate(row['Message_Id']))
            cnt=attempts
        except Exception as e:
            print('Something went wrong...'+ str(e))
            cnt=cnt+1 
            print('Waiting...')
            time.sleep(delay)
            print('Attempt to read message %s # %s'%(row['Message_Id'],cnt+1))
    if cnt>attempts:
        print('Too many false attempts. Stop execution...')
        break
print()
print('Processing  complete')         
dates_pd=pd.DataFrame({'Message_Id': SubsetToDownload['Message_Id'].tolist(),'Timestamp': dates_l})
dates_pd.to_csv(Dates_full_filename, header=True, index=False)
print(len(dates_pd))

