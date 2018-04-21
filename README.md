# Steempy WordCountBot
## Description
This bot scans the Steem blockchain for new posts in a specified tag, counts the words of each post found and leaves a comment if the word count is less than 250 words. Processed posts are added to a list to prevent double-comments.

## Why?
I programmed this bot to help our curation with @travelfeed. While #travel is spammed with many posts that consist of single photos, #travelfeed is for longer travel blogs only and has certain quality requirements, most importantly a minimum of 250 words. Using a word count tool and manually leaving comments on all short posts is a really tiring job, so I wrote this script to automate it. You can see it in action here: https://steemit.com/@travelfeed-bot/comments

## Requirements 
Apart from steem-python the python packages bs4 and markdown to turn the markdown fetched from the Blockchain into plain text to count words:
>pip install -U bs4 markdown

Passphrase of the steem-python wallet: 
>export UNLOCK='your-passphrase'

A working Steemit node. For me this configuration had the best results 
>steempy set nodes https://gtg.steem.house:8090/,https://api.steemit.com

## Usage
Adjust the tag (set to *travelfeed*) and the steem-username (set to *travelfeed-bot*, 2x). Adjust all comments written on the blockchain (posts.reply) and shell messages (print) to your liking.

Tip: Run with tmux as described here: https://steemit.com/utopian-io/@steempytutorials/part-3-creating-a-dynamic-upvote-bot-that-runs-24-7-first-weekly-challenge-3-steem-prize-pool
