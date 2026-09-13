import datetime
from django.urls import reverse
from django.utils import timezone
from django.test import TestCase
from .models import Question


def create_question(text, days):
    """Create a question labeled from the given text and published into the given number of days to now."""
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(text=text, publication_date=time)

def add_choice_to_question(id, text):
    """Create a question and add a choice to it."""
    question = Question.objects.get(pk=id)
    return question.choice_set.create(text=text, votes=0)


class QuestionIndexViewTests(TestCase):
    url = reverse("polls:index")

    def test_no_questions(self):
        """Displays an appropriate message when there isn't any questions."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """Includes questions with a publication date in the past."""
        question = create_question(text="Past question", days=-30)
        add_choice_to_question(id=question.id, text="1st choice")
        response = self.client.get(self.url)
        self.assertQuerySetEqual(response.context["latest_question_list"], [question],)

    def test_future_question(self):
        """Excludes question with a publication date in the future."""
        create_question(text="Future question", days=30)
        response = self.client.get(self.url)
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_and_past_questions(self):
        """Includes past questions without futures questions."""
        past_question = create_question(text="Past question", days=-30)
        future_question = create_question(text="Future question", days=30)
        add_choice_to_question(id=past_question.id, text="past question choice")
        add_choice_to_question(id=future_question.id, text="future question choice")
        response = self.client.get(self.url)
        self.assertQuerySetEqual(response.context["latest_question_list"], [past_question],)

    def test_two_past_questions(self):
        """Includes multiple past questions with different date and time."""
        q1 = create_question(text="1st question", days=-30)
        q2 = create_question(text="2nd question", days=-5)
        add_choice_to_question(id=q1.id, text="q1 choice")
        add_choice_to_question(id=q2.id, text="q2 choice")
        response = self.client.get(self.url)
        self.assertQuerySetEqual(response.context["latest_question_list"], [q2, q1],)

    def test_question_without_choices(self):
        """Excludes questions without choices."""
        question = create_question(text="Question without choices", days=0)
        response = self.client.get(self.url)
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """Returns 404 HTTP code for future questions."""
        future_question = create_question(text="Future question", days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """Displays the detail view of a question with past publication date."""
        past_question = create_question(text="Past Question", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.text)

    def test_non_existent_question(self):
        """Returns 404 HTTP code for non-existent question."""
        url = reverse("polls:detail", args=(999,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

class QuestionResultsViewTests(TestCase):
    def test_future_question(self):
        """Returns 404 HTTP code for future questions."""
        future_question = create_question(text="Future question", days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """Displays the detail view of a question with past publication date."""
        past_question = create_question(text="Past Question", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.text)

    def test_non_existent_question(self):
        """Returns 404 HTTP code for non-existent question."""
        url = reverse("polls:detail", args=(999,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class QuestionVoteViewTests(TestCase):
    def test_vote_on_choice(self):
        """Increases one vote on choice and redirects to results view."""
        question = create_question(text="Test vote", days=0)
        add_choice_to_question(question.id, text="Test vote choice")
        choice = question.choice_set.get(pk=1)
        url = reverse("polls:vote", args=(question.id,))
        response = self.client.post(url, {"choice": choice.id})
        choice.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertIs(choice.votes, 1)

    def test_no_choice(self):
        """Returns an appropriate message after voting without selected choice."""
        question = create_question("question without choice", days=0)
        url=reverse("polls:vote", args=(question.id,))
        response = self.client.post(url)
        self.assertContains(response, "No choice selected.")


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """Returns False for questions dated after the current date."""
        future_question = create_question("future question", days=30)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """Returns False for questions older than 1 day."""
        old_question = create_question("old question", days=1)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """Returns True for questions published within the current date."""
        question = create_question("question", days=0)
        self.assertIs(question.was_published_recently(), True)

    def test_instance_returns_question_text(self):
        """Returns the text representation of a Question instance."""
        question = create_question("question instance", days=0)
        self.assertEqual(str(question), question.text)

class ChoiceModelTests(TestCase):
    def test_instance_returns_choice_text(self):
        """Returns the text representation of a Choice instance."""
        question = create_question("choice instance", days=0)
        add_choice_to_question(question.id, "choice instance")
        choice = question.choice_set.get(pk=1)
        self.assertEqual(str(choice), choice.text)
