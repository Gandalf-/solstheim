'''
Reddit bot
'''

import datetime
import praw
import bot_secrets

reddit = praw.Reddit(
    user_agent='python:v0.1:SolstheimBot (by /u/leafiest)',
    client_id=bot_secrets.client_id,
    client_secret=bot_secrets.client_secret,
    username=bot_secrets.username,
    password=bot_secrets.password,
)

msg = (
    'A terrible place I\'ve heard. ' +
    'There\'s a boat leaving from Khuul if you have any reason to go.'
)

now = datetime.datetime.now

def main():
    ''' read comments, distribute snark
    '''
    morrowind = reddit.subreddit('Morrowind')
    stats = {'read': 0, 'matched': 0}

    for comment in morrowind.stream.comments(skip_existing=True):

        if 'solstheim' in comment.body.lower():
            stats['matched'] += 1
            print(now(), 'replying to', comment.permalink)
            comment.reply(msg)

        stats['read'] += 1

        if stats['read'] % 100 == 0:
            print(now(), stats)


if __name__ == '__main__':
    main()
