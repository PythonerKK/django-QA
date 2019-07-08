from django.views.generic import UpdateView, ListView, DetailView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST

from notifications.views import notification_handler
from qa.forms import QuestionForm
from zhihu.utils.helpers import ajax_required, AuthorRequiredMixin
from zhihu.qa.models import Question, Answer


class QuestionListView(LoginRequiredMixin, ListView):
    '''所有问题列表页'''
    model = Question
    paginate_by = 10
    context_object_name = 'questions'
    template_name = 'qa/question_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(QuestionListView, self).get_context_data(
            object_list=None, **kwargs)
        context['popular_tags'] = Question.objects.get_counted_tags()
        context['active'] = 'all'
        return context


class AnsweredQuestionListView(QuestionListView):
    '''已经有答案的问题'''

    def get_queryset(self):
        return Question.objects.get_answered()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(AnsweredQuestionListView, self).get_context_data(
            object_list=None, **kwargs)
        context['active'] = 'answered'
        return context


class UnAnsweredQuestionListView(QuestionListView):
    '''没有答案的问题'''

    def get_queryset(self):
        return Question.objects.get_unanswered()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(UnAnsweredQuestionListView, self).get_context_data(
            object_list=None, **kwargs)
        context['active'] = 'unanswered'
        return context


class CreateQuestionView(LoginRequiredMixin, CreateView):
    '''新建问题'''
    model = Question
    form_class = QuestionForm
    template_name = 'qa/question_form.html'
    message = '问题已提交'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(CreateQuestionView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, self.message)
        return reverse_lazy('qa:unanswered_q')


class QuestionDetailView(LoginRequiredMixin, DetailView):
    '''问题的详情内容'''
    model = Question
    template_name = 'qa/question_detail.html'
    context_object_name = 'question'


class QuestionDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    '''问题删除'''
    model = Question
    context_object_name = 'question'
    template_name = 'qa/question_confirm_delete.html'

    success_url = reverse_lazy('qa:unanswered_q')


class CreateAnswerView(LoginRequiredMixin, CreateView):
    '''回答问题'''
    model = Answer
    fields = ['content']
    message = '问题已提交'
    template_name = 'qa/answer_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.question_id = self.kwargs['question_id']
        return super(CreateAnswerView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, self.message)
        return reverse_lazy('qa:question_detail', kwargs={
            'pk': self.kwargs['question_id']
        })

@login_required
@ajax_required
@require_POST
def question_vote(request):
    '''给问题投票 AJAX POST'''
    question_id = request.POST['question']
    value = True if request.POST['value'] == 'U' else False
    question = Question.objects.get(pk=question_id)
    users = question.votes.values_list('user', flat=True)  #问题的投票用户

    if request.user.pk in users and (
        question.votes.get(user=request.user).value == value):
        question.votes.get(user=request.user).delete()
    else:
        question.votes.update_or_create(user=request.user, defaults={'value': value})

    """
    #用户首次操作  点赞、踩
    if request.user.pk not in users:
        question.votes.update_or_create(user=request.user, defaults={'value': value})

    #用户已经赞了  取消赞/踩
    elif question.votes.get(user=request.user).value:
        if value:
            question.votes.get(user=request.user).delete() #取消赞
        else:
            question.votes.update_or_create(user=request.user, defaults={'value': value}) #变成踩

    #用户踩过  取消踩/赞以下
    else:
        if not value:
            question.votes.get(user=request.user).delete() #取消踩
        else:
            question.votes.update_or_create(user=request.user, defaults={'value': value}) #变成赞

    """

    return JsonResponse({
        'votes': question.total_votes()
    })



@login_required
@ajax_required
@require_POST
def answer_vote(request):
    '''给回答投票 AJAX POST'''
    answer_id = request.POST['answer']
    value = True if request.POST['value'] == 'U' else False
    answer = Answer.objects.get(pk=answer_id)
    users = answer.votes.values_list('user', flat=True)  #问题的投票用户

    if request.user.pk in users and (
        answer.votes.get(user=request.user).value == value):
        answer.votes.get(user=request.user).delete()
    else:
        answer.votes.update_or_create(user=request.user, defaults={'value': value})

    return JsonResponse({
        'votes': answer.total_votes()
    })


@login_required
@ajax_required
@require_POST
def accept_answer(request):
    '''接受回答'''
    answer_id = request.POST['answer']
    answer = Answer.objects.get(pk=answer_id)
    #如果登录用户不是提问者
    if answer.question.user.username != request.user.username:
        raise PermissionDenied()
    answer.accept_answer()

    #通知回答者
    notification_handler(
        actor=request.user,
        recipient=answer.user,
        verb='W',
        action_object=answer
    )

    return JsonResponse({
        'status': 'true'
    })
