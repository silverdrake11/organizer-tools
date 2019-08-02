from bs4 import BeautifulSoup
import requests


# Fill this part out
MEETUP_EMAIL = ''
MEETUP_PASSWORD = ''
EVENT_ID = ''
MEETUP_ID = '_ChiPy_'


RSVPS_API = 'https://api.meetup.com/{}/events/{}/rsvps'
PROFILES_API = 'https://api.meetup.com/{}/members/{}'
LOGIN_URL = 'https://secure.meetup.com/login/'


def get_full_name(profile):
    display_name = profile['name'].strip().upper()
    name = display_name
    group_profile = profile['group_profile']
    for answers in group_profile['answers']:
        if 'Security' in answers['question']:
            if 'answer' in answers: # They didn't fill it out
                form_name = answers['answer'].strip()
                if form_name:
                    form_name = form_name.upper()
                    name = form_name

                    # Add all available info to suspicious looking names
                    name_parts = form_name.split() 
                    if len(name_parts) < 2:
                        name = '{} ({})'.format(display_name, form_name)
                        if 'intro' in group_profile:
                            name += ' ' + group_profile['intro']
                        name = '??? ' + name
    return name


session = requests.Session()

response = session.get(LOGIN_URL)
soup = BeautifulSoup(response.text, 'html.parser')
login_token = soup.find('input', {'name': 'token'})['value']

login_data = {'email': MEETUP_EMAIL, 
        'password':MEETUP_PASSWORD,
        'token':login_token,
        'rememberme':'on', 
        'submitButton':'Log in', 
        'returnUri':'https://www.meetup.com/', 
        'op':'login',
        'apiAppClientId':''}
response = session.post(LOGIN_URL, data=login_data)

cookies = session.cookies.get_dict()
url = RSVPS_API.format(MEETUP_ID, EVENT_ID)
auth_token = cookies['MEETUP_CSRF']
auth_header = {'Csrf-Token': auth_token}
response = session.get(url, headers=auth_header)
people = response.json()

rsvps = []
for person in people:
    if person['response'] == 'yes': # They RSVPed
        member_id = person['member']['id']
        url = PROFILES_API.format(MEETUP_ID, member_id)
        response = session.get(url, headers=auth_header)
        profile = response.json()
        name = get_full_name(profile)
        rsvps.append(name)

for idx, name in enumerate(sorted(rsvps), start=1):
    print(idx, name)



