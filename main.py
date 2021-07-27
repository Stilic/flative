from typing import List

from bs4 import BeautifulSoup

from pyflarum import FlarumUser, Filter
from guizero import *

from requests import Session
from requests_cache import CachedSession


APP = App(title="Flative", width=1700, height=800)
PER_PAGINATION_GROUP = 15
MAX_PAGINATION_GROUPS = None
USE_CACHE = True

if USE_CACHE:
    session_obj = CachedSession()
else:
    session_obj = Session

USER = FlarumUser(forum_url="https://discuss.flarum.org", session_object=session_obj)


def changeDiscussion(title):
    id = discussionsIdsCache[discussions.items.index(title)]
    discussion = USER.get_discussion_by_id(id)
    posts = discussion.get_posts()

    text_posts = [] # type: List[str]

    for post in posts:
        if post.contentType == 'comment':
            parser = BeautifulSoup(post.contentHtml, features="html.parser")

            just_text = ""
            for text in parser.find_all(text=True, recursive=True):
                just_text += text

            author = post.get_author()

            text_posts.append((post.url, author.username if author and author.username else "[deleted]", just_text))

    discussionText.value = ""
    for post_url, post_author, post in text_posts:
        discussionText.value += f"({post_url}) {post_author.upper()}:\n{post}\n\n"


def reloadDiscussions():
    discussions.clear()
    discussionsIdsCache.clear()

    for discussion in USER.all_discussions(Filter(page=int(pagination.value) - 1, limit=50, order_by='createdAt')):
        discussions.append(f"{discussion.id} | {discussion.title}")
        discussionsIdsCache.append(discussion.id)
    
    discussions.value = discussions.items[0]
    changeDiscussion(discussions.value)


def changePage(back: bool=False):
    pagination.disable()
    current_first_page = int(pagination.options[0][-1])
    current_last_page = int(pagination.options[-1][-1])

    pagination.clear()

    if back:
        for page in range(current_first_page - PER_PAGINATION_GROUP, current_first_page):
            pagination.append(str(page))

    else:
        for page in range(current_last_page, current_last_page + PER_PAGINATION_GROUP):
            pagination.append(str(page + 1))

    current_first_page = int(pagination.options[0][0])
    current_last_page = int(pagination.options[-1][0])

    if MAX_PAGINATION_GROUPS:
        max_pages = PER_PAGINATION_GROUP * MAX_PAGINATION_GROUPS

        next_page_button.enabled = current_last_page <= max_pages

    previous_page_button.enabled = current_first_page > 1

    pagination.value = str(current_first_page)
    pagination.enable()
    reloadDiscussions()


PAGINATION_BOX = Box(APP, width="fill", layout="grid")
pagination = ButtonGroup(PAGINATION_BOX, grid=[1, 0], options=[str(page_number) for page_number in range(1, PER_PAGINATION_GROUP + 1)], horizontal=True, command=reloadDiscussions)
previous_page_button = PushButton(PAGINATION_BOX, grid=[0, 0], text="Previous", align="left", command=changePage, args=[True], enabled=False)
next_page_button = PushButton(PAGINATION_BOX, grid=[2, 0], text="Next", align="right", command=changePage, args=[False])

discussionsIdsCache = [d.id for d in USER.all_discussions()]
discussions = ListBox(APP, items=[], height="fill", width="fill", align="left", scrollbar=True, command=changeDiscussion)

discussionText = TextBox(APP, width="fill", height="fill", align="right", scrollbar=True, multiline=True, enabled=False)


menubar = MenuBar(APP, toplevel=["File"], options=[[["Reload", reloadDiscussions]]])

reloadDiscussions()
APP.display()
