import jwt
from django.conf import settings
from django.http import Http404
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..core import constants as c

# models
from . import models as m
from ..account.models import User

# serializers
from . import serializers as s


class CompanyPolicyViewSet(viewsets.ModelViewSet):

    queryset = m.CompanyPolicy.objects.all()
    serializer_class = s.CompanyPolicySerializer

    def create(self, request):
        author = request.data.pop('author', None)

        if author is not None:
            pass
        else:
            author = request.user

        serializer = s.CompanyPolicySerializer(
            data=request.data,
            context={
                'author': author
            }
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def update(self, request, pk=None):
        instance = self.get_object()
        author = request.data.pop('author', None)

        if author is not None:
            pass
        else:
            author = request.user

        serializer = s.CompanyPolicySerializer(
            instance,
            data=request.data,
            context={
                'author': author
            }
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="short")
    def get_short_policies(self, request):
        page = self.paginate_queryset(m.CompanyPolicy.published_content.all())
        serializer = s.ShortCompanyPolicySerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path="policy-options")
    def get_policy(self, request):
        ret = []
        for (value, text) in c.COMPANY_POLICY_TYPE:
            ret.append({
                'value': value,
                'text': text
            })

        return Response(
            ret, status=status.HTTP_200_OK
        )


# class SecurityKnowledgeViewSet(TMSViewSet):

#     queryset = m.SecurityKnowledge.objects.all()
#     serializer_class = s.SecurityKnowledgeSerializer

#     def create(self, request):
#         author = request.data.pop('author', None)

#         if author is not None:
#             pass
#         else:
#             author = request.user

#         serializer = s.SecurityKnowledgeSerializer(
#             data=request.data,
#             context={
#                 'author': author
#             }
#         )

#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(
#             serializer.data,
#             status=status.HTTP_200_OK
#         )

#     def update(self, request, pk=None):
#         instance = self.get_object()
#         author = request.data.pop('author', None)

#         if author is not None:
#             pass
#         else:
#             author = request.user

#         serializer = s.SecurityKnowledgeSerializer(
#             instance,
#             data=request.data,
#             context={
#                 'author': author
#             }
#         )

#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(
#             serializer.data,
#             status=status.HTTP_200_OK
#         )


class QuestionViewSet(viewsets.ModelViewSet):

    queryset = m.Question.objects.all()
    serializer_class = s.QuestionSerializer

    @action(detail=False, url_path="short")
    def get_short_list(self, request):
        page = self.paginate_queryset(m.Question.objects.all())
        serializer = s.ShortQuestionSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class TestViewSet(viewsets.ModelViewSet):

    queryset = m.Test.objects.all()
    serializer_class = s.TestSerializer

    # def create(self, request):
    #     questions = request.data.pop('questions', [])
    #     applicants = request.data.pop('appliants', [])
    #     questions = [x['id'] for x in questions]
    #     appliants = [x['id'] for x in applicants]

    #     serializer = s.TestCreateSerializer(
    #         data={
    #             'questions': questions,
    #             'appliants': appliants
    #         }
    #     )

    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(
    #         serializer.data, status=status.HTTP_201_CREATED
    #     )

    # def update(self, request, pk=None):
    #     pass

    @action(detail=False, url_path="my-tests")
    def me(self, request, pk=None):
        page = self.paginate_queryset(m.Test.objects.filter(appliants=request.user))
        serializer = s.ShortTestSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


def get_company_policy(request, policy_id):
    policy = get_object_or_404(m.CompanyPolicy, id=policy_id, is_published=True)
    return render(
        request, 'security/policy.html',
        {
            'title': policy.title,
            'published_on': policy.published_on,
            'author': policy.author.name if policy.author.name else policy.author.username,
            'policy_type': policy.get_policy_type_display,
            'content': policy.content
        }
    )


def get_test_template(request, test_id):
    if request.method == 'GET':
        options = {
            'verify_exp': False
        }
        try:
            token = request.GET.get('token')
            username = request.GET.get('username')
            payload = jwt.decode(token, settings.SECRET_KEY, options=options)
            if username == payload.get('username'):
                test = get_object_or_404(m.Test, id=test_id)
                appliant = get_object_or_404(User, username=username)
                is_start = request.GET.get('start', False)

                if is_start or m.TestResult.objects.filter(test=test, appliant=appliant).exists():
                    try:
                        test_result = m.TestResult.objects.get(test=test, appliant=appliant)
                        next_question = None
                        for question in test.questions.all():
                            if question in test_result.questions.all():
                                continue
                            next_question = question
                            break
                    except m.TestResult.DoesNotExist:
                        next_question = test.questions.all().first()

                    if next_question is not None:
                        return render(
                            request, 'security/test.html',
                            {
                                'is_started': True,
                                'is_finished': False,
                                'test': test,
                                'username': username,
                                'token': token,
                                'question': next_question
                            }
                        )
                    else:
                        result = 5
                        return render(
                            request, 'security/test.html',
                            {
                                'is_finished': True,
                                'result': result
                            }
                        )

                else:
                    return render(
                        request, 'security/test.html',
                        {
                            'is_started': False,
                            'is_finished': False,
                            'test': test,
                            'username': username,
                            'token': token
                        }
                    )
            else:
                raise Http404
        except jwt.DecodeError:
            raise Http404
    elif request.method == 'POST':
        return redirect('')


def answer_question(request, test_id, question_id):
    username = request.POST['username']
    token = request.GET.get('token')
    test = get_object_or_404(m.Test, id=test_id)
    appliant = get_object_or_404(User, username=username)
    question = get_object_or_404(m.Question, id=question_id)
    test_result, created = m.TestResult.objects.get_or_create(appliant=appliant, test=test)

    if question.question_type == c.QUESTION_TYPE_BOOLEN:
        is_correct = True if request.POST['answers'] == '1' else False
        m.TestQuestionResult.objects.create(
            test_result=test_result,
            question=question,
            is_correct=is_correct
        )
    elif question.question_type == c.QUESTION_TYPE_SINGLE_CHOICE:
        m.TestQuestionResult.objects.create(
            test_result=test_result,
            question=question,
            answers=request.POST.getlist('answers')
        )
    elif question.question_type == c.QUESTION_TYPE_MULTIPLE_CHOICE:
        m.TestQuestionResult.objects.create(
            test_result=test_result,
            question=question,
            answers=request.POST.getlist('answers')
        )

    return redirect(
        reverse('security:app-test', args=[test_id]) + '?username=' + username + '&token=' + token
    )
