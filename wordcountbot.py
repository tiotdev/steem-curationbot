### Configuration start: Adjust these variables
## Setings for curatebot
# Account to track for blacklisted/muted users
trackaccount = 'travelfeed'
# Tag to search in
tracktag = 'travelfeed'
# Account to post the comments
postaccount = 'travelfeed-bot'
# List of whitelisted users who are allowed to post short posts
whitelist = ['travelfeed', 'tangofever']
# Comment for short posts 
shortposttext = "Hi @{}, \n Thank you for participating in the #travelfeed curated tag. To maintain a level of quality on the project we have certain criteria that must be met for participation. Please review the following: https://steemit.com/travelfeed/@travelfeed/how-to-participate-use-travelfeed-in-your-posts \n **We require at least 250 words, but your post has only {} words.** \n Thank you very much for your interest and we hope to read some great travel articles from you soon! \n Regards, @travelfeed"
# Comment for blacklisted users
blacklisttext = "Hi @{}, \n Thank you for participating in the #travelfeed curated tag. To maintain a level of quality on the project we have certain criteria that must be met for participation. Please review the following: https://steemit.com/travelfeed/@travelfeed/how-to-participate-use-travelfeed-in-your-posts \n **You are currently blacklisted from the TravelFeed curation.** \n This is most likely because we have detected plagiarism in one of your posts in the past. If you believe that this is a mistake, please contact us on the [Steemit Travellers Discord](https://discord.gg/jWWu73H). c \n Regards, @travelfeed"
# Comment for other languages
wronglangtext = "Hi @{}, \n Thank you for participating in the #travelfeed curated tag. To maintain a level of quality on the project we have certain criteria that must be met for participation. Please review the following: https://steemit.com/travelfeed/@travelfeed/how-to-participate-use-travelfeed-in-your-posts \n **We require at least 250 words in English, but your post seems to be in another language.** (The language of your post was automatically detected, if your post is in English, please ignore this message.) \n Thank you very much for your interest and we hope to read some great travel articles from you soon! \n Regards, @travelfeed"
# Define path for logging
logpath = 'posts.log'
## Settings for adbot
# Tag1 to search in (only occurence together tag 2)
adtag1 = 'travel'
# Tag2 to search in (only occurence together tag 1)
adtag2 = 'deutsch'
# Tag 3 to search in
adtag3 = 'reisen'
# Curated tag that can't be included
adignore = 'de-travelfeed'
# Define path for logging authors
autpath = 'author_list.log'
# Account to post the comments
adpostaccount = 'de-travelfeed'
# Comment for advertising
adtext = "Hey @{}, wusstest du schon, dass es jetzt einen eigenen Tag für Reiseposts auf Deutsch gibt? Die Verwendung des kurierten #de-travelfeed Tags belohnt täglich Autoren, die außergewöhnliche Reise-Artikel produzieren, mit Resteems und Upvotes (inklusive Upvotes von @travelfeed und über 50 Followern des TravelFeed Curation-Trails). Wir freuen uns darauf, deine nächsten Reiseposts in #de-travelfeed zu finden (Minimum 250 Wörter auf Deutsch)! \n Hier kannst du mehr über uns erfahren: https://steemit.com/de-travelfeed/@de-travelfeed/de-travelfeed-der-tag-fuer-deutschsprachige-reisende \n Für Englische Reiseposts, schau dir #travelfeed bzw. @travelfeed an! \n <center>[![Transparent-Discord-Travel.png](https://steemitimages.com/DQmQU6Zt9ifnhvTkB8YE8jq8t4AeLMUUQhKBkoyF8Zh4zrp/Transparent-Discord-Travel.png)](https://discord.gg/jWWu73H)</center>"
### Configuration end

from beem import Steem
import os
from beem.blockchain import Blockchain
from beem.comment import Comment
from beem.account import Account
from beem.exceptions import ContentDoesNotExistsException
from bs4 import BeautifulSoup
from markdown import markdown
from langdetect import detect_langs
import json
import datetime
import time
import re
import random
walletpw = os.environ.get('UNLOCK') #Wallet needs to be created in beem

def converter(object_):
    if isinstance(object_, datetime.datetime):
        return object_.__str__()

def is_eligible(text, n, lng):
    """
    Returns True if text contains at least n words in the specified lng language.
    """
    for language in detect_langs(text):
        if language.lang == lng:
            probability = language.prob
            word_count = len(text.split(" "))
            if probability * word_count > n:
                return True
            else:
                break
    return False

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
        adfile = open(autpath, 'a+')
        print(time.strftime('%X')+" Info: Stream from blockchain started at block "+str(starting_point))
    except Exception as error:
        print(time.strftime('%X')+" Warning: Could not start blockchain stream. Switching nodes. "+repr(error))
        stream_blockchain(starting_point)
    while True:
        try:
            for post in stream:
                post.refresh()
                tags = post["tags"]
                if post.is_main_post() and tracktag in tags:
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
                            count = len(content.split(" "))
                            if count < 250:
                                commenttext = shortposttext
                                print(time.strftime('%X')+" Info: Detected short post by @{} who posted with just {} words".format(author, count))
                            elif not is_eligible(content, 250, "en"):
                                commenttext = wronglangtext
                                print(time.strftime('%X')+" Info: Detected post by @{} who posted not in English".format(author))
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
                            except Exception as error:
                                print(time.strftime('%X')+" Warning: Nope, still an error, I could not levae a comment for (@{}) due to this error: ".format(author)+repr(error))
                                continue
                    file.write("\n"+postlink)
                    file.close()
                    file = open(logpath, 'a+')
                elif post.is_main_post() and ((adtag1 in tags and adtag2 in tags) or adtag3 in tags) and not adignore in tags:
                    author = post["author"]
                    adfile.seek(0)
                    author_list = adfile.readlines()
                    content = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', ''.join(BeautifulSoup(markdown(post["body"]), "html.parser").findAll(text=True)))
                    if is_eligible(content, 300, "de") and not author in author_list:
                        print(time.strftime('%X')+" Success: I detected a post by @{} eligable for an advertisement comment".format(author))
                        try:
                            post.reply(adtext.format(author), author=adpostaccount)
                            adfile.write("\n"+author)
                            print(time.strftime('%X')+" Success: I sucessfully left a comment for @{}".format(author))
                        except:
                            print(time.strftime('%X')+" Info: There was an error posting the comment, could be due to the 20 second limit on comments. I will try again.")
                            time.sleep(19)
                            try:
                                post.reply(adtext.format(author), author=adpostaccount)
                                adfile.write("\n"+author)
                                print(time.strftime('%X')+" Success: Cool, now it worked, I successfully left a comment for @{}!".format(author))
                            except Exception as error:
                                print(time.strftime('%X')+" Warning: Nope, still an error, I could not levae a comment for (@{}) due to this error: ".format(author)+repr(error))
                                continue
                        adfile.close()
                        adfile = open(autpath, 'a+')
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
            adfile.close()
            stream_blockchain(starting_point)

if __name__ == '__main__':
    print(time.strftime('%X')+" Info: Bot started")
    starting_point=None
    stream_blockchain(starting_point)