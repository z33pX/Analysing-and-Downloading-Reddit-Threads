from urllib.parse import quote_plus
import pprint
import praw
from praw.models import MoreComments
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
import json


def get_continuous_chunks(text):
    chunked = ne_chunk(pos_tag(word_tokenize(text)))
    prev = None
    continuous_chunk = []
    current_chunk = []

    for i in chunked:
        if type(i) == Tree:
            current_chunk.append(" ".join([token for token, pos in i.leaves()]))
        elif current_chunk:
            named_entity = " ".join(current_chunk)
            if named_entity not in continuous_chunk:
                continuous_chunk.append(named_entity)
                current_chunk = []
        else:
            continue

    if continuous_chunk:
        named_entity = " ".join(current_chunk)
        if named_entity not in continuous_chunk:
            if named_entity:
                continuous_chunk.append(named_entity)

    return continuous_chunk

def reddit_search(keyword, numer_of_comments, dump_to_json, append=False):
    reddit = praw.Reddit(
        user_agent='test (by /u/USERNAME)',  # Don't edit this one
        client_id='YOUT_ID', client_secret='YOUR_SECRET',
        username='YOUR_USERNAME', password='YOUR_PASSWORD')

    subreddit = reddit.subreddit('all')

    tree = list()
    if append:
        with open(dump_to_json) as f:
            print('Load database ...')
            tree = json.load(f)

    for i in subreddit.search(keyword, limit=numer_of_threads):
        # Load all comments
        submission = reddit.submission(id=i.id)
        thread = dict()
        thread[keyword] = list()

        # Iterate comments
        for top_level_comment in list(submission.comments):
            # Apply entity analysis
            entity_analysis = get_continuous_chunks(top_level_comment.body)
            top_comment_dict = dict()

            # Print stuff
            print(top_level_comment.body)
            print('Entity Recognition:')
            print(entity_analysis)
            print('Replies:')

            # Create dict
            top_comment_dict['top_comment'] = top_level_comment.body
            top_comment_dict['entity_analysis'] = entity_analysis
            top_comment_dict['replies'] = list()

            def load_replies(replies, replies_tree):
                if not replies:
                    return ""
                replies_list = list()
                for replie in replies:
                    # Apply entity analysis
                    entity_analysis = get_continuous_chunks(replie.body)

                    # Create dict
                    next_replie = dict()
                    next_replie['comment'] = replie.body
                    next_replie['entity_analysis'] = entity_analysis
                    next_replie['replies'] = list()

                    # Print stuff
                    print('   ---------')
                    print('   ' + str(replie.body))
                    print('   Entity Recognition:')
                    print('   ' + str(entity_analysis))

                    # Recursively
                    load_replies(replie.replies, next_replie['replies'])

                    # Clean the dict
                    if not next_replie['replies']:
                        del next_replie['replies']
                    if not next_replie['entity_analysis']:
                        del next_replie['entity_analysis']
                    # Append dict to list
                    replies_list.append(next_replie)

                replies_tree.append(replies_list)

            # Do the same recursively for all replies
            load_replies(
                replies=top_level_comment.replies,
                replies_tree=top_comment_dict['replies'])

            print('-------------------------------------')
            # Clean the dict
            if not top_comment_dict['replies']:
                del top_comment_dict['replies']
            if not top_comment_dict['entity_analysis']:
                del top_comment_dict['entity_analysis']
            thread[keyword].append(top_comment_dict)
            tree.append(thread)

    with open(dump_to_json, 'w') as fp:
        json.dump(tree, fp, indent=4, sort_keys=True)

if __name__ == '__main__':
    reddit_search(
        keyword="algotrading",
        numer_of_threads=1,
        dump_to_json="database.json",
        append=False)
