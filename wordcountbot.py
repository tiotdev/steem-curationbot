from beem import Steem
from beem.blockchain import Blockchain
from beem.comment import Comment
from beem.account import Account
from beem.nodelist import NodeList
from beem.memo import Memo
from beem.instance import set_shared_steem_instance
from beem.exceptions import ContentDoesNotExistsException
from beem.utils import construct_authorperm, resolve_authorperm
from bs4 import BeautifulSoup
from markdown import markdown
from langdetect import detect_langs
from datetime import datetime, timedelta
from discord.ext import commands
from discord.ext.commands import Bot
import os, re, discord, asyncio, logging, json, requests

"""
Configuration: Make adjustments here
"""
# Account to track for blacklisted/muted users
trackaccount = 'travelfeed'
# Tag to search in
tracktag = 'travelfeed'
# Account to post the comments
postaccount = 'jpphoto' #todo: change to travelfeed when testing completed
# List of curators
curatorlist = ['travelfeed', 'for91days', 'rimicane', 'guchtere', 'mrprofessor', 'jpphotography']
# List of whitelisted users who are allowed to post short posts
whitelist = ['travelfeed', 'tangofever', 'steemitworldmap', 'de-travelfeed', 'cyclefeed']
# Define path for logging
logpath = 'bot.log'
# Define path for logging
postlogpath = 'posts.log'
# Define path for block logging
blocklog = 'block.log'
# Tag to search in for ads
adtag1 = 'travel'
# Define path for logging authors advertised to
autpath = 'author_list.log'
# Comment for short posts 
shortposttext = "Hi @{}, \n Thank you for participating in the #travelfeed curated tag. To maintain a level of quality on the project we have certain criteria that must be met for participation. Please review the following: https://steemit.com/travelfeed/@travelfeed/how-to-participate-use-travelfeed-in-your-posts \n **We require at least 250 words, but your post has only {} words.** \n Thank you very much for your interest and we hope to read some great travel articles from you soon! \n If you believe that you have received this comment by mistake or have updated your post, please reply to this comment with <code>!tfreview</code>. For further questions, please contact us at the Steemit Travellers Discord](https://discord.gg/jWWu73H). \n Regards, @travelfeed"
# Comment for blacklisted users
blacklisttext = "Hi @{}, \n Thank you for participating in the #travelfeed curated tag. To maintain a level of quality on the project we have certain criteria that must be met for participation. Please review the following: https://steemit.com/travelfeed/@travelfeed/how-to-participate-use-travelfeed-in-your-posts \n **You are currently blacklisted from the TravelFeed curation.** \n This is most likely because we have detected plagiarism in one of your posts in the past. If you believe that this is a mistake, please contact us on the [Steemit Travellers Discord](https://discord.gg/jWWu73H). \n Regards, @travelfeed"
# Comment for other languages
wronglangtext = "Hi @{}, \n Thank you for participating in the #travelfeed curated tag. To maintain a level of quality on the project we have certain criteria that must be met for participation. Please review the following: https://steemit.com/travelfeed/@travelfeed/how-to-participate-use-travelfeed-in-your-posts \n We require at least 250 words **in English**. \n Thank you very much for your interest and we hope to read some great travel articles from you soon! \n The language of your post was automatically detected, if your English text is at least 250 words long or you have updated your post, please reply to this comment with <code>!tfreview</code> for it to be considered for curation. For further questions, please contact us at the Steemit Travellers Discord](https://discord.gg/jWWu73H). \n Regards, @travelfeed"
#Honour text
honourtext = "Congratulations! Your high quality-travel content was selected by @travelfeed curator @{} and earned you a **partial** upvote. We love your hard work and hope to encourage you to continue to publish strong travel-related content. <br> Thank you for participating in #travelfeed! <center> [![TravelFeed](https://ipfs.busy.org/ipfs/QmZhLuw8WE6JMCYHD3EXn3MBa2CSCcygvfFqfXde5z3TLZ)](https://steemit.com/travelfeed/@travelfeed/introducing-travelfeed-featuring-steemit-s-best-travel-content) <br> **Learn more about our travel project on Steemit by clicking on the banner above and join our community on [Discord](https://discord.gg/jWWu73H)**.</center>"
#Resteem Text
resteemtext = "Congratulations! Your high quality-travel content was selected by @travelfeed curator @{} and earned you a reward, in form of a **100% upvote** and a **resteem**. Your work really stands out. Your article now has a chance to get curated and featured under the appropriate daily topic of our Travelfeed blog. Thank you for participating in #travelfeed! <br> <center>[![TravelFeed](https://ipfs.busy.org/ipfs/QmNTkoKQNzuQbQGbcZ1exTMjvxYUprdnVczxnvib9VUSqB)](https://steemit.com/travelfeed/@travelfeed/introducing-travelfeed-featuring-steemit-s-best-travel-content) <br> **Learn more about our travel project on Steemit by clicking on the banner above and join our community on [Discord](https://discord.gg/jWWu73H)**</center>"
#Advote Text
advotetext = "Great read! Your high quality-travel content was selected by @travelfeed curator @{}. We just gave you a small upvote together with over 60 followers of the @travelfeed curation trail. <br> Have you heard of @travelfeed? Using the #travelfeed tag rewards authors and content creators who produce exceptional travel related articles, so be sure use our tag to get much bigger upvotes, resteems and be featured in our curation posts! <br> <center>[![TravelFeed](https://ipfs.busy.org/ipfs/QmNTkoKQNzuQbQGbcZ1exTMjvxYUprdnVczxnvib9VUSqB)](https://steemit.com/travelfeed/@travelfeed/introducing-travelfeed-featuring-steemit-s-best-travel-content) <br> **Learn more about our travel project on Steemit by clicking on the banner above and join our community on [Discord](https://discord.gg/jWWu73H)**</center>"
#Manual comment text for short posts
manualshorttext = "Hi @{}, \n Thank you for participating in the #travelfeed curated tag. To maintain a level of quality on the project we have certain criteria that must be met for participation. Please review the following: https://steemit.com/travelfeed/@travelfeed/how-to-participate-use-travelfeed-in-your-posts \n **We require at least 250 words.** \n Thank you very much for your interest and we hope to read some great travel articles from you soon! \n If you believe that you have received this comment by mistake or have updated your post, please reply to this comment with <code>!tfreview</code>. For further questions, please contact us at the Steemit Travellers Discord](https://discord.gg/jWWu73H). \n Regards, @travelfeed"
#Manual comment text for posts that are not in English
manuallangtext = "Hi @{}, \n Thank you for participating in the #travelfeed curated tag. To maintain a level of quality on the project we have certain criteria that must be met for participation. Please review the following: https://steemit.com/travelfeed/@travelfeed/how-to-participate-use-travelfeed-in-your-posts \n We require at least 250 words **in English**. \n Thank you very much for your interest and we hope to read some great travel articles from you soon! \n If you believe that you have received this comment by mistake or have updated your post, please reply to this comment with <code>!tfreview</code>. For further questions, please contact us at the Steemit Travellers Discord](https://discord.gg/jWWu73H). \n Regards, @travelfeed"
#Copyright text
copyrighttext = "Hi @{}, \n Thank you for participating in the #travelfeed curated tag. To maintain a level of quality on the project we have certain criteria that must be met for participation. Please review the following: https://steemit.com/travelfeed/@travelfeed/how-to-participate-use-travelfeed-in-your-posts \n We require **proper sourcing** for all media and text that is not your own. \n If you have updated your post with sources, please reply to this comment with <code>!tfreview</code>. For further questions, please contact us at the Steemit Travellers Discord](https://discord.gg/jWWu73H). \n Thank you very much for your interest and we hope to read some great travel articles from you soon! \n Regards, @travelfeed"

"""
Steemit functions
"""
async def get_history(user):
    """
    Returns the number of votes received the user received from the curation account in the past 7 days
    """
    if user in resteems and user in honours:
        return "**"+str(resteems[user])+"** Resteems, **"+str(honours[user])+"** Honours"
    elif user in resteems:
        return "**"+str(resteems[user])+"** Resteems, **0** Honours"
    elif user in honours:
        return "**0** Resteems, **"+str(honours[user])+"** Honours"
    else:
        return "**0** Resteems, **0** Honours"

async def get_ua(username):
    """
    Get Steem-UA score
    """
    user = Account(postaccount)
    steem_ua = Account("steem-ua")
    memo = Memo(user, steem_ua)
    enc_user = memo.encrypt(postaccount)["message"]
    start_account = username
    url = "https://steem-ua.com:5000/rpc"
    request = {
         "jsonrpc": "2.0",
         "id": 0,
         "method": "get_sorted_by_ua",
         "params": {"user": user["name"], "encrypted_user": enc_user, "start_account": start_account, "limit": 1}
         }
    r = requests.post(url, data=json.dumps(request))
    ua_query_result = r.json()
    print(ua_query_result)
    ua_result = ua_query_result['result']['account']['ua']
    print(ua_result)
    return ua_result

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


"""
Steem background tasks
"""
async def stream_history():
    """
    Background task: Gets votes received from travelfeed within the past 7 days every 12 hours
    """
    acc = Account("travelfeed")
    stop = datetime.utcnow() - timedelta(days=7)
    while True:
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
        logger.info("Got history from Blockchain")
        await asyncio.sleep(43200) #sleep 12 hours
        
async def stream_rewards():
    """
    Background task: Scans blockchain for travelfeed author rewards, extracts mentions and determines which reward should be sent to mentioned users
    Todo when code has been tested: Send out rewards automatically
    """
    while True:
        for reward in blockchain.stream(opNames=["author_reward"], only_virtual_ops=True):
            await asyncio.sleep(0.001)
            if reward["author"] == "travelfeed":
                steemreward = float(re.sub("( STEEM)",'',reward['steem_payout'],re.IGNORECASE|re.DOTALL))
                postlink = construct_authorperm(reward["author"], reward["permlink"])
                logger.info("Found reward")
                postlink = "@travelfeed/europe-weeklyround-up28-zvgo8x02og" #todo remove testing
                post = Comment(postlink)
                if not "Weekly Round-Up" in post["title"]:
                    logger.info("Ignoring reward for other post")
                    break
                elif "TRAVELFEED WEEKLY ROUND-UP" in post["title"]:
                    logger.info("Ignoring reward for weekly round-up")
                    break
                myre = re.compile(r"@([a-zA-Z0-9-]+)<")
                mentions = list(set(myre.findall(post["body"])))
                for curator in curatorlist:
                    if curator in mentions:
                        mentions.remove(curator)
                if "steemitworldmap" in mentions:
                    mentions.remove('steemitworldmap')
                mentionsnr = len(mentions)
                if mentionsnr == 0:
                    payout = 0
                else:
                    payout = round((1/(mentionsnr*2)*steemreward), 3)
                memo = "Congratulations! Here comes your reward for being featured in "+post["title"]+" https://steemit.com/travelfeed/"+postlink
                await loop.create_task(send_discord("Found author reward "+str(steemreward)+" STEEM for post https://steemit.com/"+postlink+" split between the users "+str(mentions)+" who will each receive "+str(payout)+" STEEM. Memo: "+memo, "reward"))

async def stream_comments(stream):
    """
    Stream comment objects from Blockchain, react to relevant ones
    """
    blacklist = Account(trackaccount).get_mutings(raw_name_list=True)
    file = open(postlogpath, 'a+')
    adfile = open(autpath, 'a+')
    for post in stream:
        try:
            post.refresh()
            await asyncio.sleep(0.001)
            tags = post["tags"]
            author = post["author"]
            body = post["body"]
            postlink = construct_authorperm(author, post['permlink'])
            if post.is_comment():
                """
                Upvotes and comments on the post if a curator uses the invocation command
                """
                if author in curatorlist:
                    parent = post.get_parent()
                    parentlink = construct_authorperm(parent['author'], parent['permlink'])
                    if "!tf50" in body:
                        try:
                            parent.upvote(weight=50, voter=postaccount)
                            await loop.create_task(send_discord("https://steemit.com/"+parentlink, "honour"))
                        except Exception as error:
                            logger.warning("Could not vote with 50% "+repr(error))
                            await loop.create_task(send_discord("Could not vote with 50% on https://steemit.com/"+parentlink, "error"))
                        await asyncio.sleep(3)
                        try:
                            parent.reply(honourtext.format(author), author=postaccount)
                        except Exception as error:
                            logger.warning("Could not comment on honour post "+repr(error))
                            try:
                                await loop.create_task(send_discord("Could not comment on honour post https://steemit.com/"+parentlink, "error"))
                            except:
                                logger.warning("Could not send message to Discord")
                    elif "!tf100" in body:
                        try:
                            parent.upvote(weight=100, voter=postaccount)
                            await loop.create_task(send_discord("https://steemit.com/"+parentlink, "upvote"))
                        except Exception as error:
                            logger.warning("Could not vote with 100% "+repr(error))
                            try:
                                await loop.create_task(send_discord("Could not vote with 100% on https://steemit.com/"+parentlink, "error"))
                            except:
                                logger.warning("Could not send message to Discord")
                            continue
                        await asyncio.sleep(3)
                        try:
                            parent.resteem(identifier=parentlink, account=postaccount)
                        except Exception as error:
                            logger.warning("Could not resteem post "+error)
                            try:
                                await loop.create_task(send_discord("Could not resteem https://steemit.com/"+parentlink, "error"))
                            except:
                                logger.warning("Could not send message to Discord")
                        await asyncio.sleep(3)
                        try:
                            parent.reply(resteemtext.format(author), author=postaccount)
                        except Exception as error:
                            logger.warning("Could not comment on resteem post "+repr(error))
                            try:
                                await loop.create_task(send_discord("Could not comment on resteem post https://steemit.com/"+parentlink, "error"))
                            except:
                                logger.warning("Could not send message to Discord")
                    elif "!coop100" in body:
                        try:
                            parent.upvote(weight=100, voter=postaccount)
                            await loop.create_task(send_discord("100% cooperation upvote https://steemit.com/"+parentlink, "othervotes"))
                        except Exception as error:
                            logger.warning("Could not vote on cooperation post "+repr(error))
                            try:
                                await loop.create_task(send_discord("Could not vote with 100% on cooperation post https://steemit.com/"+parentlink, "error"))
                            except:
                                logger.warning("Could not send message to Discord")
                            continue
                    elif "!ad10" in body:
                        try:
                            parent.upvote(weight=10, voter=postaccount)
                            await loop.create_task(send_discord("10% ad upvote https://steemit.com/"+parentlink, "othervotes"))
                        except Exception as error:
                            logger.warning("Could not vote with 10% on ad post "+repr(error))
                            try:
                                await loop.create_task(send_discord("Could not vote with 10% on ad post https://steemit.com/"+parentlink, "error"))
                            except:
                                logger.warning("Could not send message to Discord")
                            continue      
                elif "!tfreview" in body:
                    """
                    Users targeted by bot comments can have their posts manually reviewed
                    """
                    if post.parent_author == postaccount:
                        parent = post.get_parent()
                        parentlink = construct_authorperm(parent['author'], parent['permlink'])
                        logger.info("@{} requests manual review ".format(author))
                        history = await loop.create_task(get_history(author))
                        try:
                            await loop.create_task(send_discord("Author requests manual review: "+history, "feed"))
                            await loop.create_task(send_discord("https://steemit.com/"+parentlink, "feed"))
                        except:
                            logger.warning("Could not send message to Discord")
            elif post.is_main_post() and tracktag in tags and not author in whitelist:
                """
                Checks post in #travelfeed
                """
                file.seek(0)
                post_urls = file.read().splitlines()
                commenttext = ""
                if postlink in post_urls:
                    logger.info("Ignoring updated post")
                    continue
                elif author in blacklist: 
                    commenttext = blacklisttext
                    logger.info("Detected post by blacklisted user @{}".format(author))
                else:
                    try:
                        content = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', ''.join(BeautifulSoup(markdown(body), "html.parser").findAll(text=True)))
                        count = len(content.split(" "))
                        check_eligible = await loop.create_task(is_eligible(content, 225, "en"))
                        if count < 240:
                            commenttext = shortposttext
                            logger.info("Detected short post by @{} who posted with just {} words".format(author, count))
                        elif check_eligible == False:
                            commenttext = wronglangtext
                            logger.info("Detected post by @{} who posted not in English".format(author))
                        else:
                            logger.info("Ignoring awesome post by @{}".format(author))
                            history = await loop.create_task(get_history(author))
                            msg = history+". "+str(count)+" words."
                            try:
                                await loop.create_task(send_discord(msg, "feed"))
                                await loop.create_task(send_discord("https://steemit.com/"+postlink, "feed"))
                            except:
                                logger.warning("Could not send message to Discord")
                    except Exception as error:
                        logger.warning("Error during content processing "+repr(error))
                        continue
                if not commenttext == "":
                    try:
                        post.reply(commenttext.format(author, count), author=postaccount)
                        logger.info("I sucessfully left a comment for @{}".format(author))
                    except:
                        logger.warning("There was an error posting the comment.")
                        try:
                            await loop.create_task(send_discord("Could not leave a comment for bad post https://steemit.com/"+postlink, "error"))
                        except:
                            logger.warning("Could not send message to Discord")
                        continue
                file.write("\n"+postlink)
                file.close()
                file = open(postlogpath, 'a+')
            elif post.is_main_post() and (adtag1 in tags) and not tracktag in tags:
                """
                Checks if post is in #adtag1 and eligable for advertisement
                """
                content = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', ''.join(BeautifulSoup(markdown(body), "html.parser").findAll(text=True)))
                if await is_eligible(content, 400, "en"):
                    adfile.seek(0)
                    author_list = adfile.read().splitlines()
                    if not author in author_list:
                        logger.info("I detected a post by @{} eligable for an advertisement comment".format(author))
                        try:
                            adfile.write("\n"+author)
                            await loop.create_task(send_discord("https://steemit.com/"+postlink, "ad"))
                            logger.info("Found an advertisement post by @{}".format(author))
                        except:
                            logger.warning("Could not promote advertisement post by @{}".format(author))
                        adfile.close()
                        adfile = open(autpath, 'a+')
            elif author == trackaccount or author == postaccount:
                """
                Upvotes and/or resteems relevant posts/comments by travelfeed accounts
                """
                content = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', ''.join(BeautifulSoup(markdown(body), "html.parser").findAll(text=True)))
                count = len(content.split(" "))
                if count > 20:
                    try:
                        post.upvote(weight=55, voter=postaccount)
                    except:
                        logger.warning("Could not autovote on comment/post")
                    if author == trackaccount and post.is_main_post():
                        try:
                            post.resteem(identifier=postlink, account=postaccount)
                            logger.info("Resteem successful")
                        except:
                            logger.warning("Could not resteem")
                            try:
                                await loop.create_task(send_discord("Could not resteem our curation post https://steemit.com/"+postlink, "error"))
                            except:
                                logger.warning("Could not send message to Discord")
        except:
            continue

async def start_blockchain(starting_point):
    """
    Starts the Blockchain Stream
    """
    try:
        if not starting_point:
            try:
                props = steem.get_dynamic_global_properties()
                starting_point = props['last_irreversible_block_num']
            except:
                loop.create_task(start_blockchain(None))
        stream = map(Comment, blockchain.stream(start=starting_point, opNames=["comment"]))
        logger.info("Stream from blockchain started at block "+str(starting_point))
        await loop.create_task(stream_comments(stream))
    except Exception as error:
        logger.warning("Could not start blockchain stream "+repr(error))
        loop.create_task(start_blockchain(starting_point))

"""
Discord functions
"""
async def send_discord(msg, cnl):
    """
    Sends the message msg to the Discord channel cnl
    """
    if cnl == "upvote":
        channelid = '489680471878402048'
    elif cnl == "honour":
        channelid = '489680498575015937'
    elif cnl == "feed":
        channelid = "489704683137531914"
    elif cnl == "test":
        channelid = "489618210250031104"
    elif cnl == "ad":
        channelid = "489781127838433281"
    elif cnl == "reward":
        channelid = "490396153146376194"
    else:
        channelid = '489680525389332490'
    await bot.wait_until_ready()
    await bot.send_message(bot.get_channel(channelid), msg)

async def keepalive():
    """
    Ping Discord every minute to prevent connection loss
    """
    await bot.wait_until_ready()
    await bot.change_presence(game=discord.Game(name='TravelFeed.io'))
    while True:
        try:
            await send_discord("Bot is running", "test") #todo: Find better way to ping
        except:
            logger.warning("Could not ping Discord")
        await asyncio.sleep(59)

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    logger.info("Login to Discord successful")

@bot.event
async def on_reaction_add(reaction, user):
    """
    Initiate curation process by adding a reaction
    """
    curator = re.sub('\d|\W|(TravelFeed)','',str(user),re.IGNORECASE|re.DOTALL)
    if reaction.message.content.startswith('http') and curator in curatorlist:
        if reaction.emoji == '🌐':
            author, permlink = resolve_authorperm(reaction.message.content)
            post = Comment(construct_authorperm(author, permlink))
            try:
                post.upvote(weight=50, voter=postaccount)
                await loop.create_task(send_discord(reaction.message.content, "honour"))
                await bot.add_reaction(reaction.message, "🆗")
            except Exception as error:
                logger.warning("Could not vote with 50% on "+repr(error))
                await loop.create_task(send_discord("Could not vote with 50% on "+reaction.message.content, "error"))
                await bot.add_reaction(reaction.message, "🆘")
            await asyncio.sleep(3)
            try:
                post.reply(honourtext.format(curator), author=postaccount)
                await bot.add_reaction(reaction.message, "🔤")
            except Exception as error:
                logger.warning("Could not comment on honour post "+repr(error))
                await loop.create_task(send_discord("Could not comment on honour post "+reaction.message.content, "error"))
                await bot.add_reaction(reaction.message, "🆘")
        elif reaction.emoji == '🌍':
            author, permlink = resolve_authorperm(reaction.message.content)
            postlink = construct_authorperm(author, permlink)
            post = Comment(postlink)
            try:
                post.upvote(weight=100, voter=postaccount)
                await bot.add_reaction(reaction.message, "🆙")
            except Exception as error:
                logger.warning("Could not vote with 100% on "+repr(error))
                try:
                    await loop.create_task(send_discord("Could not vote with 100% on "+reaction.message.content, "error"))
                    await bot.add_reaction(reaction.message, "🆘")
                except:
                    logger.warning("Could not send message to Discord")
            await asyncio.sleep(3)
            try:
                post.resteem(identifier=postlink, account=postaccount)
                await bot.add_reaction(reaction.message, "🔄")
            except Exception as error:
                logger.warning("Could not resteem post "+repr(error))
                try:
                    await loop.create_task(send_discord("Could not resteem "+reaction.message.content, "error"))
                    await bot.add_reaction(reaction.message, "🆘")
                except:
                    logger.warning("Could not send message to Discord")
            await asyncio.sleep(3)
            try:
                post.reply(resteemtext.format(curator), author=postaccount)
                await bot.add_reaction(reaction.message, "🔤")
            except Exception as error:
                logger.warning("Could not comment on resteem post "+repr(error))
                try:
                    await loop.create_task(send_discord("Could not comment on resteem post "+reaction.message.content, "error"))
                    await bot.add_reaction(reaction.message, "🆘")
                except:
                    logger.warning("Could not send message to Discord")
        elif reaction.emoji == '👥':
            author, permlink = resolve_authorperm(reaction.message.content)
            postlink = construct_authorperm(author, permlink)
            post = Comment(postlink)
            try:
                post.upvote(weight=100, voter=postaccount)
                await bot.add_reaction(reaction.message, "🚻")
            except Exception as error:
                logger.warning("Could not vote with 100% on "+repr(error))
                try:
                    await loop.create_task(send_discord("Could not vote with 100% on "+reaction.message.content, "error"))
                    await bot.add_reaction(reaction.message, "🆘")
                except:
                    logger.warning("Could not send message to Discord")
        elif reaction.emoji == '👋':
            author, permlink = resolve_authorperm(reaction.message.content)
            postlink = construct_authorperm(author, permlink)
            post = Comment(postlink)
            try:
                post.upvote(weight=10, voter=postaccount)
                await bot.add_reaction(reaction.message, "🔟")
            except Exception as error:
                logger.warning("Could not vote with 10% on "+repr(error))
                try:
                    await loop.create_task(send_discord("Could not vote with 10% on "+reaction.message.content, "error"))
                    await bot.add_reaction(reaction.message, "🆘")
                except:
                    logger.warning("Could not send message to Discord")
            await asyncio.sleep(3)
            try:
                post.reply(advotetext.format(curator), author=postaccount)
                await bot.add_reaction(reaction.message, "🔤")
            except Exception as error:
                logger.warning("Could not comment on ad post "+repr(error))
                try:
                    await loop.create_task(send_discord("Could not comment on ad post "+reaction.message.content, "error"))
                    await bot.add_reaction(reaction.message, "🆘")
                except:
                    logger.warning("Could not send message to Discord")
        elif reaction.emoji == '📏':
            author, permlink = resolve_authorperm(reaction.message.content)
            postlink = construct_authorperm(author, permlink)
            post = Comment(postlink)
            try: 
                post.reply(manualshorttext.format(post["author"]), author=postaccount)
                await bot.add_reaction(reaction.message, "🔤")
            except Exception as error:
                logger.warning("Could not comment on short post "+repr(error))
                try:   
                    await loop.create_task(send_discord("Could not comment on short post "+reaction.message.content, "error"))
                    await bot.add_reaction(reaction.message, "🆘")
                except:
                    logger.warning("Could not send message to Discord")
        elif reaction.emoji == '🇬🇧':
            author, permlink = resolve_authorperm(reaction.message.content)
            postlink = construct_authorperm(author, permlink)
            post = Comment(postlink)
            try: 
                post.reply(manuallangtext.format(post["author"]), author=postaccount)
                await bot.add_reaction(reaction.message, "🔤")
            except Exception as error:
                logger.warning("Could not comment on non-English post "+repr(error))
                try:
                    await loop.create_task(send_discord("Could not comment on non-English post "+reaction.message.content, "error"))
                    await bot.add_reaction(reaction.message, "🆘")
                except:
                    logger.warning("Could not send message to Discord")
        elif reaction.emoji == '📝':
            author, permlink = resolve_authorperm(reaction.message.content)
            postlink = construct_authorperm(author, permlink)
            post = Comment(postlink)
            try: 
                post.reply(copyrighttext.format(post["author"]), author=postaccount)
                await bot.add_reaction(reaction.message, "🔤")
            except Exception as error:
                logger.warning("Could not comment on copyright post "+repr(error))
                try:
                    await loop.create_task(send_discord("Could not comment on copyright post "+reaction.message.content, "error"))
                    await bot.add_reaction(reaction.message, "🆘")
                except:
                    logger.warning("Could not send message to Discord")

"""
Initiate curation process by using Discord commands
"""
@bot.command(pass_context=True)
async def tf50(ctx, link):
    curator = re.sub('\d|\W|(TravelFeed)','',str(ctx.message.author),re.IGNORECASE|re.DOTALL)
    if curator in curatorlist:
        author, permlink = resolve_authorperm(link)
        post = Comment(construct_authorperm(author, permlink))
        try:
            post.upvote(weight=50, voter=postaccount)
            await loop.create_task(send_discord(link, "honour"))
            await bot.add_reaction(ctx.message, "🆗")
        except Exception as error:
            logger.warning("Could not vote with 50%"+repr(error))
            try:
                await loop.create_task(send_discord("Could not vote with 50% on "+link, "error"))
                await bot.add_reaction(ctx.message, "🆘")
            except:
                logger.warning("Could not send message to Discord")
        await asyncio.sleep(3)
        try:
            post.reply(honourtext.format(curator), author=postaccount)
            await bot.add_reaction(ctx.message, "🔤")
        except Exception as error:
            logger.warning("Could not comment on honour post "+repr(error))
            try:
                await loop.create_task(send_discord("Could not comment on honour post "+link, "error"))
                await bot.add_reaction(ctx.message, "🆘")
            except:
                logger.warning("Could not send message to Discord")

@bot.command(pass_context=True)
async def tf100(ctx, link):
    curator = re.sub('\d|\W|(TravelFeed)','',str(ctx.message.author),re.IGNORECASE|re.DOTALL)
    if curator in curatorlist:
        author, permlink = resolve_authorperm(link)
        postlink = construct_authorperm(author, permlink)
        post = Comment(postlink)
        try:
            post.upvote(weight=100, voter=postaccount)
            await bot.add_reaction(ctx.message, "🆙")
        except Exception as error:
            logger.warning("Could not vote with 100%"+repr(error))
            try:
                await loop.create_task(send_discord("Could not vote with 100% on "+link, "error"))
                await bot.add_reaction(ctx.message, "🆘")
            except:
                logger.warning("Could not send message to Discord")
        await asyncio.sleep(3)
        try:
            post.resteem(identifier=postlink, account=postaccount)
            await bot.add_reaction(ctx.message, "🔄")
        except Exception as error:
            logger.warning("Could not resteem post "+repr(error))
            try:
                await loop.create_task(send_discord("Could not resteem "+link, "error"))
                await bot.add_reaction(ctx.message, "🆘")
            except:
                logger.warning("Could not send message to Discord")
        await asyncio.sleep(3)
        try:
            post.reply(resteemtext.format(curator), author=postaccount)
            await bot.add_reaction(ctx.message, "🔤")
        except Exception as error:
            logger.warning("Could not comment on resteem post "+repr(error))
            try:
                await loop.create_task(send_discord("Could not comment on resteem post "+link, "error"))
                await bot.add_reaction(ctx.message, "🆘")
            except:
                logger.warning("Could not send message to Discord")

@bot.command(pass_context=True)
async def coop100(ctx, link):
    curator = re.sub('\d|\W|(TravelFeed)','',str(ctx.message.author),re.IGNORECASE|re.DOTALL)
    if curator in curatorlist:
        author, permlink = resolve_authorperm(link)
        postlink = construct_authorperm(author, permlink)
        post = Comment(postlink)
        try:
            post.upvote(weight=100, voter=postaccount)
            await bot.add_reaction(ctx.message, "🚻")
        except Exception as error:
            logger.warning("Could not vote with 100% on cooperation post "+repr(error))
            try:
                await loop.create_task(send_discord("Could not vote with 100% on cooperation post "+link, "error"))
                await bot.add_reaction(ctx.message, "🆘")
            except:
                logger.warning("Could not send message to Discord")

@bot.command(pass_context=True)
async def short0(ctx, link):
    curator = re.sub('\d|\W|(TravelFeed)','',str(ctx.message.author),re.IGNORECASE|re.DOTALL)
    if curator in curatorlist:
        author, permlink = resolve_authorperm(link)
        postlink = construct_authorperm(author, permlink)
        post = Comment(postlink)
        try: 
            post.reply(manualshorttext.format(post["author"]), author=postaccount)
            await bot.add_reaction(ctx.message, "🔤")
        except Exception as error:
            logger.warning("Could not comment on short post "+repr(error))
            try:
                await loop.create_task(send_discord("Could not comment on short post "+link, "error"))
                await bot.add_reaction(ctx.message, "🆘")
            except:
                logger.warning("Could not send message to Discord")

@bot.command(pass_context=True)
async def lang0(ctx, link):
    curator = re.sub('\d|\W|(TravelFeed)','',str(ctx.message.author),re.IGNORECASE|re.DOTALL)
    if curator in curatorlist:
        author, permlink = resolve_authorperm(link)
        postlink = construct_authorperm(author, permlink)
        post = Comment(postlink)
        try:  
            post.reply(manuallangtext.format(post["author"]), author=postaccount)
            await bot.add_reaction(ctx.message, "🔤")
        except Exception as error:
            logger.warning("Could not comment on non-English post "+repr(error))
            try:
                await loop.create_task(send_discord("Could not comment on non-English post "+link, "error"))
                await bot.add_reaction(ctx.message, "🆘")
            except:
                logger.warning("Could not send message to Discord")

@bot.command(pass_context=True) 
async def copyright0(ctx, link):
    curator = re.sub('\d|\W|(TravelFeed)','',str(ctx.message.author),re.IGNORECASE|re.DOTALL)
    if curator in curatorlist:
        author, permlink = resolve_authorperm(link)
        postlink = construct_authorperm(author, permlink)
        post = Comment(postlink)
        try: 
            post.reply(copyrighttext.format(post["author"]), author=postaccount)
            await bot.add_reaction(ctx.message, "🔤")
        except Exception as error:
            logger.warning("Could not comment on copyright post "+repr(error))
            try:
                await loop.create_task(send_discord("Could not comment on copyright post "+link, "error"))
                await bot.add_reaction(ctx.message, "🆘")
            except:
                logger.warning("Could not send message to Discord")

@bot.command(pass_context=True)
async def ad10(ctx, link):
    curator = re.sub('\d|\W|(TravelFeed)','',str(ctx.message.author),re.IGNORECASE|re.DOTALL)
    if curator in curatorlist:
        author, permlink = resolve_authorperm(link)
        postlink = construct_authorperm(author, permlink)
        post = Comment(postlink)
        try:
            post.upvote(weight=10, voter=postaccount)
            await bot.add_reaction(ctx.message, "🔟")
        except Exception as error:
            logger.warning("Could not vote on ad post "+repr(error))
            try:
                await loop.create_task(send_discord("Could not vote with 10% on ad post "+link, "error"))
                await bot.add_reaction(ctx.message, "🆘")
            except:
                logger.warning("Could not send message to Discord")
        await asyncio.sleep(3)
        try:
            post.reply(advotetext.format(curator), author=postaccount)
            await bot.add_reaction(ctx.message, "🔤")
        except Exception as error:
            logger.warning("Could not comment on ad post "+repr(error))
            try:
                await loop.create_task(send_discord("Could not comment on ad post "+link, "error"))
                await bot.add_reaction(ctx.message, "🆘")
            except:
                logger.warning("Could not send message to Discord")

"""
Custom Discord commands return info fetched from Blockchain
"""
@bot.command(pass_context=True)
async def rewards(ctx, username):
    history = await get_history(username)
    await bot.say(history+" in the past 7 days")

@bot.command(pass_context=True)
async def ua(ctx, username):
    ua = await loop.create_task(get_ua(username))
    await bot.say("Steem-UA score for **"+username+"** is **"+ua+"**")

"""
Initiate general functions
"""
def handle_exit():
    logger.info("Info: Exiting bot")
    loop.run_until_complete(bot.logout())
    for t in asyncio.Task.all_tasks(loop=loop):
        if t.done():
            t.exception()
            continue
        t.cancel()
        try:
            loop.run_until_complete(asyncio.wait_for(t, 5, loop=loop))
            t.exception()
        except asyncio.InvalidStateError:
            pass
        except asyncio.TimeoutError:
            pass
        except asyncio.CancelledError:
            pass

if __name__ == '__main__':
    honours = {}
    resteems = {}
    walletpw =  os.environ.get('UNLOCK') #Beem wallet passphrase must be set as environment variable
    TOKEN = os.environ.get('TOKEN') #Discord secret token must be set as environment variable
    logger = logging.getLogger(__name__)
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO) #log to file: logger.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', filename=logpath, level=logging.INFO)
    steem = Steem()
    set_shared_steem_instance(steem)
    steem.set_default_nodes(NodeList().get_nodes())
    steem.wallet.unlock(walletpw)
    blockchain = Blockchain()
    """
    Starting the bot. A custom starting block can be defined in the blocklog file.
    """
    try:
        blockfile = open(blocklog, 'r')
        starting_point = blockfile.read()
        blockfile.close()
        logger.info("Bot started from block "+starting_point)
    except:
        starting_point = None
        logger.info("Bot started from current block")
    while True:
        """
        Start the bot
        """
        if starting_point is None:
            try:
                props = Steem().get_dynamic_global_properties()
                starting_point = props['last_irreversible_block_num']
            except:
                starting_point = starting_point
        loop = asyncio.get_event_loop()
        loop.create_task(start_blockchain(starting_point))
        loop.create_task(keepalive())
        loop.create_task(stream_history())
        loop.create_task(stream_rewards())
        try:
            loop.run_until_complete(bot.start(TOKEN))
        except KeyboardInterrupt:
            handle_exit()
            loop.close()
            logger.info("Bot ended")
            break
        except SystemExit:
            handle_exit()
        except Exception as error:
            logger.warning("Bot restarting "+repr(error))