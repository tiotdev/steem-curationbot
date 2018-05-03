# Beem Bot for Curated Tags
## Description
This bot scans the Steem blockchain for new posts in a specified curated tag. If a post is found, the bot checks if the author is on a specified whitelist (action: skipping post) or on a blacklist (blacklist is automatically fetched from the blockchain by listing all users muted by the specified curation account; action: leaving blacklist comment). 
If none of that applies, the post content is processed and the language of the post is detected (if not at least 250 words in English: leaving wronglanguage comment). If that is true, a word count is performed to check if the post fulfills the minimum requirement of at least 250 words (if not: leaving shortpost comment). Posts that fulfill both requirements are skipped, all processed posts are added to a list to prevent double-comments.
If an exception occurs (mostly due to a node error), the bot automatically attempts to reconnect to the Steem blockchain starting at the block where the error occured and randomly selecting one out of four node pairs.

## Why?
I programmed this bot to help our curation with @travelfeed / #travelfeed. While #travel is spammed with many posts that consist of single photos, #travelfeed is for longer travel blogs only and has certain quality requirements, most importantly a minimum of 250 words in English. Using a word count tool and manually leaving comments on all short posts is a really tiring job, so I wrote this script to automate it. You can see it in action here: https://steemit.com/@travelfeed-bot/comments

## Requirements 
Apart from beem, the python packages *bs4*, *markdown* and *langdetect* are required:
>pip install -U bs4 markdown langdetect

The posting key of the account needs to be imported into beem via the CLI:
>beempy addkey yourpostingkey

The passphrase of the steem-python wallet (not Steem key!) needs to be exportet: 
>export UNLOCK='your-passphrase'

## Usage
Adjust the variables. 
Tip: Run with tmux as described here: https://steemit.com/utopian-io/@steempytutorials/part-3-creating-a-dynamic-upvote-bot-that-runs-24-7-first-weekly-challenge-3-steem-prize-pool
