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
def converter(object_):
    if isinstance(object_, datetime.datetime):
        return object_.__str__()

def stream_blockchain():
    steem = Steem(wif=steemPostingKey)
    blockchain = Blockchain()
    stream = map(Post, blockchain.stream(filter_by=['comment']))
    post_urls = []
    while True:
        try:
            for post in stream:
                if post.is_main_post() and "travel" in post["tags"]:
                    permlink = post['permlink']
                    if permlink in post_urls:
                        print(time.strftime('%X')+" Info: Ignoring updated post")
                    else:
                        post_urls.append(permlink)
                        author = post["author"]
                        html = markdown(post["body"])
                        soup = BeautifulSoup(html, "html.parser")
                        text = ''.join(soup.findAll(text=True))
                        remlink = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', text)
                        count = len(re.findall(r'\w+', remlink))
                        if count > 249:
                          print(time.strftime('%X')+" Success: There is a new awesome post by @{} who posted with {} words".format(author, count))
                        else:
                            commenttext = "Hey {}, I am a helpful word counting bot and just found your post while running a test. I wanted to let you know that I have counted **{} words** in your post"
                            try:
                                post.reply(commenttext.format(author, count), "", "jpphoto")
                                print(time.strftime('%X')+" Success: I detected a rule breaker and sucessfully left a comment for @{} since we require at least 250 words but I have only counted {} words in the post".format(author, count))              
                            except:
                                print(time.strftime('%X')+" Info: I detected a rule breaker but there was an error posting the comment, could be due to the 20 second limit on comments. I will try my best to not let him get away!")
                                time.sleep(19)
                                try:
                                    post.reply(commenttext.format(author, count), "", "jpphoto")
                                    print(time.strftime('%X')+" Success: Cool, now it worked, I successfully left a comment for @{}!".format(author)+repr(error))
                                except:
                                    print(time.strftime('%X')+" Warning: Nope, still an error, this rulebreaker (@{}) got away due to the error".format(author)+repr(error))
        except PostDoesNotExist:
            print(time.strftime('%X')+" Info: Skipping post")
            continue
        except Exception as error:
            print(time.strftime('%X')+" Warning: " repr(error))
            continue

if __name__ == '__main__':
    stream_blockchain()
