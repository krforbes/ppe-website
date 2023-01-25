from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from .models import *
from django.contrib.auth import authenticate, login, logout
import pandas as pd
from django.utils import timezone
from .matchings import *
import random

main_url = '/app/'
login_url = main_url+'login/'
schedule_url = main_url+'schedule/'
no_url = main_url+'no/'
pref_md_url = main_url+'preferences/md/'
availability_url = main_url+'availability/'
mcalpin_url = main_url+'availability/mcalpin/'
schedule_md_url = main_url+'schedule/md/'


days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
times = [str(i)+':00' for i in range(7, 24)]



# this can be improved tbh and it can be 2 functions + a version for ints 
def read_string_to_lists(data_str):
    stripped = data_str[1:-1] # remove [ and ]
    data_list = stripped.split(',') # BY ROW!!!! EVEN THOUGH ITS WEIRD
    for i in range(len(data_list)): # remove leading/trailing whitespace
        s = data_list[i]
        s = s.strip() 
        if s[0] == '\'':
            s = s[1:]
        if s[-1] == '\'':
            s = s[:-1]
        data_list[i] = s
    data_2d = []
    for i in range(len(times)):
        sublist = data_list[7*i:7*(i+1)]
        pairs = [(days[j], sublist[j]) for j in range(7)]
        data_2d.append((times[i], pairs))
    return data_list, data_2d

def str_to_int_list(data_str):
    stripped = data_str[1:-1]
    data_list = stripped.split(',')
    for i in range(len(data_list)):
        data_list[i] = int(data_list[i])
    return data_list


###################################################################################
#
#    LOGIN THINGS
#
###################################################################################

def login_action(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect(main_url)
    else:
        return HttpResponseRedirect(login_url)

def login_page(request):
    template = loader.get_template('app/login_page.html')
    context = {
    }
    return HttpResponse(template.render(context, request))

def logout_action(request):
    request.user.profile.cursed_with_comic_sans = False # resets if you log out
    request.user.profile.save()
    logout(request)
    return HttpResponseRedirect(login_url)

def not_md(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(login_url)
    # you get rickrolled with probability 1/5
    r = random.random()
    if r < 0.2:
        return HttpResponseRedirect('https://youtu.be/dQw4w9WgXcQ')
    # also 1/5 probability of this
    if r < 0.4: 
        request.user.profile.cursed_with_comic_sans = True 
        request.user.profile.save()
        comic_sans=True
        riddles=False
    else:
        comic_sans = False
        riddles = True
    template = loader.get_template('app/not_md.html')
    context = {
        'user': request.user,
        'comic_sans': comic_sans,
        'riddles': riddles,
    }
    return HttpResponse(template.render(context, request))

def riddle_success(request):
    confirm = request.POST['success']
    if confirm == 'yes':
        request.user.profile.has_cat = True
        request.user.profile.save()
    template = loader.get_template('app/index.html')
    context = {
        'user': request.user,
    }
    return HttpResponse(template.render(context, request))

def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(login_url)
    template = loader.get_template('app/index.html')
    context = {
        'user': request.user,
    }
    return HttpResponse(template.render(context, request))

# this should probably exist but it's not working??? 
def change_password_setup(request): # enter username to get emailed a code 
    return HttpResponseRedirect('/accounts/password_change')

def go_to_admin_site(request):
    return HttpResponseRedirect('/admin/')


###################################################################################
#
#    PIECE ASSIGNMENT THINGS
#
###################################################################################

def preferences(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(login_url)
    template = loader.get_template('app/preferences.html')
    context = {
        'user': request.user,
        'pieces': Piece.objects.all(),
    }
    return HttpResponse(template.render(context, request))

def save_preferences(request):
    pref = []
    if request.POST['hard'] == 'yes':
        pref.append(1) # hard 
    else:
        pref.append(0)
    if request.POST['hard'] != 'no':
        pref.append(1) # expHard
    else:
        pref.append(0)
    if request.POST['multiple'] == 'yes':
        pref.append(1) # multiple
    else:
        pref.append(0)
    if request.POST['multiple'] != 'no':
        pref.append(1) # expMultiple
    else:
        pref.append(0)
    # make sure piece list is consistent alphabetical order bc otherwise this might break
    piece_names = [piece.name for piece in Piece.objects.all()]
    piece_names.sort()
    for piece in piece_names:
        if request.POST[piece] == 'yes':
            pref.append(1)
        else:
            pref.append(0)
    request.user.profile.pref = str(pref)
    request.user.profile.pref_comments = request.POST['comments'].strip()
    request.user.profile.pref_updated = timezone.now()
    request.user.profile.save()
    return HttpResponseRedirect(main_url)

def preferences_md(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(login_url)
    if not request.user.is_staff:
        return HttpResponseRedirect(no_url)
    template = loader.get_template('app/preferences_md.html')
    # NEED TO ADD LIST OF PEOPLE TO CHASE DOWN
    schedule = Schedule.objects.get(name = 'schedule')
    missing = []
    for user in User.objects.all():
        if user.profile.pref_updated < schedule.pref_reset:
            missing.append(user)
    # list of pieces and their current players
    pieces_players = []
    piece_names = [piece.name for piece in Piece.objects.all()]
    piece_names.sort() # we like alphabetical order 
    for piece_name in piece_names:
        piece = Piece.objects.get(name = piece_name)
        current = []
        performers = piece.performer_string.split(',')
        if len(performers) != piece.num_pianists: # initialize if needed
            performers = ['' for i in range(piece.num_pianists)]
        for i in range(piece.num_pianists):
            current.append((i+1, performers[i]))
        pieces_players.append((piece, current))
    # comments 
    comments = []
    for user in User.objects.all():
        if user.profile.pref_comments != '':
            comments.append((user.username, user.profile.pref_comments))
    # matching string becomes a list 
    matching_list = schedule.matching_string.split('.')
    full_list = []
    for substring in matching_list:
        piece_list = substring.split(';')
        full_list.append(piece_list)
    # table of preferences
    table = []
    for user in User.objects.all():
        row = []
        pref = str_to_int_list(user.profile.pref)
        if user.profile.pref_updated >= schedule.pref_reset and len(pref) == len(Piece.objects.all())+4:
            if pref[0]==1 and pref[1] == 1: 
                row.append('yes')
            elif pref[0] == 0:
                row.append('maybe')
            else:
                row.append('no')
            if pref[2]==1 and pref[3] == 1: 
                row.append('yes')
            elif pref[2] == 0:
                row.append('maybe')
            else:
                row.append('no')
            for i in range(len(piece_names)):
                row.append(pref[i+4])
            table.append((user.username, row))
    context = {
        'user': request.user,
        'users': User.objects.all(),
        'pieces': Piece.objects.all(),
        'piece_names': piece_names,
        'pieces_players': pieces_players,
        'comments': comments,
        'missing': missing,
        'matching_string': schedule.matching_string,
        'matching_list': full_list,
        'table': table,

    }
    return HttpResponse(template.render(context, request))

def preferences_generate(request): 
    # update pieces and users with new assignment
    username_list = [user.username for user in User.objects.all()]
    for piece in Piece.objects.all():
        performer_string = ''
        performer_list = []
        for i in range(piece.num_pianists):
            query = piece.name + ' '+str(i+1)
            username = request.POST[query].strip()
            if username in username_list: # no whitespace or empty strings 
                user = User.objects.get(username = username)
                performer_list.append(user)
            performer_string += username + ', '
        piece.performers.set(performer_list)
        if performer_string != '':
            performer_string = performer_string[:-2] # remove last comma space 
        piece.performer_string = performer_string
        # calculate size of group (arrangers + performers)
        size = len(piece.performers.all())
        for arranger in piece.arrangers.all():
            if arranger not in piece.performers.all():
                size += 1
        piece.group_size = size 
        piece.save()
    # create df 
    hard = request.POST['hard']
    multiple = request.POST['multiple']
    columns_initial = ['hard', 'expHard','multiple','expMultiple']
    piece_names = [piece.name for piece in Piece.objects.all()] 
    piece_names.sort() # making sure the order is consistent with preferences order 
    columns = columns_initial + piece_names 
    rows_initial = ['easy parts', 'hard parts']
    rows = rows_initial.copy()
    # depending on expMultiple or multiple, people get a row or not 
    schedule = Schedule.objects.get(name = 'schedule')
    for user in User.objects.all(): 
        if user.profile.pref_updated < schedule.pref_reset: # ignore people who didn't fill out the form 
            continue 
        pref = str_to_int_list(user.profile.pref)
        if len(pref) != len(columns): # if not default then set to all 0
            pref = [0 for i in columns]
        if len(user.playing.all()) > 1: # no more pieces for them
            continue 
        if len(user.playing.all()) == 1: 
            if multiple == 'multiple' and pref[2] == 0: # multiple only for those who specifically asked for it
                continue
            if multiple == 'expMultiple' and pref[3] == 0: # multiple if necessary
                continue 
        rows.append(user.username)
    df = pd.DataFrame(index = rows, columns = columns)
    for column in df.columns:
        if column in columns_initial:
            for row in rows_initial:
                df.at[row, column] = 0 # we don't care about these
        else:
            piece = Piece.objects.get(name = column)
            df.at['hard parts', column] = piece.num_hard_parts
            df.at['easy parts', column] = piece.num_pianists - piece.num_hard_parts
    for user in User.objects.all():
        pref = str_to_int_list(user.profile.pref)
        if len(pref) != len(df.columns): # if not default then set to all 0
            pref = [0 for i in df.columns]
        if user.username in df.index: 
            df.loc[user.username] = pref
            if len(user.playing.all()) == 1: # if they're already on multiple they don't get 3 AND they can't be on a piece they're already playing! 
                df.at[user.username, 'multiple'] = 0
                df.at[user.username, 'expMultiple'] = 0
        for piece in user.playing.all():
            # if they are willing to play a hard part and one exists, assume they get it
            if ((hard == 'hard' and pref[0] == 1) or (hard == 'expHard' and pref[1] == 1)) and (df.at['hard parts', piece.name] > 0): 
                df.at['hard parts', piece.name] -= 1
            elif df.at['easy parts', piece.name] > 0:
                df.at['easy parts', piece.name] -= 1 
            else: # bug prevention. hopefully you never give people hard parts they didn't ask for
                df.at['hard parts', piece.name] -= 1
            if user.username in df.index:
                df.at[user.username, piece.name] = 0 # they can't play multiple parts of the same piece 
    # generate suggestions
    m = Matching(df, hard, multiple)
    full_string = ''
    for i in range(10): 
        m.shuffle()
        pairs = m.match_all()
        m_string = ''
        for piece in piece_names:
            piece_string = piece + ': '
            group = []
            for pair in pairs:
                if pair[0] == piece:
                    group.append(pair[1])
            group.sort()
            for person in group:
                piece_string += person + ', '
            if piece_string[-2] == ',':
                piece_string = piece_string[:-2] # take off last comma 
            m_string += piece_string + ';'
        full_string += m_string + '.'
    schedule.matching_string = full_string
    schedule.save()
    return HttpResponseRedirect(pref_md_url)



###################################################################################
#
#    AVAILABILITY THINGS
#
###################################################################################

def availability(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(login_url)
    template = loader.get_template('app/availability.html')
    data_str = request.user.profile.availability # is a 1D array for now
    data_list, data_2d = read_string_to_lists(data_str)
    context = {
        'user': request.user,
        'thing': request.user.username,
        'data_str': data_str,
        'data_list': data_list,
        'data_2d': data_2d,
        'days': days,
        'times': times,
    }
    return HttpResponse(template.render(context, request))

def update_piece_availability(piece):
    # modify later to separate arrangers vs no arrangers 
    new_list = empty_list.copy()
    # also calculate the piece group size at some point
    for user in piece.performers.all():
        stripped = user.profile.availability[1:-1] # remove [ and ]
        data_list = stripped.split(',') # BY ROW!!!! EVEN THOUGH ITS WEIRD
        for i in range(len(new_list)):
            new_list[i] += int(data_list[i])
    for user in piece.arrangers.all():
        if user not in piece.performers.all(): 
            stripped = user.profile.availability[1:-1] # remove [ and ]
            data_list = stripped.split(',') # BY ROW!!!! EVEN THOUGH ITS WEIRD
            for i in range(len(new_list)):
                new_list[i] += int(data_list[i])
    piece.availability = str(new_list)
    piece.save()


def save_availability(request):
    data_list = []
    for time in times:
        for day in days:
            data_list.append(int(request.POST[day+" "+time]))
    request.user.profile.availability = str(data_list)
    request.user.profile.availability_updated = timezone.now()
    request.user.profile.save()
    for piece in request.user.arranged.all():
        update_piece_availability(piece)
    for piece in request.user.playing.all():
        update_piece_availability(piece)
    return HttpResponseRedirect(availability_url)

def save_mcalpin(request):
    data_list = []
    for time in times:
        for day in days:
            data_list.append(int(request.POST[day+" "+time]))
    schedule = Schedule.objects.get(name = 'schedule')
    schedule.availability = str(data_list)
    schedule.save()
    return HttpResponseRedirect(mcalpin_url)


def availability_view(request, name):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(login_url)
    if name == 'mcalpin':
        category = 'mcalpin'
        thing = Schedule.objects.get(name = 'schedule')
    else:
        try:
            thing = User.objects.get(username = name)# SOMETHING
            category = 'user'
        except User.DoesNotExist:
            try:
                thing = Piece.objects.get(name=name)
                update_piece_availability(thing)
                category = 'piece'
            except Piece.DoesNotExist:
                raise Http404("This is not a valid availability page")
    # check for permission to access this page - people can see their own availability and their groups' but not others except MDs
    if (not request.user.is_staff) and((category == 'user' and not request.user.username == name) or (category == 'piece' and request.user not in thing.performers.all() and request.user not in thing.arrangers.all())):
        return HttpResponseRedirect(no_url)
    if category == 'user':
        data_str = thing.profile.availability # REPLACE WITH NAME'S AVAILABILITY
        arrangers = []
        performers = []
        template = loader.get_template('app/availability_view.html')
    elif category == 'piece':
        data_str = thing.availability
        arrangers = thing.arrangers.all()
        performers = thing.performers.all()
        template = loader.get_template('app/availability_view.html')
    else: # mcalpin 
        data_str = thing.availability
        arrangers = []
        performers = []
        if request.user.is_staff:
            template = loader.get_template('app/availability_mcalpin.html')
        else:
            template = loader.get_template('app/availability_view.html')
    data_list, data_2d = read_string_to_lists(data_str)
    colors = []
    # set up colours for group availability
    if category == 'piece':
        # get number of people in the group including arrangers
        size = len(performers)
        for a in arrangers: 
            if a not in performers:
                size += 1
        incr = 255//(size + 1)
        for i in range(size+1):
            g = 255-i*incr
            rgb = 65536*g + 256*255 + g
            colors.append('#{0:0=6x}'.format(rgb)) # hex code for colours going from white to green
        colors[size] = '#00cc00' # make sure this is darkest 
    else:
        colors = ['#ffffff', '#00cc00']
    data_colors = []
    data_ints = str_to_int_list(data_str) 
    for i in range(len(times)):
        sublist = data_list[7*i:7*(i+1)]
        triples = [(days[j], sublist[j], colors[data_ints[7*i + j]]) for j in range(7)]
        data_colors.append((times[i], triples))
    context = {
        'user': request.user,
        'thing':name, 
        'is_user': (category == 'user'),
        'data_str': data_str,
        'data_list': data_list,
        'data_2d': data_2d,
        'data_colors': data_colors,
        'days': days,
        'times': times,
        'arrangers': arrangers,
        'performers': performers,
        'mcalpin': Schedule.objects.get(name = 'schedule').availability,
        'colors': colors,
    }
    return HttpResponse(template.render(context, request))

def availability_md(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(login_url)
    if not request.user.is_staff:
        return HttpResponseRedirect(no_url)
    template = loader.get_template('app/availability_md.html')
    missing = []
    schedule = Schedule.objects.get(name = 'schedule')
    compare_date = schedule.availability_reset
    for profile in Profile.objects.all():
        if profile.availability_updated < compare_date:
            missing.append(profile.user)
    context = {
        'user': request.user,
        'missing': missing,
        'pieces': Piece.objects.all()
    }
    return HttpResponse(template.render(context, request))


###################################################################################
#
#    SCHEDULING THINGS
#
###################################################################################

def schedule(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(login_url)
    template = loader.get_template('app/schedule.html')
    data_str = Schedule.objects.get(name = 'schedule').pieces # is a 1D array for now
    data_list, data_2d = read_string_to_lists(data_str)
    piece_names = [piece.name for piece in Piece.objects.all()]
    data_colors = []
    for i in range(len(times)):
        sublist = data_list[7*i:7*(i+1)]
        triples = []
        for j in range(7):
            possible_string = '' # potentially the last word is a room number 
            split = sublist[j].split()
            if len(split) > 1:
                for k in range(len(split)-1):
                    possible_string += split[k]
            if sublist[j] in piece_names:
                piece = Piece.objects.get(name = sublist[j])
                triples.append((days[j], sublist[j], piece.color))
            elif possible_string in piece_names:
                piece = Piece.objects.get(name = possible_string)
                triples.append((days[j], sublist[j], piece.color))
            else:
                triples.append((days[j], sublist[j], '#ffffff'))
        data_colors.append((times[i], triples))
    context = {
        'user': request.user,
        'thing': request.user.username,
        'data_str': data_str,
        'data_list': data_list,
        'data_2d': data_2d,
        'data_colors': data_colors,
        'days': days,
        'times': times,
    }
    return HttpResponse(template.render(context, request))

def schedule_md(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(login_url)
    if not request.user.is_staff:
        return HttpResponseRedirect(no_url)
    template = loader.get_template('app/schedule_md.html')
    schedule = Schedule.objects.get(name = 'schedule')
    data_str = schedule.pieces # is a 1D array for now
    data_list, data_2d = read_string_to_lists(data_str)
    piece_names = [piece.name for piece in Piece.objects.all()]
    data_colors = []
    for i in range(len(times)):
        sublist = data_list[7*i:7*(i+1)]
        triples = []
        for j in range(7):
            possible_string = '' # potentially the last word is a room number 
            split = sublist[j].split()
            if len(split) > 1:
                for k in range(len(split)-1):
                    possible_string += split[k]
            if sublist[j] in piece_names:
                piece = Piece.objects.get(name = sublist[j])
                triples.append((days[j], sublist[j], piece.color))
            elif possible_string in piece_names:
                piece = Piece.objects.get(name = possible_string)
                triples.append((days[j], sublist[j], piece.color))
            else:
                triples.append((days[j], sublist[j], '#ffffff'))
        data_colors.append((times[i], triples))
    context = {
        'user': request.user,
        'data_str': data_str,
        'data_list': data_list,
        'data_2d': data_2d,
        'data_colors': data_colors,
        'days': days,
        'times': times,
        'piece_list': Piece.objects.all(),
        'piece_names': piece_names,
        'mcalpin': schedule.availability,
    }
    return HttpResponse(template.render(context, request))

def schedule_new(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(login_url)
    if not request.user.is_staff:
        return HttpResponseRedirect(no_url)
    template = loader.get_template('app/schedule_new.html')
    schedule = Schedule.objects.get(name = 'schedule')
    data_str = schedule.availability
    data_list, data_2d = read_string_to_lists(data_str)
    max_hours = 0
    for entry in data_list:
        max_hours += int(entry)
    context = {
        'username': request.user.username,
        'is_admin': request.user.is_staff,
        'days': days,
        'times': times,
        'piece_list': Piece.objects.all(),
        'max_hours': max_hours,
    }
    return HttpResponse(template.render(context, request))


def schedule_generate(request):
    # get data from form and set up DF 
    # columns of DF are the unneeded ones and the available mcalpin times as indices 
    schedule = Schedule.objects.get(name = 'schedule')
    columns = ['hard', 'expHard', 'multiple', 'expMultiple']
    mcalpin_list, mcalpin_2d = read_string_to_lists(schedule.availability)
    for i in range(len(mcalpin_list)): 
        if mcalpin_list[i] == '1':
            columns.append(str(i))
    # rows of DF are one row per hour of rehearsal per piece 
    rows = ['hard parts', 'easy parts']
    for piece in Piece.objects.all():
        hours = request.POST[piece.name + '_hours']
        for i in range(int(hours)):
            rows.append(piece.name + ' '+str(i))
    data = pd.DataFrame(columns=columns, index = rows)
    # create entries in DF
    for row in data.index:
        if row == 'hard parts':
            for column in data.columns:
                data.at[row, column] = 0
            continue
        if row == 'easy parts':
            for column in data.columns:
                data.at[row, column] = 1
            continue
        piece = Piece.objects.get(name=row.split()[0])
        for column in data.columns:
            if column in ('hard', 'expHard', 'multiple', 'expMultiple'):
                data.at[row, column] = 0
                continue
            i = int(column)
            available = True
            if request.POST[piece.name + '_arrangers'] == 'Yes':
                for arranger in piece.arrangers.all():
                    if not arranger.profile.is_available(i):
                        available = False
            for performer in piece.performers.all():
                if not performer.profile.is_available(i):
                    available = False
            if available:
                data.at[row, column] = 1
            else:
                data.at[row, column] = 0    
    # generate partial matching using the piece assignments code
    m = Matching(data)
    m.shuffle()
    p = PartialMatching(m.left, m.right, m.null, m)
    # convert to schedule 
    schedule_list = none_list.copy() # start with empty schedule
    for pair in p.pairs:
        timeslot = int(pair[0])
        piece = pair[1].split()[0] # take out number 
        schedule_list[timeslot] = piece
    schedule.pieces = str(schedule_list)
    schedule.save()
    return HttpResponseRedirect(schedule_md_url)

def save_schedule(request):
    data_list = []
    for time in times:
        for day in days:
            data_list.append(request.POST[day+" "+time])
    schedule = Schedule.objects.get(name = 'schedule')
    schedule.pieces = str(data_list)
    schedule.save()
    return HttpResponseRedirect(schedule_md_url)


def library(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(login_url)
    template = loader.get_template('app/library.html')
    context = {
        'user': request.user,
    }
    return HttpResponse(template.render(context, request))



