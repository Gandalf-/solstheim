'''
Reddit bot
'''

import json
import sys
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

class State():
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

def main():
    ''' read comments, distribute snark
    '''
    morrowind = reddit.subreddit('Morrowind')

    state = State()
    seen = 'submissions_seen'
    stats = 'statistics'

    state.setdefault(seen, [])
    state.setdefault(stats, {'read': 0, 'matched': 0, 'skipped': 0})
    print('starting', state[stats])

    for comment in morrowind.stream.comments(skip_existing=True):

        state[stats]['read'] += 1

        if state[stats]['read'] % 100 == 0:
            print(now(), state[stats])
            state.save()

        if 'solstheim' not in comment.body.lower():
            continue

        if comment.submission.id in state[seen]:
            # don't comment on the same submission twice
            print(now(), 'skipping', comment.permalink)
            state[stats]['skipped'] += 1

        else:
            print(now(), 'replying to', comment.permalink)
            comment.reply(msg)

            state[seen].append(comment.submission.id)
            state[stats]['matched'] += 1

        state.save()


if not sys.flags.interactive and __name__ == '__main__':
    main()
