from test_plus import TestCase

from zhihu.qa.models import Question, Answer


class QAModelTest(TestCase):

    def setUp(self) -> None:
        self.user = self.make_user('user01')
        self.other_user = self.make_user('user02')
        self.question_one = Question.objects.create(
            user=self.user,
            title='问题1',
            content='内容1',
            tags='测试1,测试2'
        )
        self.question_two = Question.objects.create(
            user=self.user,
            title='问题2',
            content='内容2',
            tags='测试1,测试2',
            has_answer=True
        )
        self.answer = Answer.objects.create(
            user=self.user,
            question=self.question_two,
            content='问题2的正确答案',
            is_answer=True
        )

    def test_can_vote_question(self):
        '''给问题投票'''
        self.question_one.votes.update_or_create(
            user=self.user,
            defaults={'value': True}
        )
        self.question_one.votes.update_or_create(
            user=self.other_user,
            defaults={'value': True}
        )
        assert self.question_one.total_votes() == 2


    def test_can_vote_answer(self):
        '''给回答投票'''
        self.answer.votes.update_or_create(
            user=self.user,
            defaults={'value': True}
        )
        self.answer.votes.update_or_create(
            user=self.other_user,
            defaults={'value': True}
        )
        assert self.answer.total_votes() == 2


    def test_get_question_voters(self):
        '''问题的投票用户'''
        self.question_one.votes.update_or_create(
            user=self.user,
            defaults={'value': True}
        )
        self.question_one.votes.update_or_create(
            user=self.other_user,
            defaults={'value': False}
        )
        assert self.user in self.question_one.get_upvoters()
        assert self.other_user in self.question_one.get_downvoters()

    def test_get_answer_voters(self):
        '''回答的投票永户'''
        self.answer.votes.update_or_create(
            user=self.user,
            defaults={'value': True}
        )
        self.answer.votes.update_or_create(
            user=self.other_user,
            defaults={'value': False}
        )
        assert self.user in self.answer.get_upvoters()
        assert self.other_user in self.answer.get_downvoters()


    def test_unanswered_question(self):
        '''未回答的问题'''
        assert self.question_one == Question.objects.get_unanswered()[0]


    def test_answered_question(self):
        '''已有答案的问题'''
        assert self.question_two == Question.objects.get_answered()[0]

    def test_question_get_answers(self):
        '''获取问题答案'''
        assert self.answer == self.question_two.get_answers()[0]
        assert self.question_two.count_answers() == 1


    def test_question_accept_answer(self):
        '''提问者接受答案'''
        answer_one = Answer.objects.create(
            user=self.user,
            question=self.question_one,
            content='1'
        )
        answer_two = Answer.objects.create(
            user=self.user,
            question=self.question_one,
            content='2'
        )
        answer_three = Answer.objects.create(
            user=self.user,
            question=self.question_one,
            content='3'
        )
        self.assertFalse(answer_one.is_answer)
        self.assertFalse(answer_two.is_answer)
        self.assertFalse(answer_three.is_answer)
        self.assertFalse(self.question_one.has_answer)

        #接受1为正确
        answer_one.accept_answer()
        self.assertTrue(answer_one.is_answer)
        self.assertTrue(self.question_one.has_answer)
        self.assertFalse(answer_two.is_answer)
        self.assertFalse(answer_three.is_answer)

    def test_question_str_(self):
        ''''''
        assert isinstance(self.question_one, Question)
        assert str(self.question_one) == '问题1'

    def test_answer_str_(self):
        ''''''
        assert isinstance(self.answer, Answer)
        assert str(self.answer) == '问题2的正确答案'
