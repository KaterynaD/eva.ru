# eva.ru
What Russian women talk about - Natural Language Processing (NLP) research of Russian women eva.ru forum

eva.ru forums exist for more than 10 years. You need to register to publish your posts, but you can do it anonymously. Even your virtual identity is known only to forum administrators and readers cannot connect various anonymous posts to one person. No registration is needed to read the forums.

Due to the anonymity hundreds of women freely discuss sensitive topics. However, there are a lot of sarcasm and even aggression due to the anonymity. The site is the only place where many women can spill out disappointment in life, spouses, kids, parents, jobs etc. Most of replies are negative (except Kids Psychology and Development) and “It happened to you because you are dummy and do not deserve better!” is a usual reaction for most concerns. 

Topics in forums are built as dialogs in a tree-form. A topic starter publishes a first post and other women reply, ask additional questions directly to this first post or organize separate branches starting from replies to the first post. 

There is practically no limit on the length of posts and because participants are usually educated, middle-aged persons there are almost no gibberish.  Profanity and especially aggressive posts are deleted by moderators. 

I choose eva.ru forums as a data source because I read forums for years as a relax between coding and to keep up to date my Russian. I know what women talking about in these forums and can feel how good modeling results are even without special metrics. I was also interested in a review of available NLP libraries and Hugging Face transformers pre-trained models for Russian language.

Projects (eva.ru/Code/Notebooks/):

0. Download Posts - Initial data download and cleaning eva.ru posts from 3 forums for more then 10 years (2009 - July 2021):
 - Kids Psychology and Development (869,532 posts in 21,892 organized discussions - topics)
 - HotLine (4,850,444 posts in 49,324 topics)
 - Everything else (3,735,637 in 54,075 topics)
 
There are more forums available, the 3 I downloaded for my research I read daily. Totaly there are more then 9M posts in 125,291 separate topics. There is a limit on the number of posts download per topic (no more then 300) somewhere at the level of eva.ru web-engine. So, the numbers do not represent the exact number of posts.
 
eva.ru has 2 modes to read forums: a mobile version when all topics posts are downloaded in one page and a version to read from a computer with frames and an individual post available in a frame. First I downloaded topics IDs from all forums (0. DownloadTopicsLinks.ipynb) and then, posts from each topic using the mobile version of the forums(1. DownloadMessages.ipynb). Posts were extracted from web pages, clened up from html tags, links, emojis using Beautiful Soup library, etc as well as basic statistics as the number of words and paragraphs was calculated in the process. The download is much faster from the mobile version, but unfortunatelly, "year" is missing in posts dates. That's why, having individual posts IDs I downloaded separate posts to extract full posts dates (2. DownloadMessagesDates.ipynb).

1. Other Preprocessing
  - The forums have a tree-based structure, that's why a number of child posts (replies) was calculated (0. Add Number of Child Messages.ipynb).
  - 2 types of sentiment analysis was conducted: based on Dostoevsky library (1. Sentiment Analysis - Dostoevsky.ipynb) and based on several transformers models from Hugging Face (2. Transformers Sentiment Analysis.ipynb). Models tested: 
     - Tatyana/rubert_conversational_cased_sentiment
     - blanchefort/rubert-base-cased-sentiment
     - Skoltech/russian-inappropriate-messages
  - The data were combined together and briefly analyzed in 3. Sentiments Analysis.ipynb Sentiments based on "Tatyana/rubert_conversational_cased_sentiment" are 100% match sentiments from "blanchefort/rubert-base-cased-sentiment" for whatever reason (was doublechecked few times.). Only "Tatyana" sentiments are used in further analysis. Inappropriate messages detection is not useful in the analysis. Forums moderators did a great job. The only few detected inapropriate messages are related to, in fact, negative comments about slapping kids. I wish there were sarcasm detection for russian language instead!

2. Text Extended Attributes are features like part of speach, number of commas, exlamations marks, sentences, etc
 - 0. TextExtendedAttributes_FeatureEngineering.ipynb is used to prepare the features with a help of treetagger for POS. It's slow and ineffective. pymorphy2 library was used in the later research.
 - 1. Posts Text Attributes EDA.ipynb abalyzes the forums posts. It's used in the further analysis of forum users only. 

3. Time Trends is analysis of posts publication dates. 
 - 0. TimeTrends FeatureEngineering.ipynb is just pre-calculates time related features
 - 1. TimeTrends Analysis.ipynb is EDA:
    - The best days of the forum were before 2012 when more posts were published monthly comparing to nowdays. Users posted their messages using their names mostly, not anonymously. The next spike is 2020 Mar-May COVID-19 lockdown. Seasonality is clear seen in the data when less posts are published in summer time.
    - Less posts on weekends, even on Friday.
    - Most posts are published day time from offices or when kids are in school. Early morning and night messages are from users in US and Canada or somebody who do not sleep.

4. Authors (forum users). Anonymous users are not taken into account in this research.
 - 0. Authors.ipynb - the listof frum users is created based on the downloaded posts. The code extracts author IDs, last used nick names (can be changed overtime or in different posts), numbers of posts published, the date of the first and last posts, number of discussions started, number or replies to their posts, and many other attributes aggregated in different ways from text extended attributes, sentiment analysis, time trends. A quick EDA is done in teh process attributes extractions
 - 1. Authors Segmentation by Style.ipynb is EDA and authors clusterization. The result of the code are attributes most important to distinguish users (total number ofusers  posts was not taken into account):
    - Number of posts with commas (fraction_of_medium_with_commas)
    - Average number of sentences (avg_num_sent)
    - Number of large topics were created by user (topics with number of posts more then average in a forum chapter) (fraction_of_Large_Topics)
    - Average by all posts fraction of recognized adjective and nouns to verbs
    - Average number of commas (avg_num_commas)
    - How many posts with discussions (start a branch in a topic to discuss something) (fraction_of_messages_with_discussion)
    - Average by all posts TTR_A - fraction of unique recognized adjectives in a message to all recognized adjective: TTR_A = num_unique_Adj/num_Adj
Basically, the complexity of text (size, commas, adjectives), interest for the public and emotional tempreture of the posts are important. (The more emotional post, the more replies and discussions it has.)

4 clusters were separated.

5. Posts similarity and clones detection. Hugging Face Transformers models available for Russian language were tested in this research.
  - 5. Philologist. It's an anonymous user but with very specific style. Her texts are long, paragraphs are double separated and she writes for very specific subjects only. This is an ideal candidate for text similarity study because I can not create a train/test subsets but can select all long texts with double separation between paragraphs for analysis. A few posts which are definetly were made by Philologist (she names herself in few posts in this way but did not open her registered user anywhere to easily combine posts.) The selected posts were used as a sample to find other similar posts. A manual review shows the similarity process was wrong in just few posts. However, the more posts are found, the harder to review and exclude other authors. Still, I was able to identify hundreds of posts teh same anonymous author.
  - 6. lizon. This lady created numerous clones but she is easy identified by the style and subjects. She likes to add photes and links to photos in her posts. No a surprise, the model trained on the original, not cleaned from html tags, posts is much better then models built on just pure text. "blinoff/roberta-base-russian-v0" pre-trained model has the best score. In general, the process is strightforward but 2 steps need more attention:
    - How to build traing/test dataset for s specific user? Using all available downloaded data (9M of posts) makes the data so unbalanced and large, it is not possible to use in practise. But, in fact, there are even more available data not downloaded. I choose one first, user, and posts from all topics where she participated, for training and test. The dataset is still unbalanced but more reasonable and processable in Google Colab GPU instance. All users and discussions after the last known post of teh pre-selected user are data for prediction, e.g. dataset to find clones in.
    -  There is still non 0, but low number of users similar by style and subjects to the selected author. They are appeared in the predicted results. the question is how to limit the number of found clones to the real one. It was easy for lizon, but not for Fedulya user.
    -  0. lizon_Data_Preparation.ipynb creates train/test dataset
    -  1. lizon_finetuning_experiments.ipynb researches different models and ways to train using ktrain library
    -  3. lizon_transformers_final.ipynb creates a final model or rather a set of several models trained on different folds.
    -  4. lizon_prediction.ipynb predicts clones based on the rest of the downloaded data.
    
 Even more interesting research, if a new model can distinguish between clones the first model found?
   - 5. lizon_dissimilarity_model.ipynb
   - 6. lizon_dissimilarity_2LargestAccounts_model.ipynb
   - 7. lizon_dissimilarity_3MediumAccounts_model.ipynb
   The more messages from a particular clone the better difference detected. 500 - 1000 posts to detect a difference.
  
  - 7. Fedulya Surprisingly but the original, not cleaned from html tags posts are more informative for a classification model even without a lot of links and photos as in a case of lizon. The difference between models is not so large but still significant. This user has even more clones. Without similar user names it was difficult to say if it's teh same person or different because the number of similar posts are low.

8. Topic Modeling Top2vec works perfectly fine to extract topics discussed and understand What Russian women talking about. 
