import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import warnings; warnings.simplefilter('ignore')
import tweepy
import time
import json
#import infomap
from tqdm import tqdm, trange

class TweetMiner:

    result_limit    =   20    
    data            =   []
    api             =   False
    
    # Use the tokens and keys to esatblish connection 
    def __init__(self, keys_dict=None, api=api, result_limit = 20):
        
        if keys_dict == None:
            raise Exception("Please input Twitter keys!")
            
        else:
        
            self.twitter_keys = keys_dict
        
            auth = tweepy.OAuthHandler(keys_dict['consumer_key'], keys_dict['consumer_secret'])
            auth.set_access_token(keys_dict['access_token_key'], keys_dict['access_token_secret'])
        
            self.api = tweepy.API(auth)
        
            self.result_limit = result_limit
    
    # Test authentication
    def verify(self):
        try:
            self.api.verify_credentials()
            print("Authentication OK")
        except:
            print("Error during authentication")
    
    # Get basic information of the account hodler
    def my_info(self,friend=False):
        me = self.api.me()
        print("Screen_name:",me.screen_name)
        print("id:", me.id)
        print("Name:", me.name)
        print("Friends Count:", me.friends_count)
        print("Follower Count:", me.followers_count)
        
        if friend == True:
            print("")
            print("Friends: ")
            friends_me = []
            for f in me.friends():
                friends_me.append(f.screen_name)
            print(*friends_me,sep=', ')
     
    # Get basic information of any of the user. 
    # The input should  be user's id or screen_name
    def get_user_info(self, user, friend=False):
        user = self.api.get_user(user)
        print("Screen_name:",user.screen_name)
        print("id:", user.id)
        print("Name:", user.name)
        print("Friends Count:", user.friends_count)
        print("Follower Count:", user.followers_count)
        
        if friend == True:
            print("")
            print("Friends: ")
            friends_me = []
            for f in user.friends():
                friends_me.append(f.screen_name)
            print(*friends_me,sep=', ')
     
    # Save content as file
    def save_file(self, path, content):
        with open(path, 'w') as file:
            file.write(content)
    
    # Read the file line by line
    def load_file_line(self, path):
        with open(path, 'r') as file:
            content=[]
            for line in file:
                content.append(line)
        return content
    
    # Save dict to JSON file
    def save_json(self, path, content):
        with open(path, 'w') as jsonfile:
            json.dump(content, jsonfile, indent=4)
    
    # Load in the JSON file
    def load_json(self, path):
        with open(path,'r') as jsonfile:
            json_dict = json.load(jsonfile)
        return json_dict
    
    # Get the id of a user's friends
    # The input should  be user's id or screen_name
    def get_friends_id(self, user):
        friends_id = []
        u = self.api.get_user(user)
        num = u.friends_count
#         print("Friends Number: ", num)
        with tqdm(total=num) as pbar:
            for item in self.limit_handled(tweepy.Cursor(self.api.friends_ids, id=u.id).items(),friends_id):  
                friends_id.append(item)
                pbar.update(1)
        return friends_id
    
    # Get screnn of an id list, and return a dictionary of id and its screen_name
    def get_sreen_name(self, id_list):
        screen_name_dict = {}
        for id_n in id_list:
            sc_n = self.api.get_user(id_n).screen_name
            screen_name_dict[id_n] = sc_n
        return screen_name_dict
    
    # Transffer a lsit of id to screen name. With or without screen_name_dict is OK.
    def transfer_to_screen_name(self, id_list, screen_name_dict=None):
        if screen_name_dict==None:
            screen_name_dict=self.get_sreen_name(id_list)
        screen_name_list=[]
        for id_n in id_list:
            sc_n = screen_name_dict[id_n]
            screen_name_list.append(sc_n)
        return screen_name_list
    
    # Get friends count for a list of users
    def get_friends_count(self, data_list):
        count_list=[]
        for i in data_list:
            user = self.api.get_user(i)
            friends_count = user.friends_count
            count_list.append(friends_count)
        return count_list
    
    # Clean the user with firends count in some range. Also can include user without friends.
    def clean_user(self, data_list, lower_limit=1000001, uper_limit=1000000, zero=False):
        local_list=[]
        for i in data_list:
            local_list.append(i)
        
        for j in data_list:
            user = self.api.get_user(j)
            friends_count = user.friends_count
            
            if zero==False:
                if friends_count > lower_limit and friends_count < uper_limit:
                    local_list.remove(j)
            else:
                if friends_count==0 or (friends_count > lower_limit and friends_count < uper_limit):
                    local_list.remove(j)
        return local_list
    
    # Get the friends of a lsit of users,and retrun as a dict{user:firends_id_list}
    def get_friends_id_second(self,data_list):
        friends_2_id_dict={}
        for i in data_list:
            friends_2_id_dict[i] = self.get_friends_id(i)
        return friends_2_id_dict
    
    def get_tweets_dict(self, data_list):
        tweets_dict={}
        for user in data_list:
            tweets = []
            u = self.api.get_user(user)
            for item in self.limit_handled(tweepy.Cursor(self.api.user_timeline, id=u.id).items(),tweets_dict): 
                tweets.append(item)
            tweets_dict[user] = tweets
        return tweets_dict

    # Helper function to handle twitter API rate limit and TweepError
    def limit_handled(self, cursor, list_name):
        while True:
            try:
                yield cursor.next()

            except tweepy.RateLimitError:
                print("\nCurrent number of data points in list = " + str(len(list_name)))
                print('Hit Twitter API rate limit.')
                for i in range(3, 0, -1):
                    print("Wait for {} mins.".format(i * 5))
                    time.sleep(5 * 60)

            except tweepy.error.TweepError:
                print('\nCaught TweepError exception' )
                print("Length of the error list: ",len(list_name))
                print("Error Position: ", list_name[-1])
                print("")
                return True

            except StopIteration:
                break
                
    def parse_tweets(self,tweets_dict):
        # Weight quantity with **text**.

        # Combine timeline and user information as weight quantity. Including:
        # - freinds_number
        # - followers_number
        # - status_number
        # - quoted
        # - retweet
        # - reply
        # - text

        weight_quantity_text = {}
        
        Nodes_list, Nodes_set = self.dict_key_sl(tweets_dict)

        # for node, tweets_list in tweets_dict_n.items():
        for node, tweets_list in tweets_dict.items():

            weight_quantity_text[node] = {"freinds_number":0, "followers_number":0, "status_number":0, 
                                    "quoted":[], "retweet":[], "reply":[], "text":'0'}

            user = self.api.get_user(node)
            friends_number = user.friends_count
            followers_number = user.followers_count

            quoted_list = []
            retweet_list = []
            reply_list = []
            text_list = []

            for tweet in tweets_list:

                rt_flag = False

                # Text
                text = tweet.text
                text_list.append(text)

                # Quoted
                try:
                    quoted_name = tweet.quoted_status.user.screen_name

        #             if quoted_name in nodes_set:
                    if quoted_name in Nodes_set:
                        quoted_list.append(quoted_name)
                except:
                    pass

                # Retweet
                try:
                    retweet_name = tweet.retweeted_status.user.screen_name
                    rt_flag = True

        #             if retweet_name in nodes_set:
                    if retweet_name in Nodes_set:
                        retweet_list.append(retweet_name)
                except:
                    pass

                # Reply
                try:
                    error_test = tweet.entities['user_mentions'][0]['screen_name']
                    if not rt_flag:
                        for reply in tweet.entities['user_mentions']:
                            reply_name = reply['screen_name']

        #                     if reply_name in nodes_set:
                            if reply_name in Nodes_set:
                                reply_list.append(reply_name)
                except:
                    pass

            weight_quantity_text[node]["freinds_number"] = friends_number
            weight_quantity_text[node]["followers_number"] = followers_number
            weight_quantity_text[node]["status_number"] = len(tweets_list)

            weight_quantity_text[node]["quoted"] = quoted_list
            weight_quantity_text[node]["retweet"] = retweet_list
            weight_quantity_text[node]["reply"] = reply_list
            weight_quantity_text[node]["text"] = text_list


        print("Calculation Finished !!!")
        return weight_quantity_text
    
    def dict_key_sl(self, data_dict):
        key_list = []
        for key in data_dict:
            key_list.append(key)
        key_set = set(key_list) 
        return key_list, key_set    
    