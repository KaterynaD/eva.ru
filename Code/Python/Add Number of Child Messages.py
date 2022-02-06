#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import pandas as pd
import numpy as np


# In[ ]:


Data='/home/kate/Projects/eva/Data'
Messages_filename='Messages.csv'
Messages_full_filename=os.path.join(Data, Messages_filename)

no_childs_filename='no_childs.csv'
no_childs_full_filename=os.path.join(Data, no_childs_filename)

Childs_filename='cnt_childs_0.csv'
Childs_full_filename=os.path.join(Data, Childs_filename)
MaxLength=500000

# In[ ]:


Messages = pd.read_csv(Messages_full_filename, error_bad_lines=False, index_col=False)
no_childs = pd.read_csv(no_childs_full_filename, error_bad_lines=False, index_col=False)


# In[ ]:


#https://stackoverflow.com/questions/40861418/how-to-count-number-of-children-for-every-node-in-an-adjacency-tree-dataframe-in
def find_children(df, node, Topic_Id, explored_children = []):
    '''
    find direct children of a cerain node within a network 
    '''
    children = df.query('Parent_Id==@node and Topic_Id==@Topic_Id')['Message_Id'].values.tolist()    
    # Takes care of the case when we go back to an already visited node    
    new_children = set(children) - set(explored_children)

    return new_children

def recursive_find_children(df, node, Topic_Id, explored_children = []):
    '''
    recursively find all children of a certain node within a network
    '''

    new_children = find_children(df, node, Topic_Id, explored_children)

    # Exit Case, when we have arrived to a node with no children or we go back to an already visited node
    if not new_children:

        return set(explored_children)

    else: 
    # Recursive call
    # Add direct children and all children of children (to any nested level)
        new_explored_children = set(explored_children).union(set(new_children))
        return set(explored_children).union(*[recursive_find_children(df, nd,Topic_Id, new_explored_children) for nd in new_children])


# In[ ]:

Topics=pd.merge(Messages, no_childs, left_on='Topic_Id', right_on='Topic_Id', how='inner')
tid=Topics['Topic_Id'].unique().tolist()
print('Number of Topics to process: %s'%len(tid))


# In[ ]:


df_cnt_childs=pd.DataFrame(columns=['Topic_Id','Message_Id','Parent_Id','cnt_childs'])


# In[ ]:

n=1;
for id in tid: 
    df=Messages[Messages['Topic_Id']==id][['Topic_Id','Message_Id','Parent_Id']]
    all_nodes_in_topics = df.groupby('Topic_Id').apply(lambda x: set(x[['Message_Id', 'Parent_Id']].values.flatten())).to_dict()
    all_children = {Topic_Id : {node : recursive_find_children(df, node, Topic_Id) for node in all_nodes_in_topics[Topic_Id]} for Topic_Id in all_nodes_in_topics}
    all_children_number = {Topic_Id: {node: len(all_children[Topic_Id][node]) for node in all_children[Topic_Id]} for Topic_Id in all_children}
    cnt_childs_topic=pd.DataFrame.from_dict(all_children_number).reset_index()
    cnt_childs_topic.columns=['Message_Id','cnt_childs']
    df=pd.merge(df, cnt_childs_topic, left_on='Message_Id', right_on='Message_Id', how='inner')
    df_cnt_childs=df_cnt_childs.append(df)
    l = len(df_cnt_childs)
    if l>MaxLength:
        print(l)
        print('Starting new file')
        Childs_filename='cnt_childs_%s.csv'%n
        Childs_full_filename=os.path.join(Data, Childs_filename)
        df_cnt_childs.to_csv(Childs_full_filename, header=True, index=False)
        df_cnt_childs=pd.DataFrame(columns=['Topic_Id','Message_Id','Parent_Id','cnt_childs'])
        n=n+1
    print('.', end = ' '),
print()
df_cnt_childs.to_csv(Childs_full_filename, header=True, index=False)
print('Processing  complete')     


# In[ ]:


df_cnt_childs.tail()

