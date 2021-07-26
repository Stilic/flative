from pyflarum import FlarumUser
from guizero import *
app = App(title="Flative")
user = FlarumUser(forum_url="https://discuss.flarum.org")


def changeDiscussion(title):
    d = user.get_discussion_by_id(
        discussionsIdsCache[discussions.items.index(title)])
    fp = d.get_posts()[0]
    discussionText.value = fp.contentHtml


def reloadDiscussions():
    discussions.clear()
    discussionsIdsCache.clear()
    for d in user.all_discussions():
        discussions.append(d.title)
        discussionsIdsCache.append(d.id)


discussions = ListBox(app, items=[d.title for d in user.all_discussions(
)], height="fill", width="fill", align="left", scrollbar=True, command=changeDiscussion)
discussionsIdsCache = [d.id for d in user.all_discussions()]

discussionText = TextBox(app, width="fill", height="fill", align="right", scrollbar=True, multiline=True, enabled=False)


menubar = MenuBar(app,
                  toplevel=["File"], options=[
                      [["Reload", reloadDiscussions]]])

app.display()
