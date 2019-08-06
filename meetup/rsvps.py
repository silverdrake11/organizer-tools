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


class MeetupAPI:

    def __init__(self, email, password):
        self.session = requests.Session()

        response = self.session.get(LOGIN_URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        login_token = soup.find('input', {'name': 'token'})['value']

        login_data = {'email': email, 
                'password':password,
                'token':login_token,
                'rememberme':'on', 
                'submitButton':'Log in', 
                'returnUri':'https://www.meetup.com/', 
                'op':'login',
                'apiAppClientId':''}

        response = self.session.post(LOGIN_URL, data=login_data)

        cookies = self.session.cookies.get_dict()
        url = RSVPS_API.format(MEETUP_ID, EVENT_ID)
        auth_token = cookies['MEETUP_CSRF']
        self.auth_header = {'Csrf-Token': auth_token}

    def get_rsvps(self, meetup_id, event_id):
        url = RSVPS_API.format(MEETUP_ID, EVENT_ID)
        response = self.session.get(url, headers=self.auth_header)
        return response.json()

    def get_profile(self, member_id):
        url = PROFILES_API.format(MEETUP_ID, member_id)
        response = self.session.get(url, headers=self.auth_header)
        return response.json()


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


meetup = MeetupAPI(MEETUP_EMAIL, MEETUP_PASSWORD)
people = meetup.get_rsvps(MEETUP_ID, EVENT_ID)

rsvps = []
for person in people:
    if person['response'] == 'yes': # They RSVPed
        member_id = person['member']['id']
        profile = meetup.get_profile(member_id)
        name = get_full_name(profile)
        rsvps.append(name)

for idx, name in enumerate(sorted(rsvps), start=1):
    print(idx, name)
