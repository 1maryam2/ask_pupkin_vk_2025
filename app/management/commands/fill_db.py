from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from faker import Faker
from app.models import Profile, Question, Answer, Tag, QuestionLike, AnswerLike
from datetime import datetime, timezone
import random
from tqdm import tqdm

class Command(BaseCommand):
    help = 'Populates the database with test data'
    
    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Base ratio for data generation')

    def handle(self, *args, **options):
        ratio = options['ratio']
        fake = Faker()
        
        # Calculate counts based on ratio
        counts = {
            'users': ratio,
            'tags': ratio,
            'questions': ratio * 10,
            'answers': ratio * 100,
            'likes': ratio * 200
        }

        self.stdout.write(f"Generating data with ratio {ratio}:")
        self.stdout.write(f"- Users: {counts['users']}")
        self.stdout.write(f"- Tags: {counts['tags']}")
        self.stdout.write(f"- Questions: {counts['questions']}")
        self.stdout.write(f"- Answers: {counts['answers']}")
        self.stdout.write(f"- Likes: {counts['likes']}")
        try:
            with transaction.atomic():
                # Create users with progress bar
                self.stdout.write("\nCreating users...")
                users = []
                for i in tqdm(range(counts['users'])):
                    user = User(
                        username=f'user_{i}',
                        email=f'user_{i}@example.com',
                        password='testpass123'
                    )
                    users.append(user)
                created_users = User.objects.bulk_create(users)
                
                # Create profiles
                Profile.objects.bulk_create([
                    Profile(user=user, avatar=None) for user in created_users
                ])

                # Create tags
                self.stdout.write("\nCreating tags...")
                tags_set = set()
                while len(tags_set) < counts['tags']:
                    tags_set.add(fake.word() + str(fake.random_int(min=1, max=10000)))
                tags = Tag.objects.bulk_create([Tag(name=name) for name in tags_set])

                # Create questions with tags
                self.stdout.write("\nCreating questions...")
                questions = []
                for _ in tqdm(range(counts['questions'])):
                    questions.append(Question(
                        title=fake.sentence()[:200],
                        content=fake.text(),
                        author=random.choice(created_users),
                        created_at=fake.date_time_this_year(tzinfo=timezone.utc),
                        rating=random.randint(0, 100)
                    ))
                created_questions = Question.objects.bulk_create(questions)
                
                # Add tags to questions
                self.stdout.write("\nAdding tags to questions...")
                for q in tqdm(created_questions):
                    q.tags.set(random.sample(tags, random.randint(1, 3)))

                # Create answers
                self.stdout.write("\nCreating answers...")
                answers = []
                question_list = list(created_questions)  # For faster random access
                for _ in tqdm(range(counts['answers'])):
                    answers.append(Answer(
                        question=random.choice(question_list),
                        author=random.choice(created_users),
                        content=fake.paragraph(),  # ← Правильное поле
                        created_at=fake.date_time_this_year(tzinfo=timezone.utc)
                    ))
                created_answers = Answer.objects.bulk_create(answers)

                # Create likes
                self.stdout.write("\nCreating likes...")
                question_likes = []
                answer_likes = []
                answer_list = list(created_answers)
                
                for _ in tqdm(range(counts['likes'])):
                    user = random.choice(created_users)
                    if random.choice([True, False]):
                        question_likes.append(QuestionLike(
                            user=user,
                            question=random.choice(question_list)
                        ))
                    else:
                        answer_likes.append(AnswerLike(
                            user=user,
                            answer=random.choice(answer_list)
                        ))
                
                QuestionLike.objects.bulk_create(question_likes, ignore_conflicts=True)
                AnswerLike.objects.bulk_create(answer_likes, ignore_conflicts=True)

            self.stdout.write(self.style.SUCCESS('\nDatabase successfully populated!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))