from steem import Steem
import os
steemPostingKey = os.environ.get('steemPostingKey')
from steem.blockchain import Blockchain
from steem.post import Post
import json
import datetime
import re
from bs4 import BeautifulSoup
from markdown import markdown

def converter(object_):
    if isinstance(object_, datetime.datetime):
        return object_.__str__()

def stream_blockchain():
    steem = Steem(wif=steemPostingKey)
    blockchain = Blockchain()
    stream = map(Post, blockchain.stream(filter_by=['comment']))
    while True:
        try:
            for post in stream:
                tags = post["tags"]
                if post.is_main_post() and "life" in tags:
                    author = post["author"]
                    body = post["body"]
                    html = markdown(body)
                    soup = BeautifulSoup(html, "html.parser")
                    text = ''.join(soup.findAll(text=True))
                    count = len(re.findall(r'\w+', text))
                    if count > 249:
                      print("There is a new awesome post by @{} who posted with {} words".format(author, count))
                    else:
                        try:
                            post.reply("Hey {}, I am a helpful word counting bot and just found your post while running a test. I wanted to let you know that I have counted **{} words** in your post".format(author, count), "", "jpphoto")
                            print("I detected a rule breaker and sucessfully left a comment for @{} since we require at least 250 words but I have only counted {} words in the post".format(author, count))                    
                        except assert_exception:
                            print("20 second limit problem")
                        except:
                            print("Error")
        except Exception as error:
            print(repr(error))
            continue

if __name__ == '__main__':
    stream_blockchain()
