from datetime import datetime
from django.db import models

# Create your models here.


class Board(models.Model):
    writer = models.CharField(null=False, max_length=50)
    title = models.CharField(null=False, max_length=200)
    content = models.TextField(null=False)
    hit = models.IntegerField(default=0)
    post_date = models.DateTimeField(default=datetime.now, blank=True)
    filename = models.CharField(null=False, max_length=500,
                                blank=True, default='')
    filesize = models.IntegerField(default=0)
    down = models.IntegerField(default=0)

    def hit_up(self):
        self.hit += 1

    def down_up(self):
        self.down += 1


class Comment(models.Model):
    # CASCADE : 외래키를 받아오는 테이블이 삭제될 때 외래키로 받는 테이블도 삭제
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    writer = models.CharField(null=False, max_length=50)
    content = models.TextField(null=False)
    post_date = models.DateTimeField(default=datetime.now, blank=True)
