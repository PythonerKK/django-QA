import functools

from django.http import HttpResponseBadRequest
from django.views.generic import View
from django.core.exceptions import PermissionDenied

def ajax_required(func):
    '''
    验证是否为AJAX
    :param func:
    :return:
    '''
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest('ajax required')
        return func(request, *args, **kwargs)

    return wrapper


class AuthorRequiredMixin(View):
    '''
    验证是否为原作者
    '''
    def dispatch(self, request, *args, **kwargs):
        if self.get_object().user.username != self.request.user.username:
            raise PermissionDenied
        return super(AuthorRequiredMixin, self).dispatch(request, *args, **kwargs)
