#!/usr/bin/env python
# coding: utf-8

# ### Number of specific Part of Speech (POS) in Russian text, punctuation, length of words
# * Basic text attributes were calculated during download to be used in quick ongoing analysis
# * Even more complex coefficients can be calculated but number of sentences is required. Punctuation is frequently omitted in forum posts and everything which depend on it is not reliable. A special model to predict punctuation could be help
# https://linguistics.stackexchange.com/questions/3167/are-there-sentence-boundary-disambiguation-algorithms-which-can-handle-punctuati

# In[1]:


import os
import pandas as pd
import numpy as np
import datetime


# In[2]:


#!pip install treetaggerwrapper
import treetaggerwrapper


# In[3]:


from itertools import groupby
def replace_consequent_symbols(text,whatever):
    for k, g in groupby(text):
        size = len(list(g))
        if k in whatever:
            text=text.replace(k * size,k)
    return text


# In[4]:


#number of correspondent lemmas based on value in pos
def num_pos(pos_to_count,pos_list,lemmas_list):
    index_list=[idx for idx, val in enumerate(pos_list) if val.startswith(pos_to_count)]
    num_pos=len(index_list)
    num_unique_pos=len(set([lemmas_list[i] for i in index_list]))
    return num_pos,num_unique_pos


# In[5]:


#number of symbols from whatever in text
def count_whatever(text,whatever):
    cnt=0
    for v in whatever:
        cnt = cnt + text.count(v)
    return cnt


# In[6]:


#Start_Message_Id=int(sys.argv[1:][2])
#End_Message_Id=int(sys.argv[1:][3])
#Part=int(sys.argv[1:][4])
Start_Message_Id=0
End_Message_Id=100000
Part=0


# In[7]:


print('Starting from message number: %s'%Start_Message_Id)
print('Ending with message number: %s'%End_Message_Id)
print('Result will be saved in %s part'%Part)


# In[8]:


Data='/home/kate/Projects/eva/Data/Main'

Message_filename='Messages.csv'
Message_full_filename=os.path.join(Data, Message_filename)
text_column='message'

ta_extended_extension_filename='Extended/TextExtendedAttributes_ext_%s.csv'%Part
ta_extended_extension_full_filename=os.path.join(Data, ta_extended_extension_filename)

long_word_syllabels=3
rus_vowels = 'аэыуояеёюи'
replace_consequent='!?.,)()'


# In[9]:


Messages = pd.read_csv(Message_full_filename, error_bad_lines=False, index_col=False) 


# In[10]:


SubsetToAnalyze=Messages[Start_Message_Id:End_Message_Id+1:1].copy(deep=True)


# In[11]:


del Messages


# In[12]:


SubsetToAnalyze[text_column]=SubsetToAnalyze[text_column].fillna(' ')


# In[13]:


tagger = treetaggerwrapper.TreeTagger(TAGLANG='ru')


# In[14]:


def calculate_all_metrics(m):
    metrics=list()
    m=m+'.'
    
    #if there are !!!!!!!!!! or ??????? or ?!!! or !????
    flg_excessive_exclamations=1 if '!!' in m else 0
    metrics.append(flg_excessive_exclamations)
    flg_excessive_questions=1 if '??' in m else 0
    metrics.append(flg_excessive_questions)
    flg_excessive_other=1 if (('?!' in m) | ('!?' in m)) else 0
    metrics.append(flg_excessive_other)

    #replacing excessive !? to correctly count sentences
    m=replace_consequent_symbols(m,replace_consequent)
    m = m.replace('?!','?').replace('!?','!')

    
    #defining POS (part-of-speach) and corresponding lammas
    ctags = tagger.tag_text(m)
    #currupted text may result in missing/t
    ctags=[i if len(i.split('\t', 2))==3 else '-\t-\t\-t' for i in ctags]
    pos=[i.split('\t', 2)[1] for i in ctags]
    lemma=[i.split('\t', 3)[2] for i in ctags]

    #number of sentences is incorrect in many cases because punctuation signs are missing or there is no space after 
    #need a finetuned model to predict end of sentence for russian. 
    #https://linguistics.stackexchange.com/questions/3167/are-there-sentence-boundary-disambiguation-algorithms-which-can-handle-punctuati
    #num_sentences=pos.count('SENT')
    #if num_sentences==0:
    #    num_sentences=1
    #metrics.append(num_sentences)

    #number of nouns(Nc), verbs(Vm) and adjective(Af):
    (num_Adj, num_unique_Adj)=num_pos('Af',pos,lemma)
    if num_Adj==0:
        num_Adj=1
    metrics.append(num_Adj)
    metrics.append(num_unique_Adj)
    (num_Nouns, num_unique_Nouns)=num_pos('Nc',pos,lemma)
    if num_Nouns==0:
        num_Nouns=1    
    metrics.append(num_Nouns)
    metrics.append(num_unique_Nouns)
    (num_Verb, num_unique_Verb)=num_pos('Vm',pos,lemma)
    if num_Verb==0:
        num_Verb=1        
    metrics.append(num_Verb)
    metrics.append(num_unique_Verb)
    num_tokens=num_Adj + num_Nouns + num_Verb
    metrics.append(num_tokens)
    num_unique_tokens=num_unique_Adj + num_unique_Nouns + num_unique_Verb
    metrics.append(num_unique_tokens)

    #number of syllables and long words based on vowels
    vowels = [count_whatever(i,rus_vowels) for i in lemma]
    num_syllables=sum(vowels)
    metrics.append(num_syllables)
    index_list=[idx for idx, val in enumerate(vowels) if val>long_word_syllabels]
    num_long_words = len([lemma[i] for i in index_list])
    metrics.append(num_long_words)
    num_unique_long_words = len(set([lemma[i] for i in index_list]))
    metrics.append(num_unique_long_words)

    #number of !,? and ,
    num_commas=count_whatever(m,'!')
    metrics.append(num_commas)
    num_exclamations=count_whatever(m,'!')
    metrics.append(num_exclamations)
    num_questions=count_whatever(m,'?')
    metrics.append(num_questions)

    #no need to calculate, already in the dataset but needed for the further calculation
    num_words=len(m.split(' '))
    metrics.append(num_words)
    #avg_sent_words = num_words/num_sentences
    #metrics.append(avg_sent_words)

    #ratio calculations based on the above
    #ASL = num_words/num_sentences
    #metrics.append(ASL)
    ASW = num_syllables/num_words
    metrics.append(ASW)
    PLW = num_long_words/num_words
    metrics.append(PLW)
    TTR = num_unique_tokens/num_tokens
    metrics.append(TTR)
    TTR_A = num_unique_Adj/num_Adj
    metrics.append(TTR_A)
    TTR_N = num_unique_Nouns/num_Nouns
    metrics.append(TTR_N)
    TTR_V = num_unique_Verb/num_Verb
    metrics.append(TTR_V)
    if TTR_V!=0:
        NAV = (TTR_A +TTR_N)/TTR_V
    else:
        NAV = 0
    metrics.append(NAV)
    if num_unique_Verb!=0:
        UNAV = (num_unique_Adj +num_unique_Nouns)/num_unique_Verb
    else:
        UNAV = 0
    metrics.append(UNAV)
    fraction_of_commas=num_commas/num_words
    metrics.append(fraction_of_commas)
    fraction_of_exclamations=num_exclamations/num_words
    metrics.append(fraction_of_exclamations)
    fraction_of_questions=num_questions/num_words
    metrics.append(fraction_of_questions)
    fraction_of_Adj=num_Adj/num_words
    metrics.append(fraction_of_Adj)
    fraction_of_Nouns=num_Nouns/num_words
    metrics.append(fraction_of_Nouns)
    fraction_of_Verbs=num_Verb/num_words
    metrics.append(fraction_of_Verbs)
    
        
    #Almost all coefficients are based on ASL which is not reliable because num_sentences issue See above
    #Also the same number of tokens should be taken into account in analysis which is not strightforward in forum posts
    #It does not make sense to use them in further analysis for now
    #Readability_Z1 = (0.62 * ASL) + (0.123 * PLW) + 0.051
    #metrics.append(Readability_Z1)
    #F4 =0.83*UNAV-6.73*TTR+0.24*ASL+3.36*ASW-2.41
    #metrics.append(F4)
    #F5 =0.81*UNAV-5.47*TTR_A+0.24*ASL+3.28*ASW-0.6*NAV-1.79
    #metrics.append(F5)
    #Q = - 0.124*ASL + 0.018*ASW - 0.007*UNAV + 0.007*NAV - 0.003*math.pow(ASL,2) + 0.184*ASL*ASW + 0.097*ASL*UNAV - 0.158*ASL*NAV + 0.09*math.pow(ASW,2) + 0.091*ASW*UNAV + 0.023*ASW*NAV - 0.157*math.pow(UNAV,2) - 0.079*UNAV*NAV + 0.058*math.pow(NAV,2)
    #metrics.append(Q)
    #Z2 = 0.5+ASL+8.4+ASW-15.59
    #metrics.append(Z2)
    df = pd.DataFrame([metrics],columns=[
'flg_excessive_exclamations',
'flg_excessive_questions',
'flg_excessive_other',
#'num_sentences',
'num_Adj',
'num_unique_Adj',
'num_Nouns',
'num_unique_Nouns',
'num_Verb',
'num_unique_Verb',
'num_tokens',
'num_unique_tokens',
'num_syllables',
'num_long_words',
'num_unique_long_words',
'num_commas',
'num_exclamations',
'num_questions',
'num_words',
#'avg_sent_words',
#'ASL',
'ASW',
'PLW',
'TTR',
'TTR_A',
'TTR_N',
'TTR_V',
'NAV',
'UNAV',
'fraction_of_commas',
'fraction_of_exclamations',
'fraction_of_questions',
'fraction_of_Adj',
'fraction_of_Nouns',
'fraction_of_Verbs'
#'Readability_Z1',
#'F4',
#'F5',
#'Q',
#'Z2'
    ])
    return df


# In[15]:


print(datetime.datetime.now())
TextAttr_df=pd.DataFrame()
for index, row in SubsetToAnalyze.iterrows():
    #print(len(row[text_column]))
    df=calculate_all_metrics(row[text_column])
    df['Message_Id']=row['Message_Id']
    TextAttr_df=TextAttr_df.append(df)
    #print('.', end = ' '),
print(datetime.datetime.now()) 
TextAttr_df.to_csv(ta_extended_extension_full_filename, header=True, index=False) 
print()
print('Processing  complete')    

