from aiohttp.web_exceptions import HTTPConflict, HTTPNotFound, HTTPBadRequest, HTTPUnauthorized
from aiohttp_apispec import request_schema, querystring_schema

from app.quiz.models import Answer
from app.quiz.schemes import (
    ThemeSchema, ThemeListSchema, QuestionSchema, ListQuestionSchema, ThemeIdSchema,
)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class ThemeAddView(AuthRequiredMixin, View):
    @request_schema(ThemeSchema)
    async def post(self):
        is_auth = await self.is_auth()
        if not is_auth:
            raise HTTPUnauthorized
        title = self.data["title"]
        quizzes = self.store.quizzes
        theme_exist = await quizzes.get_theme_by_title(title)
        if theme_exist:
            raise HTTPConflict
        theme = await quizzes.create_theme(title=title)
        return json_response(data=ThemeSchema().dump(theme))


class ThemeListView(AuthRequiredMixin, View):
    async def get(self):
        is_auth = await self.is_auth()
        if not is_auth:
            raise HTTPUnauthorized
        quizzes = self.store.quizzes
        themes = {"themes": await quizzes.list_themes()}
        return json_response(data=ThemeListSchema().dump(themes))


class QuestionAddView(AuthRequiredMixin, View):
    @request_schema(QuestionSchema)
    async def post(self):
        is_auth = await self.is_auth()
        if not is_auth:
            raise HTTPUnauthorized
        title = self.data["title"]
        theme_id = self.data["theme_id"]
        answers = []
        answers_data = self.data["answers"]
        quizzes = self.store.quizzes
        question_exist = await quizzes.get_question_by_title(title)
        theme_exist = await quizzes.get_theme_by_id(theme_id)
        is_true_count = 0
        if not theme_exist:
            raise HTTPNotFound
        if len(answers_data) < 2:
            raise HTTPBadRequest
        for item in answers_data:
            is_true_count += 1 if item["is_correct"] else 0
            answers.append(Answer(**item))
        if is_true_count != 1:
            raise HTTPBadRequest
        if question_exist:
            raise HTTPConflict
        question = await quizzes.create_question(title=title, theme_id=theme_id, answers=answers)
        return json_response(data=QuestionSchema().dump(question))


class QuestionListView(AuthRequiredMixin, View):
    @querystring_schema(ThemeIdSchema)
    async def get(self):
        is_auth = await self.is_auth()
        if not is_auth:
            raise HTTPUnauthorized
        quizzes = self.store.quizzes
        query_params = self.request["querystring"]
        theme_id = query_params.get("theme_id", None)
        questions = {"questions": await quizzes.list_questions(theme_id)}
        return json_response(data=ListQuestionSchema().dump(questions))
