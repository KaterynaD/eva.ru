from bs4 import BeautifulSoup
import urllib.request
import os
import pandas as pd
import numpy as np

Base_URL='https://eva.ru'
Data='/home/kate/Projects/eva/Data'
Chapters_filename='Chapters.csv'
Chapters_full_filename=os.path.join(Data, Chapters_filename)
Topics_links_filename='Topics.csv'
Topics_links_full_filename=os.path.join(Data, Topics_links_filename)

def GetTopics_v1(archive_topics_url,topics_folder,chapter_id):
    html_page = urllib.request.urlopen(archive_topics_url)
    start = '<h3>'
    end = '</h3>'
    Topics_Names=list()
    Topics_Links=list()
    Chapters_ids=list()
    soup = BeautifulSoup(html_page)
    for link in soup.findAll('a'):
        l=link['href']
        if '/%s/messages-'%topics_folder in l:
            topic_link=l
            s=str(link)
            topic_name=s[s.find(start)+len(start):s.rfind(end)]
            Chapters_ids.append(chapter_id)
            Topics_Links.append(topic_link)
            Topics_Names.append(topic_name)
    return list(zip(Chapters_ids,Topics_Names,Topics_Links))
    
Chapters = pd.read_csv(Chapters_full_filename, error_bad_lines=False, index_col=False) 

Topics=pd.DataFrame(columns=['Chapter_Id','Name','Link'])
for index, row in Chapters[Chapters['StopOnPage']>Chapters['ProcessedPage']].iterrows():
    page=row['StartFromPage']
    StopOnPage=row['StopOnPage']
    topics_folder=row['Folder']
    chapter_id=row['Id']
    print('Starting chapter %s'%row['Chapter'])
    while True:
        print('%s,'%page, end = " "),
        try:
            t=GetTopics_v1('%s/%s/topics-%s.htm?pageNum=%s'%(Base_URL,topics_folder,chapter_id,page),topics_folder,chapter_id)
            if len(t)==0:
                print()
                print('No topics found on page %s'%page)
                break            
            Topics=Topics.append(pd.DataFrame(t, columns=['Chapter_Id','Name','Link']))
            Topics.to_csv(Topics_links_full_filename, header=True, index=False)
            Chapters.at[index,'ProcessedPage']=page
            Chapters.to_csv(Chapters_full_filename, header=True, index=False)  
            if page==StopOnPage:
                break                    
            page=page+1
        except Exception as e:
            print('Something went wrong...'+ str(e))
            break
    print()
    print('Processing chapter %s complete'%row['Chapter'])