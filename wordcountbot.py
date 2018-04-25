from steem import Steem
import os
steemPostingKey = os.environ.get('steemPostingKey')
from steem.blockchain import Blockchain
from steem.post import Post
import json
import datetime
import re
import time
import random
from bs4 import BeautifulSoup
from markdown import markdown
from steembase.exceptions import PostDoesNotExist
from langdetect import detect
import atexit
# Account to track for blacklisted/muted users
trackaccount = 'travelfeed'
# Tag to search in
tracktag = 'travelfeed'
# Account (previously added in steempy) to post the comments
postaccount = 'travelfeed-bot'
# List of whitelisted users who are allowed to post short posts
whitelist = ['tangofever']
# Max. number of blacklisted (=muted) accounts to check
abusersmax = 20
# Comment for short posts 
shortposttext = "Hi @{}, \n Thank you for participating in the #travelfeed curated tag. To maintain a level of quality on the project we have certain criteria that must be met for participation. Please review the following: https://steemit.com/travelfeed/@travelfeed/how-to-participate-use-travelfeed-in-your-posts \n **We require at least 250 words, but your post has only {} words.** \n Thank you very much for your interest and we hope to read some great travel articles from you soon! \n Regards, TravelFeed"
# Comment for blacklisted users
blacklisttext = "Hi @{}, \n Thank you for participating in the #travelfeed curated tag. To maintain a level of quality on the project we have certain criteria that must be met for participation. Please review the following: https://steemit.com/travelfeed/@travelfeed/how-to-participate-use-travelfeed-in-your-posts \n **You are currently blacklisted from the TravelFeed curation.** \n This is most likely because we have detected plagiarism in one of your posts in the past. If you believe that this is a mistake, please contact us on the [Steemit Travellers Discord](https://discord.gg/jWWu73H). c \n Regards, TravelFeed"
# Comment for other languages
wronglangtext = "Hi @{}, \n Thank you for participating in the #travelfeed curated tag. To maintain a level of quality on the project we have certain criteria that must be met for participation. Please review the following: https://steemit.com/travelfeed/@travelfeed/how-to-participate-use-travelfeed-in-your-posts \n **We require at least 250 words in English, but your post seems to be in another language.** (The language of your post was automatically detected, if your post is in English, please ignore this message.) \n Thank you very much for your interest and we hope to read some great travel articles from you soon! \n Regards, TravelFeed"
# Define path for logging
logpath = 'short_posts.log'
try: 
    with open(logpath) as f:
        post_urls = f.read().splitlines()
    file.close()
except:
    post_urls = []
def converter(object_):
    if isinstance(object_, datetime.datetime):
        return object_.__str__()

def stream_blockchain(starting_point):
    try:
        nodenr = random.randint(1, 4)
        if nodenr%4 == 0: 
            nodes = ['https://rpc.buildteam.io', 'wss://steemd.steemgigs.org']
        elif nodenr%4 == 1:
            nodes = ['https://rpc.steemliberator.com', 'wss://gtg.steem.house:8090']
        elif nodenr%4 == 2:
            nodes = ['wss://steemd.privex.io', 'https://rpc.steemviz.com']
        else:
            nodes = ['wss://steemd.pevo.science', 'https://api.steemit.com']
        steem = Steem(wif=steemPostingKey,node=nodes)
        blockchain = Blockchain()
        if not starting_point:
            try:
                props = steem.get_dynamic_global_properties()
                starting_point = props['last_irreversible_block_num']
            except:
                stream_blockchain(None)
        stream = map(Post, blockchain.stream(filter_by=['comment'], start_block=starting_point))
        abusers = steem.get_following(trackaccount, '', 'ignore', abusersmax)
        print(time.strftime('%X')+" Info: Stream from blockchain started with nodes "+str(nodes).strip('[]')+" starting at block "+str(starting_point))
    except Exception as error:
        print(time.strftime('%X')+" Warning: Could not start blockchain stream. Switching nodes. "+repr(error))
        stream_blockchain(None)
    while True:
        try:
            for post in stream:
                try:
                    tags = post["tags"]
                except:
                    tags = []
                if post.is_main_post() and tracktag in tags:
                    permlink = post['permlink']
                    author = post["author"]
                    commenttext = ""
                    if permlink in post_urls:
                        print(time.strftime('%X')+" Info: Ignoring updated post")
                    elif author in whitelist:
                        print(time.strftime('%X')+" Info: Ignoring short post by whitelisted user @{}".format(author))
                    elif any(d['following'] == author for d in abusers): 
                        commenttext = blacklisttext
                        print(time.strftime('%X')+" Success: Detected post by blacklisted user @{}".format(author))
                    else:
                        try:
                            html = markdown(post["body"])
                            soup = BeautifulSoup(html, "html.parser")
                            text = ''.join(soup.findAll(text=True))
                            remlink = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', text)
                            count = len(re.findall(r'\w+', remlink))
                            try:
                                lang = detect(remlink)
                            except:
                                lang = "en"
                            if not lang == "en":
                                commenttext = wronglangtext
                            elif count < 250:
                                commenttext = shortposttext
                                print(time.strftime('%X')+" Success: Detected short post by @{} who posted with just {} words".format(author, count))
                        except Exception as error:
                            print(time.strftime('%X')+" Warning: Error during content processing "+repr(error))
                            continue
                    if not commenttext == "":
                        try:
                            post.reply(commenttext.format(author, count), "", postaccount)
                            print(time.strftime('%X')+" Success: I sucessfully left a comment for @{}".format(author))              
                        except:
                            print(time.strftime('%X')+" Info: There was an error posting the comment, could be due to the 20 second limit on comments. I will try again.")
                            time.sleep(19)
                            try:
                                post.reply(commenttext.format(author, count), "", postaccount)
                                print(time.strftime('%X')+" Success: Cool, now it worked, I successfully left a comment for @{}!".format(author))
                            except:
                                print(time.strftime('%X')+" Warning: Nope, still an error, I could not levae a comment for (@{}) due to this error: ".format(author)+repr(error))
                                continue
                    else:
                        print(time.strftime('%X')+" Info: Ignoring awesome post by @{}".format(author))
                    post_urls.append(permlink)
        except PostDoesNotExist:
            print(time.strftime('%X')+" Info: Skipping blockchain error")
            continue
        except Exception as error:
            try:
                props = steem.get_dynamic_global_properties()
                starting_point = props['last_irreversible_block_num']
            except:
                starting_point = None
            print(time.strftime('%X')+" Warning at block "+str(starting_point)+": "+repr(error))
            stream_blockchain(starting_point)

def exit_handler():
    file = open(logpath, 'a+')
    for item in post_urls:
        file.write("%s\n" % item)
    file.close()

if __name__ == '__main__':
    starting_point=None
    stream_blockchain(starting_point)

atexit.register(exit_handler)