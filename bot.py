'''
Reddit bot
'''

import json
import sys
import datetime
import random

import praw
import bot_secrets

reddit = praw.Reddit(
    user_agent='python:v0.1:SolstheimBot (by /u/leafiest)',
    client_id=bot_secrets.client_id,
    client_secret=bot_secrets.client_secret,
    username=bot_secrets.username,
    password=bot_secrets.password,
)

msgs = [
    (
        'A terrible place I\'ve heard. '
        'There\'s a boat leaving from Khuul if you have any reason to go.'
    ),
    (
        'That\'s the frozen island up to the north, right? '
        'Sounds awful to me. If you\'re looking to get there, '
        'you might check for transportation in Khuul.'
    ),
    (
        'S\'virr can take you to Solstheim. At a fair price, too.'
    ),
    (
        'It\'s an inhospitable place, to be sure. '
        'Bears, wolves, and other creatures I\'d rather not imagine '
        'abound. It\'s cold, windy, and generally unfriendly.'
    )
]


def get_msg():
    ''' pick a comment '''
    return random.choice(msgs)


now = datetime.datetime.now


class State:
    ''' persistant state '''

    def __init__(self, filename='state.json'):
        self.filename = filename
        self.state = self._load()

    def __getitem__(self, key):
        return self.state[key]

    def __setitem__(self, key, value):
        self.state[key] = value

    def _load(self):
        ''' load data '''
        with open(self.filename, 'r') as fd:
            return json.load(fd)

    def save(self):
        ''' persist '''
        with open(self.filename, 'w+') as fd:
            json.dump(self.state, fd)

    def setdefault(self, key, value):
        ''' dict behavior '''
        if key not in self.state:
            self.state[key] = value


def is_comment(obj):
    ''' sanity check '''
    return isinstance(obj, praw.models.reddit.comment.Comment)


def transitive_to_myself(comment, depth=0):
    ''' figure out if this is a reply related to another reply I've made

    this will work even if the comment is at the top level, since the
    parent is the submission itself
    '''
    if depth > 10 or not is_comment(comment):
        # likely a submission, meaning we hit the top of the tree
        return False

    if comment.author.name == 'SolstheimBot':
        return True

    return transitive_to_myself(comment.parent(), depth=depth + 1)


def main():
    ''' read comments, distribute snark
    '''
    subreddits = reddit.subreddit('Morrowind+Skyrim')

    state = State()
    seen = 'submissions_seen'
    stats = 'statistics'

    state.setdefault(seen, [])
    state.setdefault(stats, {'read': 0, 'matched': 0, 'skipped': 0})
    print(now(), 'starting', state[stats])

    for comment in subreddits.stream.comments(skip_existing=True):

        state[stats]['read'] += 1

        if state[stats]['read'] % 100 == 0:
            print(now(), 'statdump', state[stats])
            state.save()

        if 'solstheim' not in comment.body.lower():
            continue

        if transitive_to_myself(comment):
            # don't comment on our own comments upstream
            print(now(), 'skipping', comment.permalink)
            state[stats]['skipped'] += 1

        else:
            print(now(), 'replying', comment.permalink)
            comment.reply(get_msg())

            state[seen].append(comment.submission.id)
            state[stats]['matched'] += 1

        state.save()


if not sys.flags.interactive and __name__ == '__main__':
    main()
