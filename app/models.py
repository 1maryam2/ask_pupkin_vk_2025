from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.user.username
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

class QuestionManager(models.Manager):
    def new(self):
        return self.order_by('-created_at')
    
    def best(self):
        return self.annotate(likes_count=models.Count('questionlike')).order_by('-likes_count')

class Question(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)
    objects = QuestionManager()
    tags = models.ManyToManyField(Tag, related_name='questions')
    def save(self, *args, **kwargs):
        if not self.pk:  # Для нового вопроса
            self.rating = 0
        super().save(*args, **kwargs)

class Answer(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(default=False)
    rating = models.IntegerField(default=0)
class QuestionLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('user', 'question')

class AnswerLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('user', 'answer')
@receiver([post_save, post_delete], sender=QuestionLike)
def update_question_rating(sender, instance, **kwargs):
    question = instance.question
    new_rating = QuestionLike.objects.filter(question=question).count()
    Question.objects.filter(pk=question.pk).update(rating=new_rating)
@receiver([post_save, post_delete], sender=AnswerLike)
def update_answer_rating(sender, instance, **kwargs):
    answer = instance.answer
    answer.rating = AnswerLike.objects.filter(answer=answer).count()
    answer.save()
print("Все гуд")