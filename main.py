from pyflarum import FlarumUser
from guizero import *
app = App(title="Flative")
user = FlarumUser(forum_url="https://discuss.flarum.org")

# layouts
discussions = ListBox(app, items=[d.title for d in user.all_discussions(
)], height="fill", width="fill", align="left")


def reloadDiscussions():
    discussions.clear()
    for discussion in user.all_discussions():
        discussions.append(discussion.title)


menubar = MenuBar(app,
                  toplevel=["File"], options=[
                      [ ["Reload", reloadDiscussions] ]])

rightBox = Box(app, height="fill", width="fill", align="right")

# other
Text(rightBox, text="Test")

app.display()
