import os
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv


load_dotenv()
CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
REDIRECT_URI = os.getenv('LINKEDIN_REDIRECT_URI')


# NOTE: LinkedIn API use requires approved app and correct permissions. The code here
# provides the basic OAuth flow and stubs for uploading and posting. You must register
# the app and get r_liteprofile, r_emailaddress, w_member_social permissions for posting.


AUTH_BASE = 'https://www.linkedin.com/oauth/v2/authorization'
TOKEN_URL = 'https://www.linkedin.com/oauth/v2/accessToken'


def get_auth_url(state, scope=['r_liteprofile','r_emailaddress','w_member_social']):
    params = {
    'response_type': 'code',
    'client_id': CLIENT_ID,
    'redirect_uri': REDIRECT_URI,
    'state': state,
    'scope': ' '.join(scope)
    }
    return f"{AUTH_BASE}?{urlencode(params)}"


def exchange_code_for_access_token(code):
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    r = requests.post(TOKEN_URL, data=data)
    r.raise_for_status()
    return r.json()


# The following are stubs to show how posting would be done. For the MVP we'll
# simulate posting and return a fake post id.


def upload_images_and_create_post(access_token, image_paths, text):
# Real implementation should follow LinkedIn upload registration and asset upload
# docs: https://docs.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/media-api
# For now, return a fake id and pretend success
    return {'post_id': 'fake-post-12345', 'status': 'posted'}