from django.http import Http404
from django.shortcuts import render

from django_viewcomponent.preview import ViewComponentPreview


def request_get_to_dict(request):
    """
    Convert request.GET to a dictionary
    """
    query_dict = request.GET
    return {
        key: query_dict.getlist(key)
        if len(query_dict.getlist(key)) > 1
        else query_dict.get(key)
        for key in query_dict.keys()
    }


def preview_index_view(request):
    previews = ViewComponentPreview.previews
    context = {"previews": previews}
    return render(request, "django_viewcomponent/index.html", context)


def previews_view(request, preview_name):
    preview_cls = ViewComponentPreview.previews.get(preview_name, None)
    if not preview_cls:
        raise Http404
    context = {"preview_cls": preview_cls}
    return render(request, "django_viewcomponent/previews.html", context)


def preview_view(request, preview_name, example_name):
    preview_cls = ViewComponentPreview.previews.get(preview_name, None)
    if not preview_cls:
        raise Http404

    preview_instance = preview_cls()

    query_dict = request_get_to_dict(request)
    fun = getattr(preview_instance, example_name, None)
    if fun is None:
        raise Http404

    preview_html = fun(**query_dict)
    preview_source = preview_instance.preview_source(example_name)

    context = {
        "preview_instance": preview_instance,
        "preview_html": preview_html,
        "preview_source": preview_source,
    }

    return render(request, "django_viewcomponent/preview.html", context)
