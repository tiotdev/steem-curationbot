import os, re, discord, asyncio, logging, janus, pycountry, pycountry_convert
from datetime import datetime, timedelta
from beem import Steem
from beem.blockchain import Blockchain
from beem.comment import Comment
from beem.account import Account
from beem.nodelist import NodeList
from beem.discussions import Query, Discussions_by_created
from beem.exceptions import ContentDoesNotExistsException
from beem.utils import construct_authorperm, resolve_authorperm
from bs4 import BeautifulSoup
from markdown import markdown
from langdetect import detect_langs
from discord.ext import commands
from discord.ext.commands import Bot
from geopy.geocoders import Nominatim

"""
Configuration: Make adjustments here
"""
#Discord Channel configuration
upvotechannel = "489680471878402048"
honourchannel = "489680498575015937"
feedchannel = "489704683137531914"
adchannel = "489781127838433281"
rewardchannel = "490396153146376194"
logchannel = "489680525389332490"
commandchannel = '490205632394297345'
australiaoceaniaafrica = '495307186608537601'
asia = '495307374597373982'
foodoftheworld = '495307704374394901'
europe = '495307415965794304'
america = '495307447616143373'
traveladvice = '495307928526389288'
nocategory = '495307497977020426'
# Curation account to track
trackaccount = 'travelfeed'
# Curated tag to search in
tracktag = 'travelfeed'
# Account to perform curation routines (can be different from tracked curation account)
postaccount = 'travelfeed'
# List of curators by Steem username
curatorlist = ['for91days', 'rimicane', 'guchtere', 'mrprofessor', 'jpphotography']
# List of curators by Discord ID
discordcuratorlist = ['386832984487231490', '385782450288328704', '347827940702289920', '433065572901584907', '264508921899646980']
# ID of the Discord bot
botid = "489608879223734292"
# List of whitelisted users whose posts are ignored
whitelist = ['travelfeed', 'tangofever', 'steemitworldmap', 'de-travelfeed', 'cyclefeed']
# Define path for logging
logpath = 'bot.log'
# Define path for start block
startblock = 'startblock.txt'
# Tag to search in for ads
adtag1 = 'travel'
# Define path for logging authors advertised to
autpath = 'author_list.log'
# Comment for short posts 
shortposttext = "Hi @{}, \n Thank you for participating in the #travelfeed curated tag. To maintain a level of quality on the project we have certain criteria that must be met for participation. Please review the following: https://steemit.com/travelfeed/@travelfeed/how-to-participate-use-travelfeed-in-your-posts \n **We require at least 250 words, but your post has only {} words.** \n Thank you very much for your interest and we hope to read some great travel articles from you soon! \n If you believe that you have received this comment by mistake or have updated your post to fit our criteria, please reply to this comment with <code>!tfreview</code>. For further questions, please contact us on the [Steemit Travellers Discord](https://discord.gg/jWWu73H). \n Regards, @travelfeed"
# Comment for blacklisted users
blacklisttext = "Hi @{}, \n Thank you for participating in the #travelfeed curated tag. To maintain a level of quality on the project we have certain criteria that must be met for participation. Please review the following: https://steemit.com/travelfeed/@travelfeed/how-to-participate-use-travelfeed-in-your-posts \n **You are currently blacklisted from the TravelFeed curation.** \n This is most likely because we have detected plagiarism in one of your posts in the past. If you believe that this is a mistake, please contact us on the [Steemit Travellers Discord](https://discord.gg/jWWu73H). \n Regards, @travelfeed"
# Comment for other languages
wronglangtext = "Hi @{}, \n Thank you for participating in the #travelfeed curated tag. To maintain a level of quality on the project we have certain criteria that must be met for participation. Please review the following: https://steemit.com/travelfeed/@travelfeed/how-to-participate-use-travelfeed-in-your-posts \n We require at least 250 words **in English**. \n Thank you very much for your interest and we hope to read some great travel articles from you soon! \n The language of your post was automatically detected, if your English text is at least 250 words long or you have updated your post to fit our criteria, please reply to this comment with <code>!tfreview</code> for it to be considered for curation. For further questions, please contact us on the [Steemit Travellers Discord](https://discord.gg/jWWu73H). \n Regards, @travelfeed"
# Honour text
honourtext = "Congratulations! Your high-quality travel content was selected by @travelfeed curator @{} and earned you a **partial** upvote. We love your hard work and hope to encourage you to continue to publish strong travel-related content. <br> Thank you for participating in #travelfeed! <center> [![TravelFeed](https://ipfs.busy.org/ipfs/QmZhLuw8WE6JMCYHD3EXn3MBa2CSCcygvfFqfXde5z3TLZ)](https://steemit.com/travelfeed/@travelfeed/introducing-travelfeed-featuring-steemit-s-best-travel-content) <br> **Learn more about our travel project on Steemit by clicking on the banner above and join our community on [Discord](https://discord.gg/jWWu73H)**.</center>"
# Resteem Text
resteemtext = "Congratulations! Your high-quality travel content was selected by @travelfeed curator @{} and earned you a reward, in form of a **100% upvote** and a **resteem**. Your work really stands out. Your article now has a chance to get curated and featured under the appropriate daily topic of our Travelfeed blog. Thank you for participating in #travelfeed! <br> <center>[![TravelFeed](https://ipfs.busy.org/ipfs/QmNTkoKQNzuQbQGbcZ1exTMjvxYUprdnVczxnvib9VUSqB)](https://steemit.com/travelfeed/@travelfeed/introducing-travelfeed-featuring-steemit-s-best-travel-content) <br> **Learn more about our travel project on Steemit by clicking on the banner above and join our community on [Discord](https://discord.gg/jWWu73H)**</center>"
# Advote Text
advotetext = "Great read! Your high-quality travel content was selected by @travelfeed curator @{}. We just gave you a small upvote together with over 60 followers of the @travelfeed curation trail. <br> Have you heard of @travelfeed? Using the #travelfeed tag rewards authors and content creators who produce exceptional travel related articles, so be sure use our tag to get much bigger upvotes, resteems and be featured in our curation posts! <br> <center>[![TravelFeed](https://ipfs.busy.org/ipfs/QmNTkoKQNzuQbQGbcZ1exTMjvxYUprdnVczxnvib9VUSqB)](https://steemit.com/travelfeed/@travelfeed/introducing-travelfeed-featuring-steemit-s-best-travel-content) <br> **Learn more about our travel project on Steemit by clicking on the banner above and join our community on [Discord](https://discord.gg/jWWu73H)**</center>"
# Manual comment text for short posts
manualshorttext = "Hi @{}, \n Thank you for participating in the #travelfeed curated tag. To maintain a level of quality on the project we have certain criteria that must be met for participation. Please review the following: https://steemit.com/travelfeed/@travelfeed/how-to-participate-use-travelfeed-in-your-posts \n **We require at least 250 words.** \n Thank you very much for your interest and we hope to read some great travel articles from you soon! \n If you believe that you have received this comment by mistake or have updated your post to fit our criteria, please reply to this comment with <code>!tfreview</code>. For further questions, please contact us on the [Steemit Travellers Discord](https://discord.gg/jWWu73H). \n Regards, @travelfeed"
# Manual comment text for posts that are not in English
manuallangtext = "Hi @{}, \n Thank you for participating in the #travelfeed curated tag. To maintain a level of quality on the project we have certain criteria that must be met for participation. Please review the following: https://steemit.com/travelfeed/@travelfeed/how-to-participate-use-travelfeed-in-your-posts \n We require at least 250 words **in English**. \n Thank you very much for your interest and we hope to read some great travel articles from you soon! \n If you believe that you have received this comment by mistake or have updated your post to fit our criteria, please reply to this comment with <code>!tfreview</code>. For further questions, please contact us on the [Steemit Travellers Discord](https://discord.gg/jWWu73H). \n Regards, @travelfeed"
# Copyright text
copyrighttext = "Hi @{}, \n Thank you for participating in the #travelfeed curated tag. To maintain a level of quality on the project we have certain criteria that must be met for participation. Please review the following: https://steemit.com/travelfeed/@travelfeed/how-to-participate-use-travelfeed-in-your-posts \n We require **proper sourcing** for all media and text that is not your own. \n If you have updated your post with sources, please reply to this comment with <code>!tfreview</code>. For further questions, please contact us on the [Steemit Travellers Discord](https://discord.gg/jWWu73H). \n Thank you very much for your interest and we hope to read some great travel articles from you soon! \n Regards, @travelfeed"

honours = {}
resteems = {}
walletpw =  os.environ.get('UNLOCK') #Beem wallet passphrase must be set as environment variable
TOKEN = os.environ.get('TOKEN') #Discord secret token must be set as environment variable
logger = logging.getLogger(__name__)
logging.basicConfig(filename=logpath, format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)
node_list = NodeList().get_nodes()
steem = Steem(node=node_list)
steem.set_default_nodes(node_list)
steem.wallet.unlock(walletpw)
blockchain = Blockchain()
blacklist = Account(trackaccount).get_mutings(raw_name_list=True)

"""
Discord functions
"""
async def send_discord(msg, cnl):
    """Sends the message *msg* to the Discord channel *cnl*"""
    await bot.wait_until_ready()
    await bot.send_message(bot.get_channel(cnl), msg)

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    """Changes discord presence to "Playing TravelFeed.io" when the bot comes online"""
    try:
        await bot.change_presence(game=discord.Game(name='TravelFeed.io'))
    except:
        logger.warning("Could not change Discord presence")
    logger.info("Login to Discord successful")

@bot.event
async def on_reaction_add(reaction, user):
    """Initiate curation process by adding a reaction"""
    if reaction.message.content.startswith('http'):
        curator = re.sub(r'\d|\W|(TravelFeed)','',str(user),re.IGNORECASE|re.DOTALL)
        if not user.id in discordcuratorlist and not user.id == botid:
            """Checks if user who added reaction is a curator"""
            await loop.create_task(send_discord("Curator unauthorised: "+curator, logchannel))
            return
        else:
            author, permlink = resolve_authorperm(reaction.message.content)
            post = Comment(construct_authorperm(author, permlink))
            if reaction.emoji == '🌍':
                await bot.add_reaction(reaction.message, "⏳")
                actionqueue.put(Post_Action(post, "tf100", curator, reaction.message))
            elif reaction.emoji == '🌐': 
                await bot.add_reaction(reaction.message, "⏳") 
                actionqueue.put(Post_Action(post, "tf50", curator, reaction.message))
            elif reaction.emoji == '👥':
                await bot.add_reaction(reaction.message, "⏳")
                actionqueue.put(Post_Action(post, "coop100", None, reaction.message))
            elif reaction.emoji == '👋':
                await bot.add_reaction(reaction.message, "⏳")
                actionqueue.put(Post_Action(post, "ad10", curator, reaction.message))
            elif reaction.emoji == '📏':
                await bot.add_reaction(reaction.message, "⏳")
                actionqueue.put(Post_Action(post, "short0", None, reaction.message))
            elif reaction.emoji == '🇬🇧':
                await bot.add_reaction(reaction.message, "⏳")
                actionqueue.put(Post_Action(post, "lang0", None, reaction.message))
            elif reaction.emoji == '📝':
                await bot.add_reaction(reaction.message, "⏳")
                actionqueue.put(Post_Action(post, "copyright0", None, reaction.message))

"""Initiate curation process by using Discord commands"""
@bot.command(pass_context=True)
async def tf100(ctx, link):
    curator = re.sub(r'\d|\W|(TravelFeed)','',str(ctx.message.author),re.IGNORECASE|re.DOTALL)
    if not ctx.message.channel.id == commandchannel:
        """Checks if the command was set in the correct channel"""
        await loop.create_task(send_discord("Bot commands are only allowed in #bot-commands", ctx.message.channel.id))
        return
    if not ctx.message.author.id in discordcuratorlist:
        """Checks if user who used the command is a curator"""
        await loop.create_task(send_discord("Curator unauthorised: "+curator, logchannel))
        return
    await bot.add_reaction(ctx.message, "⏳")
    author, permlink = resolve_authorperm(link)
    authorperm = construct_authorperm(author, permlink)
    post = Comment(authorperm)
    actionqueue.put(Post_Action(post, "tf100", curator, ctx.message))

@bot.command(pass_context=True)
async def tf50(ctx, link):
    curator = re.sub(r'\d|\W|(TravelFeed)','',str(ctx.message.author),re.IGNORECASE|re.DOTALL)
    if not ctx.message.channel.id == commandchannel:
        await loop.create_task(send_discord("Bot commands are only allowed in #bot-commands", ctx.message.channel.id))
        return
    if not ctx.message.author.id in discordcuratorlist:
        await loop.create_task(send_discord("Curator unauthorised: "+curator, logchannel))
        return
    await bot.add_reaction(ctx.message, "⏳")
    author, permlink = resolve_authorperm(link)
    post = Comment(construct_authorperm(author, permlink))
    actionqueue.put(Post_Action(post, "tf50", curator, ctx.message))

@bot.command(pass_context=True)
async def coop100(ctx, link):
    curator = re.sub(r'\d|\W|(TravelFeed)','',str(ctx.message.author),re.IGNORECASE|re.DOTALL)
    if not ctx.message.channel.id == commandchannel:
        await loop.create_task(send_discord("Bot commands are only allowed in #bot-commands", ctx.message.channel.id))
        return
    if not ctx.message.author.id in discordcuratorlist:
        await loop.create_task(send_discord("Curator unauthorised: "+curator, logchannel))
        return
    await bot.add_reaction(ctx.message, "⏳")
    author, permlink = resolve_authorperm(link)
    authorperm = construct_authorperm(author, permlink)
    post = Comment(authorperm)
    actionqueue.put(Post_Action(post, "coop100", None, ctx.message))

@bot.command(pass_context=True)
async def ad10(ctx, link):
    curator = re.sub(r'\d|\W|(TravelFeed)','',str(ctx.message.author),re.IGNORECASE|re.DOTALL)
    if not ctx.message.channel.id == commandchannel:
        await loop.create_task(send_discord("Bot commands are only allowed in #bot-commands", ctx.message.channel.id))
        return
    if not ctx.message.author.id in discordcuratorlist:
        await loop.create_task(send_discord("Curator unauthorised: "+curator, logchannel))
        return
    await bot.add_reaction(ctx.message, "⏳")
    author, permlink = resolve_authorperm(link)
    authorperm = construct_authorperm(author, permlink)
    post = Comment(authorperm)
    actionqueue.put(Post_Action(post, "ad10", curator, ctx.message))

@bot.command(pass_context=True)
async def short0(ctx, link):
    curator = re.sub(r'\d|\W|(TravelFeed)','',str(ctx.message.author),re.IGNORECASE|re.DOTALL)
    if not ctx.message.channel.id == commandchannel:
        await loop.create_task(send_discord("Bot commands are only allowed in #bot-commands", ctx.message.channel.id))
        return
    if not ctx.message.author.id in discordcuratorlist:
        await loop.create_task(send_discord("Curator unauthorised: "+curator, logchannel))
        return
    await bot.add_reaction(ctx.message, "⏳")
    author, permlink = resolve_authorperm(link)
    authorperm = construct_authorperm(author, permlink)
    post = Comment(authorperm)
    actionqueue.put(Post_Action(post, "short0", None, ctx.message))

@bot.command(pass_context=True)
async def lang0(ctx, link):
    curator = re.sub(r'\d|\W|(TravelFeed)','',str(ctx.message.author),re.IGNORECASE|re.DOTALL)
    if not ctx.message.channel.id == commandchannel:
        await loop.create_task(send_discord("Bot commands are only allowed in #bot-commands", ctx.message.channel.id))
        return
    if not ctx.message.author.id in discordcuratorlist:
        await loop.create_task(send_discord("Curator unauthorised: "+curator, logchannel))
        return
    await bot.add_reaction(ctx.message, "⏳")
    author, permlink = resolve_authorperm(link)
    authorperm = construct_authorperm(author, permlink)
    post = Comment(authorperm)
    actionqueue.put(Post_Action(post, "lang0", None, ctx.message))
 
@bot.command(pass_context=True) 
async def copyright0(ctx, link):
    curator = re.sub(r'\d|\W|(TravelFeed)','',str(ctx.message.author),re.IGNORECASE|re.DOTALL)
    if not ctx.message.channel.id == commandchannel:
        await loop.create_task(send_discord("Bot commands are only allowed in #bot-commands", ctx.message.channel.id))
        return
    if not ctx.message.author.id in discordcuratorlist:
        await loop.create_task(send_discord("Curator unauthorised: "+curator, logchannel))
        return
    await bot.add_reaction(ctx.message, "⏳")
    author, permlink = resolve_authorperm(link)
    authorperm = construct_authorperm(author, permlink)
    post = Comment(authorperm)
    actionqueue.put(Post_Action(post, "copyright0", None, ctx.message))

"""
Custom Discord commands that return info fetched from the Blockchain
"""
@bot.command(pass_context=True)
async def rewards(ctx, username):
    """Get number of upvotes by @travelfeed for an account *username* within the past 7 days"""
    history = get_history(username)
    await bot.say(history+" in the past 7 days")

@bot.command()
async def mana():
    """Get current voting mana of @travelfeed"""
    acc = Account("travelfeed")
    mana = acc.get_manabar()
    await bot.say("The voting mana of @travelfeed is **"+str(round(mana['current_mana_pct'], 2))+"**")

@bot.command(pass_context=True)
async def payouts(ctx, time):
    """Get author rewards to be paid out to featured authors for the past *time* days"""
    await bot.say("Fetching rewards history for the past **"+time+"** days to #rewards_log")
    await loop.create_task(send_discord("*Manual queing initiated*", rewardchannel))
    await stream_rewards(time)
    await loop.create_task(send_discord("*Manual queing ended*", rewardchannel))

@bot.command(pass_context=True)
async def location(ctx, link):
    """Get the location of a post *link*"""
    author, permlink = resolve_authorperm(link)
    post = Comment(construct_authorperm(author, permlink))
    body = post['body']
    location = get_location(body, None)
    if location == None:
        await bot.say("No location provided")
    else:
        await bot.say("The location is: **"+location+"**")

@bot.command(pass_context=True)
async def getposts(ctx, theme):
    """Get the location of a post *link*"""
    q = Query(limit=100, tag="travelfeed")
    for post in Discussions_by_created(q):
        continent_code = get_location(post['body'], "continentcode")
        link = "https://steemit.com/"+construct_authorperm(post['author'], post['permlink'])
        if post['author'] in curatorlist or post['author'] in whitelist:
            continue
        elif (continent_code == "AF" or continent_code == "OC" or continent_code == "AN") and (theme == "Africa" or theme == "Oceania" or theme =="Australia" or theme == "australiaoceaniaafrica"):
            await bot.say(link)
        elif continent_code == "AS" and theme == "Asia":
            await bot.say(link)
        elif continent_code == "EU" and theme == "Europe":
            await bot.say(link)
        elif (continent_code == "SA" or continent_code == "NA") and theme == "America":
            await bot.say(link)
        elif ("food" in post['body'] or "eat" in post['body'] or "restaurant" in post['body']) and (theme == "Food" or theme =="foodoftheworld"):
            await bot.say(link)
        elif ("advice" in post['body'] or "budget" in post['body'] or "learn" in post['body']) and (theme == "Advice" or theme == "Travel Advice" or theme == "traveladvice"):
            await bot.say(link)

"""
Queue functions
"""
class Discord_Message:
    """Class to send a Discord message"""
    def __init__(self, message, channel):
        self.message = message
        self.channel = channel
    async def run(self):
        await loop.create_task(send_discord(self.message, self.channel))

class Post_Action:
    """Class to initiate a curation routine for a post"""
    def __init__(self, post, action, curator, reaction):
        self.post = post
        self.action = action
        self.curator = curator
        self.reaction = reaction
    async def run(self):
        await loop.create_task(post_do_action(self.post, self.action, self.curator, self.reaction))

async def queue_worker(async_q):
    """Worker function to process queue"""
    while True:
        if async_q.empty() == True:
            await asyncio.sleep(5)
        else:
            action = async_q.get()
            await action.run()

"""
Beem query functions
"""
def get_history(user):
    """Returns the number of votes received the user received from the curation account in the past 7 days"""
    if user in resteems and user in honours:
        return "**"+str(resteems[user])+"** Resteems, **"+str(honours[user])+"** Honours"
    elif user in resteems:
        return "**"+str(resteems[user])+"** Resteems, **0** Honours"
    elif user in honours:
        return "**0** Resteems, **"+str(honours[user])+"** Honours"
    else:
        return "**0** Resteems, **0** Honours"

def get_location(body, returnthis):
    """If a steemitworldmap code is in the text, the location is extracted"""
    m = re.search(r"\bsteemitworldmap\b\s([-+]?([1-8]?\d(\.\d+)?|90(\.0+)?))\s\blat\b\s([-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?))", body)
    if m:
        try:
            latitude = m.group(1)
            longitude = m.group(5)
            geolocator = Nominatim(user_agent="travelfeed/0.1")
            rawlocation = geolocator.reverse(latitude+", "+longitude, language="en", timeout=10).raw
            address = rawlocation['address']
            state = address.get('state', None)
            if state == None: #Not every location has a state/region/... set!
                state = address.get('region', None)
                if state == None:
                    state = address.get('state_district', None)
                    if state == None:
                        state = address.get('county', None)
                        if state == None:
                            state = ""
            country_code = str(address["country_code"]).upper()
            country_object = pycountry.countries.get(alpha_2=country_code)
            try:
                country = country_object.common_name #Some countries such as Taiwan or Bolivia have a common name that is used instead of the official name
            except:
                country = country_object.name
            continent_code = pycountry_convert.country_alpha2_to_continent_code(country_code)
            if continent_code == "AF":
                continent = "Africa"
            elif continent_code == "NA":
                continent = "North America"
            elif continent_code == "OC":
                continent = "Oceania"
            elif continent_code == "AN":
                continent = "Antarctica"
            elif continent_code == "AS":
                continent = "Asia"
            elif continent_code == "EU":
                continent = "Europe"
            elif continent_code == "SA":
                continent = "South America"
            if returnthis == None:
                location = state+", "+country+", "+continent
                return location
            if returnthis == "continentcode":
                return continent_code
        except Exception as error:
            logger.warning("Could not determine location: "+repr(error))
            return None
    else:
        return None

def is_eligible(text, n, lng):
    """Returns True if *text* contains at least *n* words in the specified *lng* language"""
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
Beem actions
"""
async def post_do_action(post, action, curator, reaction):
    """Executes curation routine *action* for post *post*"""
    try:
        authorperm = construct_authorperm(post["author"], post["permlink"])
        link = "https://steemit.com/"+authorperm
        if post["author"] in blacklist:
            await loop.create_task(send_discord("WARNING: Author is blacklisted "+link, logchannel))
            return
        elif action == "tf100":
            try:
                post.upvote(weight=100, voter=postaccount)
                await loop.create_task(send_discord(link, upvotechannel))
                continent_code = get_location(post['body'], "continentcode")
                if continent_code == "AF" or continent_code == "OC" or continent_code == "AN":
                    await loop.create_task(send_discord(link, australiaoceaniaafrica))
                elif continent_code == "AS":
                    await loop.create_task(send_discord(link, asia))
                elif continent_code == "EU":
                    await loop.create_task(send_discord(link, europe))
                elif continent_code == "SA" or continent_code == "NA":
                    await loop.create_task(send_discord(link, america))
                elif "food" in post['body'] or " eat" in post['body'] or "restaurant" in post['body']:
                    await loop.create_task(send_discord(link, foodoftheworld))
                elif "advice" in post['body'] or "budget" in post['body'] or "learn" in post['body']:
                    await loop.create_task(send_discord(link, traveladvice))
                else:
                    await loop.create_task(send_discord(link, nocategory))
                if not reaction == None:
                    await bot.add_reaction(reaction, "🆙")
            except Exception as error:
                if not "skip_transaction_dupe_check" in repr(error):
                    logger.warning("Could not vote with 100%"+repr(error))
                    try:
                        await loop.create_task(send_discord("Could not vote with 100% on "+link+" Exception: "+repr(error), logchannel))
                        if not reaction == None:
                            await bot.add_reaction(reaction, "🆘")
                    except:
                        logger.warning("Could not send message to Discord")
                    return
            await asyncio.sleep(4)
            try:
                post.resteem(identifier=authorperm, account=postaccount)
                if not reaction == None:
                    await bot.add_reaction(reaction, "🔄")
            except Exception as error:
                logger.warning("Could not resteem post "+repr(error))
                try:
                    await loop.create_task(send_discord("Could not resteem "+link+" Exception: "+repr(error), logchannel))
                    if not reaction == None:
                        await bot.add_reaction(reaction, "🆘")
                except:
                    logger.warning("Could not send message to Discord")
            await asyncio.sleep(4)
            try:
                post.reply(resteemtext.format(curator), author=postaccount)
                if not reaction == None:
                    await bot.add_reaction(reaction, "🔤")
            except Exception as error:
                logger.warning("Could not comment on resteem post "+repr(error))
                try:
                    await loop.create_task(send_discord("Could not comment on resteem post "+link+" Exception: "+repr(error), logchannel))
                    if not reaction == None:
                        await bot.add_reaction(reaction, "🆘")
                except:
                    logger.warning("Could not send message to Discord")
        elif action == "tf50":
            try:
                post.upvote(weight=50, voter=postaccount)
                if not reaction == None:
                    await bot.add_reaction(reaction, "🆗")
                await loop.create_task(send_discord(link, honourchannel))
            except Exception as error:
                logger.warning("Could not vote with 50%"+repr(error))
                try:
                    await loop.create_task(send_discord("Could not vote with 50% on "+link+" Exception: "+repr(error), logchannel))
                    if not reaction == None:
                        await bot.add_reaction(reaction, "🆘")
                except:
                    logger.warning("Could not send message to Discord")
                return
            await asyncio.sleep(4)
            try:
                post.reply(honourtext.format(curator), author=postaccount)
                if not reaction == None:
                    await bot.add_reaction(reaction, "🔤")
            except Exception as error:
                logger.warning("Could not comment on honour post "+repr(error))
                try:
                    await loop.create_task(send_discord("Could not comment on honour post "+link+" Exception: "+repr(error), logchannel))
                    if not reaction == None:
                        await bot.add_reaction(reaction, "🆘")
                except:
                    logger.warning("Could not send message to Discord")
        elif action == "coop100":
            try:
                post.upvote(weight=100, voter=postaccount)
                if not reaction == None:
                    await bot.add_reaction(reaction, "🚻")
            except Exception as error:
                logger.warning("Could not vote with 100% on cooperation post "+repr(error))
                try:
                    await loop.create_task(send_discord("Could not vote with 100% on cooperation post "+link+" Exception: "+repr(error), logchannel))
                    if not reaction == None:
                        await bot.add_reaction(reaction, "🆘")
                except:
                    logger.warning("Could not send message to Discord")
                return
        elif action == "ad10":
            try:
                post.upvote(weight=10, voter=postaccount)
                if not reaction == None:
                    await bot.add_reaction(reaction, "🔟")
            except Exception as error:
                logger.warning("Could not vote on ad post "+repr(error))
                try:
                    await loop.create_task(send_discord("Could not vote with 10% on ad post "+link+" Exception: "+repr(error), logchannel))
                    if not reaction == None:
                        await bot.add_reaction(reaction, "🆘")
                except:
                    logger.warning("Could not send message to Discord")
                return
            await asyncio.sleep(4)
            try:
                post.reply(advotetext.format(curator), author=postaccount)
                if not reaction == None:
                    await bot.add_reaction(reaction, "🔤")
            except Exception as error:
                logger.warning("Could not comment on ad post "+repr(error))
                try:
                    await loop.create_task(send_discord("Could not comment on ad post "+link+" Exception: "+repr(error), logchannel))
                    if not reaction == None:
                        await bot.add_reaction(reaction, "🆘")
                except:
                    logger.warning("Could not send message to Discord")
        elif action == "short0":
            try: 
                post.reply(manualshorttext.format(post["author"]), author=postaccount)
                if not reaction == None:
                    await bot.add_reaction(reaction, "🔤")
            except Exception as error:
                logger.warning("Could not comment on short post "+repr(error))
                try:
                    await loop.create_task(send_discord("Could not comment on short post "+link+" Exception: "+repr(error), logchannel))
                    if not reaction == None:
                        await bot.add_reaction(reaction, "🆘")
                except:
                    logger.warning("Could not send message to Discord")
        elif action == "lang0":
            try:  
                post.reply(manuallangtext.format(post["author"]), author=postaccount)
                if not reaction == None:
                    await bot.add_reaction(reaction, "🔤")
            except Exception as error:
                logger.warning("Could not comment on non-English post "+repr(error))
                try:
                    await loop.create_task(send_discord("Could not comment on non-English post "+link+" Exception: "+repr(error), logchannel))
                    if not reaction == None:
                        await bot.add_reaction(reaction, "🆘")
                except:
                    logger.warning("Could not send message to Discord")
        elif action == "copyright0":
            try: 
                post.reply(copyrighttext.format(post["author"]), author=postaccount)
                if not reaction == None:
                    await bot.add_reaction(reaction, "🔤")
            except Exception as error:
                logger.warning("Could not comment on copyright post "+repr(error))
                try:
                    await loop.create_task(send_discord("Could not comment on copyright post "+link+" Exception: "+repr(error), logchannel))
                    if not reaction == None:
                        await bot.add_reaction(reaction, "🆘")
                except:
                    logger.warning("Could not send message to Discord")
        if not reaction == None:
            try:
                await bot.remove_reaction(reaction, "⏳", bot.user)
            except Exception as error:
                logger.warning("Could not remove hourglass reaction"+repr(error))
        await asyncio.sleep(3)
    except Exception as error:
        logger.warning("Could not execute action for post "+str(post)+repr(error))
        try:
            await loop.create_task(send_discord("Could not execute action on post "+str(post)+" Exception:"+repr(error), logchannel))
            if not reaction == None:
                await bot.add_reaction(reaction, "🆘")
        except:
            logger.warning("Could not send message to Discord")

"""
Beem background tasks
"""
async def stream_history():
    """Background task: Gets votes received from travelfeed within the past 7 days every hour"""
    acc = Account(trackaccount)
    stop = datetime.utcnow() - timedelta(days=7)
    while True:
        global honours
        global resteems
        honours = {}
        resteems = {}
        try:
            for vote in acc.history_reverse(stop=stop, only_ops=["vote"]):
                if vote["voter"] == trackaccount and vote["weight"] == 5000:
                    if vote["author"] not in honours:
                        honours[vote["author"]]=1
                    else:
                        honours[vote["author"]]=honours[vote["author"]]+1
                elif vote["voter"] == trackaccount and vote["weight"] == 10000:
                    if vote["author"] not in resteems:
                        resteems[vote["author"]]=1
                    else:
                        resteems[vote["author"]]=resteems[vote["author"]]+1
            logger.info("Got history from Blockchain")
        except Exception as error:
            logger.warning("Could not get history from Blockchain: "+repr(error))
        await asyncio.sleep(60*60) #sleep 1 hour
        
async def stream_rewards(rewardtime):
    """Background task: Scans blockchain for travelfeed author rewards, extracts mentions and determines which reward should be sent to mentioned users every six hours"""
    #Todo when code has been tested: Send out rewards automatically
    while True:
        try:
            if rewardtime == None:
                rewardtime = 6
            else:
                rewardtime = int(rewardtime)*24
            acc = Account(trackaccount)
            stop = datetime.utcnow() - timedelta(hours=rewardtime)
            for reward in acc.history_reverse(stop=stop, only_ops=["author_reward"]):
                authorperm = construct_authorperm(reward["author"], reward["permlink"])
                post = Comment(authorperm)
                if not "Weekly Round-Up" in post["title"]:
                    continue
                if reward['sbd_payout'] == '0.000 SBD':
                    sbdreward = None
                else:
                    sbdreward = float(re.sub("( SBD)",'',reward['sbd_payout'],re.IGNORECASE|re.DOTALL))
                if reward['steem_payout'] == '0.000 STEEM':
                    steemreward = None
                else:
                    steemreward = float(re.sub("( STEEM)",'',reward['steem_payout'],re.IGNORECASE|re.DOTALL))
                myre = re.compile(r"@([a-zA-Z0-9-]+)<")
                mentions = list(myre.findall(post["body"]))
                for curator in curatorlist:
                    if curator in mentions:
                        mentions.remove(curator)
                while True:
                    if "travelfeed" in mentions:
                        mentions.remove('travelfeed')
                    elif "steemitworldmap" in mentions:
                        mentions.remove('steemitworldmap')
                    else:
                        break
                memo = "Congratulations! Here comes your reward for being featured in "+post["title"]+" https://steemit.com/travelfeed/"+authorperm
                mentionsdict = {x:mentions.count(x) for x in mentions}
                mentionsnr = len(mentions)
                if mentionsnr == 0:
                    continue
                elif mentionsnr > 3:
                    logging.warning("Could not get rewards for post "+authorperm+": Mentions more than three")
                    continue
                logger.info("Found author reward for post https://steemit.com/"+authorperm)
                if steemreward == None: #Payouts in Steem, SBD or both are supported
                    await loop.create_task(send_discord("Found author reward of "+str(sbdreward)+" SBD for post https://steemit.com/"+authorperm+". Half of the liquid SBD rewards will be split between the featured authors "+str(mentions)+". Memo: `"+memo+"`", rewardchannel))
                    for postauthor in mentionsdict:
                        payout = round((mentionsdict[postauthor]/(mentionsnr*2)*sbdreward), 3)
                        await loop.create_task(send_discord("Please send the reward of **"+str(payout)+" SBD** to **"+postauthor+"**", rewardchannel))
                elif sbdreward == None:
                    await loop.create_task(send_discord("Found author reward of "+str(steemreward)+" STEEM for post https://steemit.com/"+authorperm+". Half of the liquid STEEM rewards will be split between the featured authors "+str(mentions)+". Memo: `"+memo+"`", rewardchannel))
                    for postauthor in mentionsdict:
                        payout = round((mentionsdict[postauthor]/(mentionsnr*2)*steemreward), 3)
                        await loop.create_task(send_discord("Please send the reward of **"+str(payout)+" Steem** to **"+postauthor+"**", rewardchannel))
                else:
                    await loop.create_task(send_discord("Found author reward of "+str(steemreward)+" STEEM and "+str(sbdreward)+" SBD for post https://steemit.com/"+authorperm+". Half of the liquid rewards will be split between the featured authors "+str(mentions)+". Memo: `"+memo+"`", rewardchannel))
                    for postauthor in mentionsdict:
                        steempayout = round((mentionsdict[postauthor]/(mentionsnr*2)*steemreward), 3)
                        sbdpayout = round((mentionsdict[postauthor]/(mentionsnr*2)*sbdreward), 3)
                        await loop.create_task(send_discord("Please send the reward of **"+str(steempayout)+" Steem** and **"+str(sbdpayout)+" SBD** to **"+postauthor+"**", rewardchannel))
                await loop.create_task(send_discord(":boom: :boom: :boom: :boom: :boom: :boom:", rewardchannel))
            logger.info("Got rewards from Blockchain")
            if rewardtime == None:
                await asyncio.sleep(60*60*6) #sleep for 6 hours
            else:
                return
        except Exception as error:
            logger.warning("Could not stream rewards: "+repr(error))
            await loop.create_task(send_discord("Could not stream rewards: "+repr(error), rewardchannel))


def stream_comments(sync_q):
    """Main task: Starts comment stream from the blockchain"""
    processed_posts = []
    try:
        blockfile = open(startblock, 'r')
        starting_point = int(blockfile.read())
        blockfile.close()
    except:
        try:
            props = steem.get_dynamic_global_properties()
            starting_point = props['last_irreversible_block_num']
        except:
            stream_comments(sync_q)
    try:
        stream = map(Comment, blockchain.stream(start=starting_point, opNames=["comment"]))
        logger.info("Stream from blockchain started at block "+str(starting_point))
    except Exception as error:
        logger.warning("Could not start blockchain stream "+repr(error))
        stream_comments(starting_point)
    """Continuously stream comment objects from Blockchain, react to relevant one"""
    for post in stream:
        try:
            post.refresh()
            tags = post["tags"]
            author = post["author"]
            body = post["body"]
            authorperm = construct_authorperm(author, post['permlink'])
            if post.is_comment():
                if author in curatorlist:                
                    """Initiates an action if a curator uses the invocation command in a comment"""
                    parent = post.get_parent()
                    if "!tf50" in body:
                        sync_q.put(Post_Action(parent, "tf50", author, None))
                    elif "!tf100" in body:
                        sync_q.put(Post_Action(parent, "tf100", author, None))
                    elif "!coop100" in body:
                        sync_q.put(Post_Action(parent, "coop100", None, None))
                    elif "!ad10" in body:
                        sync_q.put(Post_Action(parent, "ad10", author, None)) 
                elif "!tfreview" in body:
                    """Users targeted by bot comments can have their posts manually reviewed"""
                    if post.parent_author == postaccount:
                        parent = post.get_parent()
                        parentlink = construct_authorperm(parent['author'], parent['permlink'])
                        logger.info("@{} requests manual review ".format(author))
                        history = get_history(author)
                        try:
                            sync_q.put(Discord_Message("Author requests manual review: "+history, feedchannel))
                            sync_q.put(Discord_Message("https://steemit.com/"+parentlink, feedchannel))
                        except:
                            logger.warning("Could not send message to Discord")
                        try:
                            post.reply("Thanks! We will review your post.", author=postaccount)
                        except:
                            logger.warning("Could not send reply to !tfreview reuester")
            elif post.is_main_post() and tracktag in tags and not author in whitelist:
                """Checks for each *post* in #travelfeed if it fits the criteria"""
                commenttext = ""
                if post.time_elapsed() > timedelta(minutes=2) or post in processed_posts: #If a post is edited within the first two minutes it would be processed twice without checking for the second condition. The array of processed posts does not need to be saved at exit since it is only relevant for two minutes
                    logger.info("Ignoring updated post")
                    continue
                elif author in blacklist: 
                    commenttext = blacklisttext
                    logger.info("Detected post by blacklisted user @{}".format(author))
                else:
                    try:
                        content = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', ''.join(BeautifulSoup(markdown(body), "html.parser").findAll(text=True)))
                        count = len(content.split(" "))
                        check_eligible = is_eligible(content, 225, "en")
                        if count < 240:
                            commenttext = shortposttext
                            logger.info("Detected short post by @{} who posted with just {} words".format(author, count))
                        elif check_eligible == False:
                            commenttext = wronglangtext
                            logger.info("Detected post by @{} who posted not in English".format(author))
                        else:
                            logger.info("Sending awesome post by @{} to Discord feed".format(author))
                            try:
                                history = get_history(author)
                                location = get_location(body, None)
                            except:
                                history = ""
                                location = None
                            if location == None:
                                msg = history+". **"+str(count)+"** words."
                            else:
                                msg = history+". **"+str(count)+"** words. Location: **"+location+"**"
                            try:
                                sync_q.put(Discord_Message(msg, feedchannel))
                                sync_q.put(Discord_Message("https://steemit.com/"+authorperm, feedchannel))
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
                            sync_q.put(Discord_Message("Could not leave a comment for bad post https://steemit.com/"+authorperm, logchannel))
                        except:
                            logger.warning("Could not send message to Discord")
                        continue
                processed_posts += [authorperm]
            elif post.is_main_post() and (adtag1 in tags) and not tracktag in tags:
                """Checks if post is in adtag and eligable for advertisement"""
                content = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', ''.join(BeautifulSoup(markdown(body), "html.parser").findAll(text=True)))
                if is_eligible(content, 400, "en"):
                    adfile = open(autpath, 'a+')
                    adfile.seek(0)
                    author_list = adfile.read().splitlines()
                    if not author in author_list:
                        try:
                            adfile.write("\n"+author)
                            sync_q.put(Discord_Message("https://steemit.com/"+authorperm, adchannel))
                            logger.info("Found an advertisement post by @{}".format(author))
                        except:
                            logger.warning("Could not promote advertisement post by @{}".format(author))
                        adfile.close()
                        adfile = open(autpath, 'a+')
        except ContentDoesNotExistsException:
            continue
        except Exception as error:
            logger.warning("Exception during post processing: "+repr(error))

if __name__ == '__main__':
    """
    Starting the bot. An optional custom starting block can be defined in the optional *startblock* file.
    """
    loop = asyncio.get_event_loop()
    queue = janus.Queue(loop=loop) #janus enables the synchronous beem library to work with the asynchronous Discord.py library
    actionqueue = queue.sync_q
    loop.create_task(stream_history())
    loop.create_task(stream_rewards(None))
    loop.create_task(queue_worker(actionqueue))
    threaded = loop.run_in_executor(None, stream_comments, actionqueue)
    while True:
        try:
            loop.run_until_complete(bot.start(TOKEN))
            loop.run_until_complete(threaded)
        except KeyboardInterrupt:
            loop.close()
            bot.logout()
            logger.debug("Bot ended by user")
            break
        except SystemExit:
            loop.close()
            bot.logout()
            logger.debug("Bot crashed")
            break
        except Exception as error:
            logger.warning("Bot restarting "+repr(error))