from django.db import models
import datetime

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
times = [str(i//4+7)+':'+str(15*(i%4)).zfill(2) for i in range((24-7)*4)]
empty_list = [0 for i in range(len(days)*len(times))]
none_list = ['' for i in range(len(days)*len(times))]
EMPTY_SCHEDULE = str(empty_list)
NONE_SCHEDULE = str(none_list)



# Create your models here.

from django.contrib.auth.models import User

class Piece(models.Model):
    name = models.CharField(max_length = 20)
    composer = models.CharField(max_length = 200)
    title = models.CharField(max_length = 200)
    num_pianists = models.IntegerField(default=4)
    num_pianos = models.IntegerField(default=4)
    num_hard_parts = models.IntegerField(default = 1)
    extras = models.CharField(max_length = 200, blank = True)
    length = models.IntegerField(default = 6)
    arrangers = models.ManyToManyField(User, related_name = 'arranged', blank = True)
    performers = models.ManyToManyField(User, related_name = 'playing')
    group_size = models.IntegerField(default = 0)
    performer_string = models.CharField(max_length = 1000, default = '', blank = True)
    availability = models.CharField(max_length = 1000, default = EMPTY_SCHEDULE)
    color = models.CharField(max_length = 10, default = '#ffffff')
    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pref = models.CharField(max_length = 1000, default = '[0]', blank = True)
    pref_comments = models.CharField(max_length = 10000, default = '', blank = True)
    availability = models.CharField(max_length = 1000, default = EMPTY_SCHEDULE)
    pref_updated = models.DateTimeField('last updated preferences')
    availability_updated = models.DateTimeField('last updated availability')
    cursed_with_comic_sans = models.BooleanField(default=False) # don't ask
    has_cat = models.BooleanField(default = False)
    def is_available(self, index):
        ''' returns whether the person is available at a given index in the availability lists '''
        stripped = self.availability[1:-1] # remove [ and ]
        data_list = stripped.split(',') # BY ROW!!!! EVEN THOUGH ITS WEIRD
        for i in range(len(data_list)): # remove leading/trailing whitespace
            s = data_list[i]
            s = s.strip()
            if s[0] == '\'':
                s = s[1:]
            if s[-1] == '\'':
                s = s[:-1]
            data_list[i] = s
        return data_list[index]=='1'
    def __str__(self):
        if self.has_cat:
            return "*"
        else:
            return ' '


class Schedule(models.Model): # this is really just global variables
    pieces = models.CharField(max_length = 5000, default = NONE_SCHEDULE) # schedule itself
    availability = models.CharField(max_length = 1000, default = EMPTY_SCHEDULE) # mcalpin availability
    name = models.CharField(max_length = 10, default = 'schedule') # for finding the schedule
    pref_reset = models.DateTimeField('last reset preferences')
    availability_reset = models.DateTimeField('last reset availability')
    matching_string = models.CharField(max_length = 10000, default = '', blank = True) # for sending suggested matchings back to md page

    def __str__(self):
        return "This is just for global variables"


