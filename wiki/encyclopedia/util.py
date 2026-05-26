import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))


def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None

def get_html(markdown):
    texts = markdown.splitlines()
    for i in range(len(texts)):
        texts[i] = re.sub(r"#{3} (.+)", r"<h3>\1</h3>", texts[i])
        texts[i] = re.sub(r"#{2} (.+)", r"<h2>\1</h2>", texts[i])
        texts[i] = re.sub(r"#{1} (.+)", r"<h1>\1</h1>", texts[i])
        texts[i] = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", texts[i])
        texts[i] = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', texts[i])
        if "<h" not in texts[i] and texts[i] != "":
            texts[i] = f"<p>{texts[i]}</p>"
    texts = "\n".join(texts)
    return texts
