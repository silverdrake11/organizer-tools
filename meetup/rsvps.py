import json
import urllib.request as request


# Fill this part out
EVENT_ID = ''
MEETUP_ID = '_ChiPy_'


RSVPS_API = 'https://api.meetup.com/{}/events/{}/rsvps'
PROFILES_API = 'https://api.meetup.com/{}/members/{}'


def get_rsvps(meetup_id, event_id):
    url = RSVPS_API.format(meetup_id, event_id)
    return get_json(url)


def get_profile(meetup_id, member_id):
    url = PROFILES_API.format(meetup_id, member_id)
    return get_json(url)


def get_json(url):
    response = request.urlopen(url).read()
    return json.loads(response)


def clean_name(name):
    return name.strip().upper().replace('.','')


def is_suspect(name):
    '''If name looks like it may not be a real person's name'''
    name_parts = name.split()
    if len(name_parts) < 2: # One part in name
        return True
    if len(name_parts[0]) < 2: # One letter in first name
        return True
    if len(name_parts[-1]) < 2: # One letter in last name
        return True
    return False


def get_full_name(profile):
    display_name = clean_name(profile['name'])
    name = display_name
    group_profile = profile['group_profile']
    for answers in group_profile['answers']:
        if 'Security' in answers['question']:
            if 'answer' in answers: # They didn't fill it out
                form_name = answers['answer'].strip()
                if form_name:
                    form_name = clean_name(form_name)
                    name = form_name

                    # Add all available info to suspicious looking names
                    if is_suspect(name):
                        if display_name != form_name: # Both names are not the same
                            name = '{} ({})'.format(display_name, form_name)
                        if 'intro' in group_profile:
                            name += ' ' + group_profile['intro']
    return name


if EVENT_ID:
    event_id = EVENT_ID
else:
    event_id = input("What is the Event ID? (found on the URL)\n")
if MEETUP_ID:
    meetup_id = MEETUP_ID
else:
    meetup_id = input("What is ID of the Meetup group? (found on the URL)\n")

people = get_rsvps(meetup_id, event_id)

rsvps = []
for person in people:
    if person['response'] == 'yes': # They RSVPed
        member_id = person['member']['id']
        profile = get_profile(MEETUP_ID, member_id)
        name = get_full_name(profile)
        rsvps.append(name)

for idx, name in enumerate(sorted(rsvps), start=1):
    print(idx, name)
