import json

from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory
from test_plus.test import CBVTestCase

from qa import views
from zhihu.qa.models import Question, Answer


class BaseQATest(CBVTestCase):

    def setUp(self) -> None:
        self.user = self.make_user("user01")
        self.other_user = self.make_user("user02")

        self.question_one = Question.objects.create(
            user=self.user,
            title="问题1",
            content="问题1的内容",
            tags="测试1, 测试2"
        )
        self.question_two = Question.objects.create(
            user=self.user,
            title="问题2",
            content="问题2的内容",
            has_answer=True,
            tags="测试1, 测试2"
        )
        self.answer = Answer.objects.create(
            user=self.user,
            question=self.question_two,
            content="问题2被采纳的回答",
            is_answer=True
        )
        self.request = RequestFactory().get('/fake')
        self.request.user = self.user


class TestQuestionListView(BaseQATest):
    '''问题列表页'''
    def test_context_data(self):
        response = self.get(views.QuestionListView, request=self.request)

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context_data['questions'],
            map(repr, [self.question_one,self.question_two]),
            ordered=False)
        self.assertContext('popular_tags', Question.objects.get_counted_tags())
        self.assertContext('active', 'all')


class TestAnsweredQuestionListView(BaseQATest):
    '''问题列表页'''
    def test_context_data(self):
        response = self.get(views.AnsweredQuestionListView, request=self.request)

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context_data['questions'],
            [repr(self.question_two)]
        )
        self.assertEqual(response.context_data['active'], 'answered')


class TestUnAnsweredQuestionListView(BaseQATest):
    '''问题列表页'''
    def test_context_data(self):
        response = self.get(views.UnAnsweredQuestionListView, request=self.request)

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context_data['questions'],
            [repr(self.question_one)]
        )
        self.assertEqual(response.context_data['active'], 'unanswered')


class TestCreateQuestionView(BaseQATest):
    '''创建问题'''

    def test_get(self):
        response = self.get(views.CreateQuestionView, request=self.request)
        self.response_200(response)

        self.assertContains(response, '标题')
        self.assertContains(response, '编辑')
        self.assertContains(response, '标签')
        self.assertIsInstance(response.context_data['view'], views.CreateQuestionView)

    def test_post(self):
        data = {
            'title': 'title',
            'content': 'content',
            'tags': 'tag1,tag2',
            'status': 'O'
        }
        request = RequestFactory().post('/fake', data=data)
        request.user = self.user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.post(views.CreateQuestionView, request=request)
        assert response.status_code == 302
        assert response.url == '/qa/'


class TestQuestionDetailView(BaseQATest):
    '''测试问题详情页'''

    def test_get_context_data(self):
        response = self.get(views.QuestionDetailView, request=self.request,
                            pk=self.question_one.pk)
        self.response_200(response)

        self.assertEqual(
            response.context_data['question'],
            self.question_one
        )


class TestCreateAnswerView(BaseQATest):

    def test_get(self):
        response = self.get(views.CreateAnswerView, request=self.request,
                            question_id=self.question_one.id)
        self.response_200(response)
        self.assertContains(response, '编辑')

        self.assertIsInstance(response.context_data['view'], views.CreateAnswerView)

    def test_post(self):
        data = {
            'content': 'a'
        }
        request = RequestFactory().post('/fake', data=data)
        request.user = self.user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.post(views.CreateAnswerView, request=request,
                             question_id=self.question_one.id)
        self.response_302(response)
        # assert response.url == f'/qa/question-detail/{self.question_one.id}'


class TestQAVote(BaseQATest):

    def setUp(self) -> None:

        super(TestQAVote, self).setUp()
        self.request = RequestFactory().post('/fake',
                                             HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.request.POST = self.request.POST.copy()

        self.request.user = self.other_user


    def test_question_upvote(self):
        '''赞同'''
        self.request.POST['question'] = self.question_one.id
        self.request.POST['value'] = 'U'

        response = views.question_vote(self.request)

        self.response_200(response)
        assert json.loads(response.content)['votes'] == 1

    def test_question_downvote(self):
        '''踩'''
        self.request.POST['question'] = self.question_two.id
        self.request.POST['value'] = 'D'

        response = views.question_vote(self.request)

        self.response_200(response)
        assert json.loads(response.content)['votes'] == -1


    def test_answer_upvote(self):
        '''赞同回答'''
        self.request.POST['answer'] = self.answer.pk
        self.request.POST['value'] = 'U'

        response = views.answer_vote(self.request)

        self.response_200(response)
        assert json.loads(response.content)['votes'] == 1


    def test_answer_downvote(self):
        '''反对回答'''
        self.request.POST['answer'] = self.answer.pk
        self.request.POST['value'] = 'D'

        response = views.answer_vote(self.request)

        self.response_200(response)
        assert json.loads(response.content)['votes'] == -1


    def test_accept_answer(self):
        '''接受回答'''
        self.request.user = self.user  #提问者
        self.request.POST['answer'] = self.answer.pk

        response = views.accept_answer(self.request)

        self.response_200(response)
        assert json.loads(response.content)['status'] == 'true'

