from pyflarum import FlarumUser, Filter, FlarumError

from guizero import *

from time import sleep
from tkhtmlview import HTMLScrolledText

from requests import Session
from requests_cache import CachedSession


APP = App(title="Flative", width=1700, height=800)

PER_PAGINATION_GROUP = 20
MAX_PAGINATION_GROUPS = None


USE_CACHE = True
if USE_CACHE:
    session_obj = CachedSession()
else:
    session_obj = Session()


USER = FlarumUser(
    forum_url="https://discuss.flarum.org",
    session_object=session_obj
)


def authenticate():
    username = auth_username_input.value
    password = auth_password_input.value
    forum_url = auth_forum_url_input.value

    clearCache()
    auth_status.value = ""

    if len(forum_url) >= 12:
        USER.forum_url = forum_url
        auth_status.value += "Forum URL updated. "
        auth_status.text_color = "green"

    else:
        auth_status.value += "Forum URL is invalid. "
        auth_status.text_color = "red"

    try:
        if len(username) > 0 and len(password) > 0:
            USER.authenticate(
                username_or_email=username,
                password=password
            )

            auth_status.value += "You are now logged in. "
            auth_status.text_color = "green"

        else:
            auth_status.value += "You are now browsing in guest mode (unauthenticated). "
            auth_status.text_color = "orange"

    except FlarumError as error:
        auth_status.value = error
        auth_status.text_color = "red"

    reloadDiscussions()


def getContentFromType(content_type: str, content: dict) -> str:
    # TODO: More metadata
    if content_type == "discussionLocked":
        return f"{'locked' if content['locked'] else 'unlocked'} the discussion"

    elif content_type == "discussionStickied":
        return f"{'stickied' if content['sticky'] else 'unstickied'} the discussion"

    else:
        return f"{content_type}"


def changeDiscussion(title):
    discussions.disable()
    discussionText.set_html(f"<h2>Loading...</h2>")
    discussionText.fit_height()
    id = discussionsIdsCache[discussions.items.index(title)]
    discussion = USER.get_discussion_by_id(id)
    posts = discussion.get_posts()

    html = ""

    for post in posts:
        post_author = post.get_author()

        if post.contentType == "comment":
            html += f'''<div><div><h3>Post #{post.number}:</h3>\n<b>{post_author.username if post_author else '[deleted]'}</b> <i>on {post.createdAt.strftime(r'%d %B %Y')} at {post.createdAt.strftime(r'%H:%M:%S')}</i></div>\n{post.contentHtml}\n<a href="{post.url}" style="font-size: 10px;">Open original post in your browser</a>\n\n'''

        else:
            html += f'''<div><div><b>{post_author.username if post_author else '[deleted]'}</b> {getContentFromType(post.contentType, post.content)} <i>on {post.createdAt.strftime(r'%d %B %Y')} at {post.createdAt.strftime(r'%H:%M:%S')}</i></div>\n<a href="{post.url}" style="font-size: 10px;">Open original post in your browser</a>\n\n'''

    discussionText.tag_delete(discussionText.tag_names)
    discussionText.set_html(html, strip=False)
    discussionText.fit_height()
    sleep(0.1)
    discussions.enable()


def reloadDiscussions():
    discussions.clear()
    discussionsIdsCache.clear()
    order_by = search_order_by.value

    if order_by == 'relevance':
        order_by = None

    for discussion in USER.get_discussions(Filter(query=search_input.value, page=int(pagination.value) - 1, limit=50, order_by=order_by)):
        discussions.append(f"{discussion.id} | {discussion.title} [{discussion.commentCount}]")
        discussionsIdsCache.append(discussion.id)

    if len(discussions.items) > 0:
        discussions.value = discussions.items[0]
        changeDiscussion(discussions.value)

    else:
        discussions.append("There are no discussions to be shown.")


def changePage(back: bool = False):
    current_first_page = int(pagination.options[0][-1])
    current_last_page = int(pagination.options[-1][-1])

    if MAX_PAGINATION_GROUPS:
        max_pages = PER_PAGINATION_GROUP * MAX_PAGINATION_GROUPS

    else:
        max_pages = None

    pagination.clear()

    if len(goto_page.value) > 0:
        from_page = int(goto_page.value)
        to_page = from_page + PER_PAGINATION_GROUP

        if max_pages and from_page >= max_pages - PER_PAGINATION_GROUP:
            from_page = (max_pages - PER_PAGINATION_GROUP)
            to_page = max_pages + 1

        elif from_page < 0:
            from_page = 1
            to_page = PER_PAGINATION_GROUP

        for page in range(from_page, to_page):
            pagination.append(str(page))

        pagination.value = goto_page.value
        goto_page.value = ""

    else:
        if back:
            if current_first_page < PER_PAGINATION_GROUP:
                from_page = 1
                to_page = PER_PAGINATION_GROUP

            else:
                from_page = current_first_page - PER_PAGINATION_GROUP
                to_page = current_first_page

            for page in range(from_page, to_page):
                pagination.append(str(page))

            pagination.value = str(from_page)

        else:
            from_page = current_last_page

            if max_pages and current_last_page > max_pages - PER_PAGINATION_GROUP:
                to_page = max_pages

            else:
                to_page = current_last_page + PER_PAGINATION_GROUP

            for page in range(from_page, to_page):
                pagination.append(str(page + 1))

            pagination.value = str(from_page + 1)

    current_first_page = int(pagination.options[0][0])
    current_last_page = int(pagination.options[-1][0])

    if max_pages:
        next_page_button.enabled = current_last_page < max_pages
    previous_page_button.enabled = current_first_page > 1

    reloadDiscussions()


def clearCache():
    try:
        USER.session.cache.clear()
        print("Cache was cleared.")

    except:  # not using a cache
        pass


AUTH_SPACE = Box(APP, width="fill", visible=False)
AUTH_BOX = Box(AUTH_SPACE, layout="grid")


def showOrHideLogin():
    AUTH_SPACE.visible = not AUTH_SPACE.visible


auth_forum_url_label = Text(AUTH_BOX,
                            grid=[0, 0],
                            size=10,
                            align="left",
                            text="Forum URL: "
                            )

auth_forum_url_input = TextBox(AUTH_BOX,
                               grid=[1, 0],
                               align="left",
                               text="https://discuss.flarum.org",
                               width=50
                               )

auth_username_label = Text(AUTH_BOX,
                           grid=[0, 2],
                           size=10,
                           align="left",
                           text="Username or E-mail (optional): "
                           )

auth_username_input = TextBox(AUTH_BOX,
                              grid=[1, 2],
                              align="left",
                              width=50
                              )

auth_password_label = Text(AUTH_BOX,
                           grid=[0, 3],
                           size=10,
                           align="left",
                           text="Password (optional): "
                           )

auth_password_input = TextBox(AUTH_BOX,
                              grid=[1, 3],
                              width=50,
                              align="left",
                              hide_text=True
                              )

auth_button = PushButton(AUTH_BOX,
                         grid=[1, 4],
                         text="Update",
                         command=authenticate,
                         pady=0,
                         padx=130
                         )

auth_status = Text(AUTH_BOX,
                   grid=[1, 5],
                   size=10,
                   text=""
                   )


PAGINATION_BOX = Box(APP, width="fill", layout="grid", align="bottom")
pagination = ButtonGroup(PAGINATION_BOX,
                         grid=[1, 0],
                         options=[str(page_number)
                                  for page_number in range(1, PER_PAGINATION_GROUP + 1)],
                         horizontal=True,
                         command=reloadDiscussions
                         )

previous_page_button = PushButton(PAGINATION_BOX,
                                  grid=[0, 0],
                                  text="Previous",
                                  align="left",
                                  command=changePage,
                                  args=[True],
                                  pady=2,
                                  padx=2,
                                  enabled=False
                                  )

next_page_button = PushButton(PAGINATION_BOX,
                              grid=[2, 0],
                              text="Next",
                              align="right",
                              command=changePage,
                              pady=2,
                              padx=2,
                              args=[False]
                              )

goto_page_label = Text(PAGINATION_BOX,
                       grid=[3, 0],
                       height=2,
                       size=10,
                       text="Goto page: "
                       )

goto_page = TextBox(PAGINATION_BOX,
                    grid=[4, 0]
                    )

goto_page_button = PushButton(PAGINATION_BOX,
                              grid=[5, 0],
                              text="Goto",
                              command=changePage,
                              pady=0,
                              padx=0
                              )


SEARCH_BOX = Box(APP, width="fill", layout="grid")
search_label = Text(SEARCH_BOX,
                    grid=[0, 0],
                    height=2,
                    size=10,
                    text="Search for discussions: "
                    )

search_input = TextBox(SEARCH_BOX,
                       grid=[1, 0],
                       width=50
                       )

search_button = PushButton(SEARCH_BOX,
                           grid=[2, 0],
                           text="Search",
                           command=reloadDiscussions,
                           pady=0,
                           padx=0
                           )

search_order_by = ButtonGroup(SEARCH_BOX,
                              options=[
                                  ["Relevance", "relevance"],
                                  ["Top", "commentCount"],
                                  ["Latest", "-commentCount"],
                                  ["Oldest", "createdAt"],
                                  ["Newest", "-createdAt"],
                              ],
                              selected="relevance",
                              horizontal=True,
                              grid=[3, 0],
                              command=reloadDiscussions
                              )


discussionsIdsCache = [d.id for d in USER.get_discussions()]
discussions = ListBox(APP,
                      items=[],
                      height="fill",
                      width=APP.width / 2,
                      align="left",
                      scrollbar=True,
                      command=changeDiscussion
                      )


menubar = MenuBar(APP,
                  toplevel=["Options"],
                  options=[[
                      ["Reload", reloadDiscussions],
                      ["Toggle authentication form", showOrHideLogin],
                      ["Clear cache", clearCache],
                      ["Exit", exit]
                  ]]
                  )


discussionText = HTMLScrolledText(APP.tk)
discussionText.configure(width=discussionText.winfo_reqwidth() * 2)
discussionText.bind("<Key>", lambda _: "break")
APP.add_tk_widget(discussionText)


reloadDiscussions()
APP.display()
