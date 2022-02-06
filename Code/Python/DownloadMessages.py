#!/usr/bin/env python
# coding: utf-8

# In[1]:

import sys
from bs4 import BeautifulSoup
import urllib.request
import os
import pandas as pd
import numpy as np

from emoji import UNICODE_EMOJI
import re

import time


# In[2]:


Chapter_Id_To_Load=int(sys.argv[1:][0])
print(Chapter_Id_To_Load)

# In[3]:


def cnt_emoji(s):
    count = 0
    for emoji in UNICODE_EMOJI['en']:
        count += s.count(emoji)
    return count


# In[4]:


def remove_urls (vTEXT):
    vTEXT = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%|\-)*\b', '', vTEXT, flags=re.MULTILINE)
    return(vTEXT)


# In[9]:


Base_URL='https://eva.ru'
Data='/home/kate/Projects/eva/Data'
Chapters_filename='Chapters-%s.csv'%Chapter_Id_To_Load
Chapters_full_filename=os.path.join(Data, Chapters_filename)
Topics_links_filename='Topics.csv'
Topics_links_full_filename=os.path.join(Data, Topics_links_filename)
Messages_filename='Messages.csv'
Messages_full_filename=os.path.join(Data, Messages_filename)
max_count_messages_in_file=100000
attempts=10
delay=60


# In[6]:


def GetMessages(Topic_Url):
    html_page = urllib.request.urlopen(Base_URL+Topic_Url)
    soup = BeautifulSoup(html_page)
    Message_Ids = list()
    Parent_Ids = list()
    Date_Time = list()
    Author_Ids = list()
    Authors = list()
    Original_Messages = list()
    Messages = list()
    Message_chars = list()
    Message_words = list()
    Emojis = list()
    Images = list()
    Links = list()
    Original_Paragraphs = list()
    Actual_Paragraphs = list()
    Avg_Paragraph_chars = list()
    Avg_Paragraph_words = list()
    items = soup.findAll('li', {'class': 'item'})
    for item in items: 
        for message_id in item.findAll('div', {'class': 'id'}): 
            Message_Ids.append(message_id.text.strip().rstrip('\n').lstrip('\n')[1:])
            p_i=0
            for parent_id in item.findAll('div', {'class': 'message-id'}):
                p_i=parent_id.text.strip().rstrip('\n').lstrip('\n')[10:]         
            Parent_Ids.append(p_i) 
            for date_time in item.findAll('div', {'class': 'date-time'}):
                Date_Time.append(date_time.text.strip().rstrip('\n').lstrip('\n')[1:])         
            for author in item.findAll('div', {'class': 'author'}): 
                Authors.append(remove_urls(author.text.strip().rstrip('\n').lstrip('\n')))
                a_i=0
                for author_id in author.findAll('a', href=True):
                    a_i=author_id['href'][1:]
                Author_Ids.append(a_i)
            for message in item.findAll('div', {'class': 'body'}):
                Original_Messages.append(message)
                message_content=remove_urls(message.text.strip().rstrip('\n').lstrip('\n'))
                Messages.append(message_content)
                Message_chars.append(len(message_content))
                Message_words.append(len(message_content.split()))
                Emojis1 = 0
                Img = 0
                for img in message.findAll('img', src=True):
                    if '/design/eva/images/forum/' in img['src']:
                        Emojis1 = Emojis1 + 1
                    else:
                        Img = Img + 1 
                Images.append(Img)
                Emojis2=cnt_emoji(message_content)
                Emojis.append(Emojis1 + Emojis2)
                Links.append(len(message.findAll('a')))
                Original_Paragraphs.append(len(message.findAll('br')))
                ap=message.get_text(strip=True, separator='<br/>').count('<br/>')
                Actual_Paragraphs.append(ap)
                if ap>1:
                    pl = 0
                    pw = 0
                    for p in message.get_text(strip=True, separator='<br/>').split('<br/>'):
                        pl = pl + len(p)
                        pw = pw + len(p.split())
                    Avg_Paragraph_chars.append(pl/ap)
                    Avg_Paragraph_words.append(pw/ap)
                else:
                    Avg_Paragraph_chars.append(0)
                    Avg_Paragraph_words.append(0)
    return list(zip(Message_Ids, Parent_Ids, Date_Time, Author_Ids, Authors, Original_Messages, Messages, Message_chars,Message_words, Emojis, Images, Links, Original_Paragraphs,Actual_Paragraphs,  Avg_Paragraph_chars, Avg_Paragraph_words))


# In[10]:


Chapters = pd.read_csv(Chapters_full_filename, error_bad_lines=False, index_col=False) 



# In[8]:


Topics = pd.read_csv(Topics_links_full_filename, error_bad_lines=False, index_col=False) 
Topics.sort_values(by=['Chapter_Id','Topic_Id'], ascending=True, inplace=True)


# In[ ]:


for c_index, c_row in Chapters[Chapters['Chapter_Id']==Chapter_Id_To_Load].iterrows():
    File_Num=c_row['Messages_File']
    Messages_full_filename=os.path.join(Data, '%s-%s.csv'%(c_row['Chapter_Id'],File_Num))
    Messages=pd.DataFrame(columns=['Message_Id','Parent_Id','date_time','Author_Id','author','original_message','message','message_characters','message_words','emojis','images','links','original_paragraphs','actual_paragraphs',' avg_paragraph_characters', 'avg_paragraph_words','Topic_Id','Topic','Chapter_Id','Chapter'])
    #Messages = pd.read_csv(Messages_full_filename, error_bad_lines=False, index_col=False)
    print('Processing Chapter: %s(%s)'%(c_row['Chapter'],c_row['Chapter_Id']))
    cnt_topics=c_row['cnt_ProcessedTopics']
    for t_index, t_row in Topics[((Topics['Chapter_Id']==c_row['Chapter_Id']) & (Topics['Topic_Id']>=c_row['StartFromTopic']))].iterrows():
        #print('Processing Topic: %s(%s)'%(t_row['Topic'],t_row['Topic_Id']))
        print('.', end = ' '),
        cnt=0
        while cnt<attempts:
            try:
                t=GetMessages(t_row['Link'])
                if len(t)==0:
                    print()
                    print('No messages found in topic %s'%t_row['Link'])
                cnt=attempts
            except Exception as e:
                print('Something went wrong...'+ str(e))
                cnt=cnt+1
                print('Waiting...')
                time.sleep(delay)
                print('Attempt to read topic %s # %s'%(t_row['Topic_Id'],cnt+1))
        if cnt>attempts:
            print('Too many false attempts. Stop execution...')
            break
        t_pd = pd.DataFrame(t, columns=['Message_Id','Parent_Id','date_time','Author_Id','author','original_message','message','message_characters','message_words','emojis','images','links','original_paragraphs','actual_paragraphs',' avg_paragraph_characters', 'avg_paragraph_words'])
        t_pd['Topic_Id']=t_row['Topic_Id']
        t_pd['Topic']=t_row['Topic']
        t_pd['Chapter_Id']=c_row['Chapter_Id']
        t_pd['Chapter']=c_row['Chapter']
        Messages=Messages.append(t_pd)
        Messages.to_csv(Messages_full_filename, header=True, index=False)
        if len(Messages)>max_count_messages_in_file:
            File_Num=File_Num+1
            Chapters.at[c_index,'Messages_File']=File_Num
            Messages_full_filename=os.path.join(Data, '%s-%s.csv'%(c_row['Chapter_Id'],File_Num))
            Messages=pd.DataFrame(columns=['Message_Id','Parent_Id','date_time','Author_Id','author','original_message','message','message_characters','message_words','emojis','images','links','original_paragraphs','actual_paragraphs',' avg_paragraph_characters', 'avg_paragraph_words','Topic_Id','Topic','Chapter_Id','Chapter'])
            print('New file started: %s-%s.csv'%(c_row['Chapter_Id'],File_Num))
        Chapters.at[c_index,'LastProcessedTopic']=t_row['Topic_Id']
        cnt_topics=cnt_topics+1
        Chapters.at[c_index,'cnt_ProcessedTopics']=cnt_topics
        Chapters.to_csv(Chapters_full_filename, header=True, index=False)
        #print('Processed %s messages'%len(t_pd))
        #print('--------------------------------------------')
        if t_row['Topic_Id']==c_row['StopOnTopic']:
            break                  
print()
print('Processing  complete')            

