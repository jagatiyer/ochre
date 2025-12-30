from django.shortcuts import render

def story_page(request):
    return render(request, "story/story_page.html")


def society_page(request):
    return render(request, "story/society.html")
