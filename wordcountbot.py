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
from steembase.exceptions import PostDoesNotExist, RPCError
nodenr = 1
nodes = []
post_urls = []
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
blacklisttext = "Hi @{}, \n Thank you for participating in the #travelfeed curated tag. To maintain a level of quality on the project we have certain criteria that must be met for participation. Please review the following: https://steemit.com/travelfeed/@travelfeed/how-to-participate-use-travelfeed-in-your-posts \n Regards, TravelFeed"
def converter(object_):
    if isinstance(object_, datetime.datetime):
        return object_.__str__()

def stream_blockchain():
    try:
        if nodenr%4 == 0: 
            nodes = ['https://steemd.privex.io', 'https://api.steemit.com']
        elif nodenr%4 == 1:
            nodes = ['https://rpc.steemliberator.com', 'https://gtg.steem.house:8090']
        elif nodenr%4 == 2:
            nodes = ['https://steemd.pevo.science', 'https://rpc.steemviz.com']
        else:
            nodes = ['https://rpc.buildteam.io', 'https://steemd.minnowsupportproject.org']
        steem = Steem(wif=steemPostingKey,node=nodes)
        blockchain = Blockchain()
        stream = map(Post, blockchain.stream(filter_by=['comment']))
        abusers = steem.get_following(trackaccount, '', 'ignore', abusersmax)
        print(time.strftime('%X')+" Info: Stream from blockchain started")
    except Exception as error:
        print(time.strftime('%X')+" Info: Could not start blockchain stream. Switching nodes. "+repr(error))
        ++nodenr
        stream_blockchain()
    while True:
        try:
            for post in stream:
                if post.is_main_post() and tracktag in post["tags"]:
                    permlink = post['permlink']
                    author = post["author"]
                    if permlink in post_urls:
                        print(time.strftime('%X')+" Info: Ignoring updated post")
                    elif author in whitelist:
                        print(time.strftime('%X')+" Info: Ignoring short post by whitelisted user")
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
        except RPCError:
            print(time.strftime('%X')+" Info: Blockchain Error. Switching node.")
            ++nodenr
            stream_blockchain()
        except PostDoesNotExist:
            print(time.strftime('%X')+" Info: Skipping invalid post")
            continue
        except Exception as error:
            print(time.strftime('%X')+" Warning: Blockchain error "+repr(error))
            continue
if __name__ == '__main__':
    stream_blockchain()
