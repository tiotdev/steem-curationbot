from beem import Steem
from beem.blockchain import Blockchain
from beem.comment import Comment
from beem.account import Account
from beem.exceptions import ContentDoesNotExistsExceptio
from beem.utils import construct_authorperm
from bs4 import BeautifulSoup
from markdown import markdown
from langdetect import detect_langs
from datetime import datetime, timedelta
import os, json, time, re, discord, asyncio

### Configuration start: Adjust these variables
## Setings for curatebot
# Account to track for blacklisted/muted users
trackaccount = 'travelfeed'
# Tag to search in
tracktag = 'life' #Todo: Replace testing tag with travelfeed
# Account to post the comments
postaccount = 'travelfeed-bot'
# List of curators
curatorlist = ['travelfeed', 'for91days', 'rimicane', 'guchtere', 'mrprofessor', 'jpphotography']
# List of whitelisted users who are allowed to post short posts
whitelist = ['travelfeed', 'tangofever', 'steemitworldmap', 'de-travelfeed', 'cyclefeed']
# Define path for logging
logpath = 'posts.log'
# Define path for block logging
blocklog = 'block.log'
# Tag1 to search in for ads
adtag1 = 'travel'
# Define path for logging authors advertised to
autpath = 'author_list.log'
# Comment for short posts 
shortposttext = "Hi @{}, \n Thank you for participating in the #travelfeed curated tag. To maintain a level of quality on the project we have certain criteria that must be met for participation. Please review the following: https://steemit.com/travelfeed/@travelfeed/how-to-participate-use-travelfeed-in-your-posts \n **We require at least 250 words, but your post has only {} words.** \n Thank you very much for your interest and we hope to read some great travel articles from you soon! \n Regards, @travelfeed"
# Comment for blacklisted users
blacklisttext = "Hi @{}, \n Thank you for participating in the #travelfeed curated tag. To maintain a level of quality on the project we have certain criteria that must be met for participation. Please review the following: https://steemit.com/travelfeed/@travelfeed/how-to-participate-use-travelfeed-in-your-posts \n **You are currently blacklisted from the TravelFeed curation.** \n This is most likely because we have detected plagiarism in one of your posts in the past. If you believe that this is a mistake, please contact us on the [Steemit Travellers Discord](https://discord.gg/jWWu73H). \n Regards, @travelfeed"
# Comment for other languages
wronglangtext = "Hi @{}, \n Thank you for participating in the #travelfeed curated tag. To maintain a level of quality on the project we have certain criteria that must be met for participation. Please review the following: https://steemit.com/travelfeed/@travelfeed/how-to-participate-use-travelfeed-in-your-posts \n We require at least 250 words **in English**. (The language of your post was automatically detected, if your English text is at least 250 words long, please ignore this message.) \n Thank you very much for your interest and we hope to read some great travel articles from you soon! \n Regards, @travelfeed"
#Honour text
honourtext = "Congratulations! Your high quality-travel content was selected by @travelfeed curator @{} and earned you a **partial** upvote. We love your hard work and hope to encourage you to continue to publish strong travel-related content. <br> Thank you for participating in #travelfeed! <center> [![TravelFeed](https://ipfs.busy.org/ipfs/QmZhLuw8WE6JMCYHD3EXn3MBa2CSCcygvfFqfXde5z3TLZ)](https://steemit.com/travelfeed/@travelfeed/introducing-travelfeed-featuring-steemit-s-best-travel-content) <br> **Learn more about our travel project on Steemit by clicking on the banner above and join our community on [Discord](https://discord.gg/jWWu73H)**.</center>"
#Resteem Text
resteemtext = "Congratulations! Your high quality-travel content was selected by @travelfeed curator @{} and earned you a reward, in form of a **100% upvote** and a **resteem**. Your work really stands out. Your article now has a chance to get curated and featured under the appropriate daily topic of our Travelfeed blog. Thank you for participating in #travelfeed! <br> <center>[![TravelFeed](https://ipfs.busy.org/ipfs/QmNTkoKQNzuQbQGbcZ1exTMjvxYUprdnVczxnvib9VUSqB)](https://steemit.com/travelfeed/@travelfeed/introducing-travelfeed-featuring-steemit-s-best-travel-content) <br> **Learn more about our travel project on Steemit by clicking on the banner above and join our community on [Discord](https://discord.gg/jWWu73H)**</center>"
### Configuration end

walletpw =  os.environ.get('UNLOCK') #Beem wallet passphrase must be set as environment variable
TOKEN = os.environ.get('TOKEN') #Discord secret token must be set as environment variable
client = discord.Client()

async def send_discord(msg, channel):
    """
    Sends the message msg to the Discord channel channel
    """
    if channel == "upvote":
        channelid = '489680471878402048'
    elif channel == "honour":
        channelid = '489680498575015937'
    elif channel == "feed":
        channelid = "489704683137531914"
    elif channel == "test":
        channelid = "489618210250031104"
    elif channel == "ad":
        channelid = "489781127838433281"
    else:
        channelid = '489680525389332490'
    await client.wait_until_ready()
    await client.send_message(client.get_channel(channelid), msg)

async def is_eligible(text, n, lng):
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

async def get_history(user):
    """
    Returns a string with votes received from travelfeed within the past 7 days
    """
    acc = Account("travelfeed")
    stop = datetime.utcnow() - timedelta(days=7)
    honours = {}
    resteems = {}
    for vote in acc.history_reverse(stop=stop, only_ops=["vote"]):
        if vote["voter"] == "travelfeed" and vote["weight"] == 5000:
            if vote["author"] not in honours:
                honours[vote["author"]]=1
            else:
                honours[vote["author"]]=honours[vote["author"]]+1
        elif vote["voter"] == "travelfeed" and vote["weight"] == 10000:
            if vote["author"] not in resteems:
                resteems[vote["author"]]=1
            else:
                resteems[vote["author"]]=resteems[vote["author"]]+1
    if user in resteems and user in honours:
        return "**"+str(resteems[user])+"** Resteems, **"+str(honours[user])+"** Honours"
    elif user in resteems:
        return "**"+str(resteems[user])+"** Resteems, **0** Honours"
    elif user in honours:
        return "**0** Resteems, **"+str(honours[user])+"** Honours"
    else:
        return "**0** Resteems, **0** Honours"

async def get_rewards(blockchain):
    """
    Scan blockchain for author rewards
    Todo: Filter out mentions, split the reward and send it out automatically
    """
    for reward in blockchain.stream(opNames=["author_reward"], only_virtual_ops=True):
        if reward["author"] == "travelfeed":
            print(time.strftime('%X')+" Info: Found reward")
            await client.loop.create_task(send_discord("Found author reward", "reward"))

@client.event
async def on_message(message):
    """
    Listens to custom Discord commands
    Todo: Add more commands
    """
    if message.content.startswith('!rewards'):
        msg = await client.loop.create_task(get_history("travelfeed"))
        await client.send_message(message.channel, msg)

@client.event
async def on_ready():
    print(time.strftime('%X')+" Info: Logged into Discord as "+client.user.name+" "+client.user.id)

async def stream_blockchain(stream, blacklist):
    file = open(logpath, 'a+')
    adfile = open(autpath, 'a+')
    for post in stream:
        try:
            post.refresh()
            tags = post["tags"]
            author = post["author"]
            postlink = construct_authorperm(author, post['permlink'])
            if post.is_comment() and author in curatorlist:
                """
                Upvotes and comments on the post if a curator uses the invocation command
                Todo: Replace testing commands / accounts with production values
                """
                parent = post.get_parent()
                parentlink = construct_authorperm(parent['author'], parent['permlink'])
                if "!tftest50" in post["body"]:
                    try:
                        parent.upvote(weight=50, voter="jpphoto")
                        await client.loop.create_task(send_discord("https://steemit.com/"+parentlink, "honour"))
                    except Exception as error:
                        print(time.strftime('%X')+" Warning: Could not vote on honour post "+error)
                        await client.loop.create_task(send_discord("Could not vote with 50% on https://steemit.com/"+parentlink, "error"))
                    await asyncio.sleep(5)
                    try:
                        parent.reply(honourtext.format(author), author="jpphoto")
                    except Exception as error:
                        print(time.strftime('%X')+" Warning: Could not comment on honour post "+error)
                        await client.loop.create_task(send_discord("Could not comment on https://steemit.com/"+parentlink, "error"))
                elif "!tftest100" in post["body"]:
                    try:
                        parent.upvote(weight=100, voter="jpphoto")
                        await client.loop.create_task(send_discord("https://steemit.com/"+parentlink, "upvote"))
                    except Exception as error:
                        print(time.strftime('%X')+" Warning: Could not vote on resteem post "+error)
                        await client.loop.create_task(send_discord("Could not vote with 100% on https://steemit.com/"+parentlink, "error"))
                        continue
                    await asyncio.sleep(5)
                    try:
                        parent.resteem(identifier=parentlink, account="jpphoto")
                    except Exception as error:
                        print(time.strftime('%X')+" Warning: Could not resteem post "+error)
                        await client.loop.create_task(send_discord("Could not resteem https://steemit.com/"+parentlink, "error"))
                    await asyncio.sleep(5)
                    try:
                        parent.reply(resteemtext.format(author), author="jpphoto")
                    except Exception as error:
                        print(time.strftime('%X')+" Warning: Could not comment on resteem post "+error)
                        await client.loop.create_task(send_discord("Could not comment on https://steemit.com/"+parentlink, "error"))
            elif post.is_main_post() and tracktag in tags and not author in whitelist:
                """
                Checks post in #travelfeed
                """
                file.seek(0)
                post_urls = file.read().splitlines()
                commenttext = ""
                if postlink in post_urls:
                    print(time.strftime('%X')+" Info: Ignoring updated post")
                    continue
                elif author in blacklist: 
                    commenttext = blacklisttext
                    print(time.strftime('%X')+" Info: Detected post by blacklisted user @{}".format(author))
                else:
                    try:
                        content = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', ''.join(BeautifulSoup(markdown(post["body"]), "html.parser").findAll(text=True)))
                        count = len(content.split(" "))
                        check_eligible = await client.loop.create_task(is_eligible(content, 225, "en"))
                        if count < 240:
                            commenttext = shortposttext
                            print(time.strftime('%X')+" Info: Detected short post by @{} who posted with just {} words".format(author, count))
                        elif check_eligible == False:
                            commenttext = wronglangtext
                            print(time.strftime('%X')+" Info: Detected post by @{} who posted not in English".format(author))
                        else:
                            print(time.strftime('%X')+" Info: Ignoring awesome post by @{}".format(author))
                            history = await client.loop.create_task(get_history(author))
                            msg = history+". "+str(count)+" words. https://steemit.com/"+postlink
                            await client.loop.create_task(send_discord(msg, "feed"))
                    except Exception as error:
                        print(time.strftime('%X')+" Warning: Error during content processing "+repr(error))
                        continue
                if not commenttext == "":
                    try:
                        # post.reply(commenttext.format(author, count), author=postaccount) #commented out for testing
                        print(time.strftime('%X')+" Success: I sucessfully left a comment for @{}".format(author))
                    except:
                        print(time.strftime('%X')+" Warning: There was an error posting the comment.")
                        await client.loop.create_task(send_discord("Could not leave a comment for bad post https://steemit.com/"+postlink, "error"))
                        continue
                file.write("\n"+postlink)
                file.close()
                file = open(logpath, 'a+')
            elif post.is_main_post() and (adtag1 in tags) and not tracktag in tags:
                """
                Checks if post is in #travel an eligable for advertisement
                """
                content = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', ''.join(BeautifulSoup(markdown(post["body"]), "html.parser").findAll(text=True)))
                if await is_eligible(content, 400, "en"):
                    adfile.seek(0)
                    author_list = adfile.read().splitlines()
                    if not author in author_list:
                        print(time.strftime('%X')+" Success: I detected a post by @{} eligable for an advertisement comment".format(author))
                        try:
                            adfile.write("\n"+author)
                            await client.loop.create_task(send_discord("https://steemit.com/"+postlink, "ad"))
                            print(time.strftime('%X')+" Success: Found an advertisement post by @{}".format(author))
                        except:
                            print(time.strftime('%X')+" Warning: Could not promote advertisement post by @{}".format(author))
                        adfile.close()
                        adfile = open(autpath, 'a+')
            elif author == trackaccount or author == postaccount:
                """
                Upvotes and/or resteems relevant posts/comments by travelfeed accounts
                """
                content = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', ''.join(BeautifulSoup(markdown(post["body"]), "html.parser").findAll(text=True)))
                count = len(content.split(" "))
                if count > 20:
                    try:
                        post.upvote(weight=55, voter=postaccount)
                    except:
                        print(time.strftime('%X')+" Warning: Could not autovote on comment/post")
                    if author == trackaccount and post.is_main_post():
                        try:
                            post.resteem(identifier=postlink, account=postaccount)
                            print(time.strftime('%X')+" Info: Resteem successful")
                        except:
                            print(time.strftime('%X')+" Warning: Could not resteem")
                            await client.loop.create_task(send_discord("Could not resteem our curation post https://steemit.com/"+postlink, "error"))
        except:
            continue

async def start_blockchain(starting_point):
    "Starts the Blockchain Stream"
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
                client.loop.create_task(start_blockchain(None))
        stream = map(Comment, blockchain.stream(start=starting_point, opNames=["comment"]))
        blacklist = account.get_mutings(raw_name_list=True)
        print(time.strftime('%X')+" Info: Stream from blockchain started at block "+str(starting_point))
        await client.loop.create_task(stream_blockchain(stream, blacklist))
        await client.loop.create_task(get_rewards(blockchain))
    except Exception as error:
        print(time.strftime('%X')+" Warning: Could not start blockchain stream "+repr(error))
        client.loop.create_task(start_blockchain(starting_point))

def handle_exit():
    print(time.strftime('%X')+ " Info: Handling error")
    client.loop.run_until_complete(client.logout())
    for t in asyncio.Task.all_tasks(loop=client.loop):
        if t.done():
            t.exception()
            continue
        t.cancel()
        try:
            client.loop.run_until_complete(asyncio.wait_for(t, 5, loop=client.loop))
            t.exception()
        except asyncio.InvalidStateError:
            pass
        except asyncio.TimeoutError:
            pass
        except asyncio.CancelledError:
            pass

if __name__ == '__main__':
    """
    Starting the bot. A custom starting block can be defined in the blocklog file.
    """
    try:
        blockfile = open(blocklog, 'r')
        starting_point = blockfile.read()
        blockfile.close()
        print(time.strftime('%X')+" Info: Bot started from block "+starting_point)
    except:
        starting_point = None
        print(time.strftime('%X')+" Info: Bot started from current block")
    while True:
        """
        Todo: Better exception handling to make sure that no Blocks are missed
        """
        if starting_point is None:
            try:
                props = Steem().get_dynamic_global_properties()
                starting_point = props['last_irreversible_block_num']
            except:
                starting_point = starting_point
        client.loop.create_task(start_blockchain(starting_point))
        try:
            client.loop.run_until_complete(client.start(TOKEN))
        except KeyboardInterrupt:
            handle_exit()
            client.loop.close()
            print(time.strftime('%X')+" Info: Bot ended")
            break
        except SystemExit:
            handle_exit()
        except:
            print(time.strftime('%X')+" Info: Bot restarting")
            client = discord.Client(loop=client.loop)
        print(time.strftime('%X')+" Info: Bot restarting")
        client = discord.Client(loop=client.loop)