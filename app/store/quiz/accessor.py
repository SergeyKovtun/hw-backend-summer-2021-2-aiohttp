from typing import Optional

from app.base.base_accessor import BaseAccessor
from app.quiz.models import Theme, Question, Answer


class QuizAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> Theme:
        theme = Theme(id=self.app.database.next_theme_id, title=str(title))
        self.app.database.themes.append(theme)
        return theme

    async def get_theme_by_title(self, title: str) -> Optional[Theme]:
        theme = None
        for item in self.app.database.themes:
            if item.title == title:
                theme = item
                break
        return theme

    async def get_theme_by_id(self, id_: int) -> Optional[Theme]:
        theme = None
        for item in self.app.database.themes:
            if item.id == id_:
                theme = item
                break
        return theme

    async def list_themes(self) -> list[Theme]:
        list_themes = [item for item in self.app.database.themes]
        return list_themes

    async def get_question_by_title(self, title: str) -> Optional[Question]:
        question = None
        for item in self.app.database.questions:
            if item.title == title:
                question = item
                break
        return question

    async def create_question(
            self, title: str, theme_id: int, answers: list[Answer]
    ) -> Question:
        question = Question(id=self.app.database.next_question_id,
                            title=str(title),
                            theme_id=theme_id,
                            answers=answers)
        self.app.database.questions.append(question)
        return question

    async def list_questions(self, theme_id: Optional[int] = None) -> list[Question]:
        list_questions = [item for item in self.app.database.questions
                          if item.theme_id == theme_id or not theme_id]
        return list_questions
