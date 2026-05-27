from django.shortcuts import render, redirect
from . import util
import random

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html")
    else:
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "texts": util.get_html(util.get_entry(title))
        })

def randompage(request):
    random_str = random.choice(util.list_entries())
    return redirect(f"/wiki/{random_str}")

def search(request):
    if request.method == "GET":
        keyword = request.GET.get("q").lower()
        synonym = []
        for entry in util.list_entries():
            if keyword == entry.lower():
                return redirect(f"/wiki/{entry}")
            elif keyword in entry.lower():
                synonym.append(entry)
        if not synonym:        
            return render(request, "encyclopedia/error.html")
        else:
            return render(request, "encyclopedia/search.html", {
                        "synonym": synonym
                    })
def create(request):
    if request.method == "GET":
        return render(request, "encyclopedia/create.html")
    if request.method == "POST":
        title = request.POST.get("title").title()
        content = request.POST.get("content")
        if title.lower() in [entry.lower() for entry in util.list_entries()]:
            return render(request, "encyclopedia/create.html", {
                "error": "This entry already exists!"
            })
        else:
            util.save_entry(title, content)
            return redirect(f"/wiki/{title}")
        
def edit(request, title):
    if request.method == "GET":
        content = util.get_entry(title)
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "content": content
        })
    if request.method == "POST":
        content = request.POST.get("content")
        util.save_entry(title, content)
        return redirect(f"/wiki/{title}")