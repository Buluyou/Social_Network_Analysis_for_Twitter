# Social_Network_Analysis_for_Twitter
SNA from the zero

Description: Code for MISCADA Final Dissertation.
Author: XIAO JIN
Date: 9/4/2020

This code is the implementation of the final dissertation project, Social Network Analysis for Twitter. Technically, we only need one class to include all of modules. But to make the presentation more clear, we separate it into three class and perform different process in three notebooks. We also extract the first class to the "TweetMiner.py" so that other class can inherit from the class "TweetMiner".

1. Data_Mining
As the raw data is too large to collect in short time, we choose a user with few friends as the root user to demonstrate the whole process of data mining. 
*Output:* "Attribute_Dataset.json" and "Relational_Dataset.json", which are two datasets.

2. Graph Generation
As we have the pre-mined original dataset  "Friends_2_id_dict.json" and "Weight_quantity" which are the relational dataset and atrribute dataset for the project. Thus, we generate the graph based on these two datasets. 
*Output:*  "Ego_1.5_Graph_HuXijin_GT.gexf" and "Ego_2_Graph_HuXijin_GT.gexf", which are two egocentric graphs.

3. Analysis
We perform social network analysis on the graph generated in last step. We only analyze the samller graph, because the analysis on large graph would take a lot time. So, we pre-saved the analysis result of the larger graph in "G2_centrality.csv" and also dispaly it in the notebook.
*Output:* "Community_Detection.gexf" , which is the graph with the communities detected, and all the plot are shown in the notebook.

