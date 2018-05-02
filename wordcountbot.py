### Configuration start: Adjust these variables
# Account to track for blacklisted/muted users
trackaccount = 'travelfeed'
# Tag to search in
tracktag = 'travelfeed'
# Account to post the comments
postaccount = 'travelfeed-bot'
# List of whitelisted users who are allowed to post short posts
whitelist = ['travelfeed', 'tangofever']
# Comment for short posts 
shortposttext = "Hi @{}, \n Thank you for participating in the #travelfeed curated tag. To maintain a level of quality on the project we have certain criteria that must be met for participation. Please review the following: https://steemit.com/travelfeed/@travelfeed/how-to-participate-use-travelfeed-in-your-posts \n **We require at least 250 words, but your post has only {} words.** \n Thank you very much for your interest and we hope to read some great travel articles from you soon! \n Regards, TravelFeed"
# Comment for blacklisted users
blacklisttext = "Hi @{}, \n Thank you for participating in the #travelfeed curated tag. To maintain a level of quality on the project we have certain criteria that must be met for participation. Please review the following: https://steemit.com/travelfeed/@travelfeed/how-to-participate-use-travelfeed-in-your-posts \n **You are currently blacklisted from the TravelFeed curation.** \n This is most likely because we have detected plagiarism in one of your posts in the past. If you believe that this is a mistake, please contact us on the [Steemit Travellers Discord](https://discord.gg/jWWu73H). c \n Regards, TravelFeed"
# Comment for other languages
wronglangtext = "Hi @{}, \n Thank you for participating in the #travelfeed curated tag. To maintain a level of quality on the project we have certain criteria that must be met for participation. Please review the following: https://steemit.com/travelfeed/@travelfeed/how-to-participate-use-travelfeed-in-your-posts \n **We require at least 250 words in English, but your post seems to be in another language.** (The language of your post was automatically detected, if your post is in English, please ignore this message.) \n Thank you very much for your interest and we hope to read some great travel articles from you soon! \n Regards, TravelFeed"
# Define path for logging
logpath = 'posts.log'
### Configuration end

from beem import Steem
import os
from beem.blockchain import Blockchain
from beem.comment import Comment
from beem.account import Account
from beem.exceptions import ContentDoesNotExistsException
from bs4 import BeautifulSoup
from markdown import markdown
from langdetect import detect
import json
import datetime
import time
import re
import random
walletpw = os.environ.get('UNLOCK') #Wallet needs to be created in beem

def converter(object_):
    if isinstance(object_, datetime.datetime):
        return object_.__str__()

def stream_blockchain(starting_point):
    try:
        steem = Steem()
        steem.wallet.unlock(walletpw)
        account = Account(trackaccount, steem_instance=steem)
        blockchain = Blockchain()
        if not starting_point:
            try:
                props = steem.get_dynamic_global_properties()
                starting_point = props['last_irreversible_block_num']
            except:
                stream_blockchain(None)
        stream = map(Comment, blockchain.stream(start=starting_point, opNames=["comment"]))
        blacklist = account.get_mutings(raw_name_list=True)
        file = open(logpath, 'a+')
        print(time.strftime('%X')+" Info: Stream from blockchain started at block "+str(starting_point))
    except Exception as error:
        print(time.strftime('%X')+" Warning: Could not start blockchain stream. Switching nodes. "+repr(error))
        stream_blockchain(starting_point)
    while True:
        try:
            for post in stream:
                post.refresh()
                if post.is_main_post() and tracktag in post["tags"]:
                    author = post["author"]
                    postlink = "@"+author+"/"+post['permlink']
                    file.seek(0)
                    post_urls = file.read().splitlines()
                    commenttext = ""
                    if postlink in post_urls:
                        print(time.strftime('%X')+" Info: Ignoring updated post")
                        continue
                    elif author in whitelist:
                        print(time.strftime('%X')+" Info: Ignoring short post by whitelisted user @{}".format(author))
                        continue
                    elif author in blacklist: 
                        commenttext = blacklisttext
                        print(time.strftime('%X')+" Info: Detected post by blacklisted user @{}".format(author))
                    else:
                        try:
                            content = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', ''.join(BeautifulSoup(markdown(post["body"]), "html.parser").findAll(text=True)))
                            count = len(re.findall(r'\w+', content))
                            try:
                                lang = detect(content)
                            except:
                                lang = "en"
                            if not lang == "en":
                                commenttext = wronglangtext
                                print(time.strftime('%X')+" Info: Detected post by @{} who posted in {}".format(author, lang))
                            elif count < 250:
                                commenttext = shortposttext
                                print(time.strftime('%X')+" Info: Detected short post by @{} who posted with just {} words".format(author, count))
                            else:
                                print(time.strftime('%X')+" Info: Ignoring awesome post by @{}".format(author))
                        except Exception as error:
                            print(time.strftime('%X')+" Warning: Error during content processing "+repr(error))
                            continue
                    if not commenttext == "":
                        try:
                            post.reply(commenttext.format(author, count), author=postaccount)
                            print(time.strftime('%X')+" Success: I sucessfully left a comment for @{}".format(author))
                        except:
                            print(time.strftime('%X')+" Info: There was an error posting the comment, could be due to the 20 second limit on comments. I will try again.")
                            time.sleep(19)
                            try:
                                post.reply(commenttext.format(author, count), author=postaccount)
                                print(time.strftime('%X')+" Success: Cool, now it worked, I successfully left a comment for @{}!".format(author))
                            except:
                                print(time.strftime('%X')+" Warning: Nope, still an error, I could not levae a comment for (@{}) due to this error: ".format(author)+repr(error))
                                continue
                    file.write("\n"+postlink)
                    file.close()
                    file = open(logpath, 'a+')
        except ContentDoesNotExistsException:
            print(time.strftime('%X')+" Info: Skipping node error")
            continue
        except Exception as error:
            try:
                props = steem.get_dynamic_global_properties()
                starting_point = props['last_irreversible_block_num']
            except:
                starting_point = starting_point
            print(time.strftime('%X')+" Warning at block "+str(starting_point)+": "+repr(error))
            file.close()
            stream_blockchain(starting_point)

if __name__ == '__main__':
    print(time.strftime('%X')+" Info: Bot started")
    starting_point=None
    stream_blockchain(starting_point)
