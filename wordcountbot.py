from steem import Steem
import os
steemPostingKey = os.environ.get('steemPostingKey')
from steem.blockchain import Blockchain
from steem.post import Post
import json
import datetime
import re
import time
from bs4 import BeautifulSoup
from markdown import markdown
from steembase.exceptions import (
    PostDoesNotExist
)
nodes = ['wss://steemd.privex.io', 'wss://steemd.pevo.science', 'wss://rpc.buildteam.io', 'wss://rpc.steemliberator.com', 'wss://gtg.steem.house:8090', 'wss://rpc.steemviz.com', 'wss://seed.bitcoiner.me', 'wss://steemd.steemgigs.org', 'wss://steemd.minnowsupportproject.org', 'https://rpc.buildteam.io', 'https://steemd.minnowsupportproject.org', 'https://steemd.pevo.science', 'https://rpc.steemviz.com', 'https://seed.bitcoiner.me', 'https://rpc.steemliberator.com', 'https://steemd.privex.io', 'https://gtg.steem.house:8090', 'https://rpc.curiesteem.com', 'https://steemd.steemgigs.org', 'https://api.steemit.com', 'wss://appbasetest.timcliff.com', 'https://api.steem.house']
post_urls = []
# Account to track for blacklisted/muted users
trackaccount = 'travelfeed'
# Tag to search in
tracktag = 'travelfeed'
# Account (previously added in steempy) to post the comments
postaccount = 'travelfeed-bot'
# Max. number of blacklisted (=muted) accounts to check
abusersmax = 20
# Comment for short posts 
shortposttext = "Hi @{}, \n Thank you for participating in the #travelfeed curated tag. To maintain a level of quality on the project we have certain criteria that must be met for participation. Please review the following: https://steemit.com/travelfeed/@travelfeed/how-to-participate-use-travelfeed-in-your-posts \n **We require at least 250 words, but your post has only {} words.** \n Thank you very much for your interest and we hope to read some great travel articles from you soon! \n Regards, TravelFeed"
# Comment for blacklisted users
blacklisttext = "Hi @{}, \n Thank you for participating in the #travelfeed curated tag. To maintain a level of quality on the project we have certain criteria that must be met for participation. Please review the following: https://steemit.com/travelfeed/@travelfeed/how-to-participate-use-travelfeed-in-your-posts \n Regards, TravelFeed"
def converter(object_):
    if isinstance(object_, datetime.datetime):
        return object_.__str__()

def stream_blockchain():
    try:
        steem = Steem(wif=steemPostingKey,node=nodes)
        blockchain = Blockchain()
        stream = map(Post, blockchain.stream(filter_by=['comment']))
        abusers = steem.get_following(trackaccount, '', 'ignore', abusersmax)
        print(time.strftime('%X')+" Info: Stream from blockchain started")
    except Exception as error:
        print(time.strftime('%X')+" Error: Could not start blockchain stream "+repr(error))
        stream_blockchain()
    while True:
        try:
            for post in stream:
                if post.is_main_post() and tracktag in post["tags"]:
                    permlink = post['permlink']
                    author = post["author"]
                    if permlink in post_urls:
                        print(time.strftime('%X')+" Info: Ignoring updated post")
                    elif any(d['following'] == author for d in abusers): 
                        try: 
                            post.reply(blacklisttext.format(author), "", postaccount)
                            print(time.strftime('%X')+" Success: I detected a blacklisted user and sucessfully left a comment for @{}".format(author))              
                        except:
                            print(time.strftime('%X')+" Info: I detected a blacklisted user but there was an error posting the comment, could be due to the 20 second limit on comments. I will try my best to not let him get away!")
                            time.sleep(19)
                            try:
                                post.reply(blacklisttext.format(author), "", postaccount)
                                print(time.strftime('%X')+" Success: Cool, now it worked, I successfully left a comment for the blaklisted user @{}!".format(author))
                            except:
                                print(time.strftime('%X')+" Warning: Nope, still an error, this blacklisted user (@{}) got away due to the error".format(author)+repr(error))
                    else:
                        try:
                            post_urls.append(permlink)
                            html = markdown(post["body"])
                            soup = BeautifulSoup(html, "html.parser")
                            text = ''.join(soup.findAll(text=True))
                            remlink = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', text)
                            count = len(re.findall(r'\w+', remlink))
                            if count > 249:
                                print(time.strftime('%X')+" Success: There is a new awesome post by @{} who posted with {} words".format(author, count))
                            else:
                                try:
                                    post.reply(shortposttext.format(author, count), "", postaccount)
                                    print(time.strftime('%X')+" Success: I detected a rule breaker and sucessfully left a comment for @{} since we require at least 250 words but I have only counted {} words in the post".format(author, count))              
                                except:
                                    print(time.strftime('%X')+" Info: I detected a rule breaker but there was an error posting the comment, could be due to the 20 second limit on comments. I will try my best to not let him get away!")
                                    time.sleep(19)
                                    try:
                                        post.reply(shortposttext.format(author, count), "", postaccount)
                                        print(time.strftime('%X')+" Success: Cool, now it worked, I successfully left a comment for @{}!".format(author))
                                    except:
                                        print(time.strftime('%X')+" Warning: Nope, still an error, the rulebreaker (@{}) got away due to this error: ".format(author)+repr(error))
                                        continue
                        except Exception as error:
                            print(time.strftime('%X')+" Warning: Error while processing post "+repr(error))
                            continue
        except PostDoesNotExist:
            print(time.strftime('%X')+" Info: Skipping invalid post")
            continue
        except Exception as error:
            print(time.strftime('%X')+" Info: Skipping blockchain error "+repr(error))
            stream_blockchain()
if __name__ == '__main__':
    stream_blockchain()
