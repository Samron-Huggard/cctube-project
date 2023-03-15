from keys import client_secret, client_id
import webvtt
import google_auth_oauthlib.flow
import google.oauth2.credentials

from google.oauth2 import service_account
import googleapiclient.discovery
import googleapiclient.errors
from google.cloud import translate_v2 as translate
import io
import os
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import langcodes, language_data
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

translate_credentials = service_account.Credentials.from_service_account_file(
    os.path.abspath('client_secret_file.json'))
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl", "https://www.googleapis.com/auth/youtubepartner"]
api_service_name = "youtube"
api_version = "v3"
authorized = False


flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    os.path.abspath('client_secret_youtube.json'), scopes=scopes)

flow.redirect_uri = 'http://127.0.0.1:5000/'

authorization_url, state = flow.authorization_url(
    # Enable offline access so that you can refresh an access token without
    # re-prompting the user for permission. Recommended for web server apps.
    access_type='offline',
    # Enable incremental authorization. Recommended as a best practice.
    include_granted_scopes='true')


translator = translate.Client(credentials=translate_credentials)
youtube = None


def create_client(credentials):
    youtube_client = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)
    return youtube_client


def get_captions(video_id):
    list_request = youtube.captions().list(part="id", videoId=video_id)
    response = list_request.execute()
    cap_reqeust = youtube.captions().download(id=response["items"][0]["id"], tfmt="vtt")

    cap_response = cap_reqeust.execute()
    f = io.FileIO("maincaptions.vtt", "wb")

    download = MediaIoBaseDownload(f, cap_reqeust)
    complete = False
    while not complete:
        status, complete = download.next_chunk()

    captions = webvtt.read("maincaptions.vtt")

    return captions


def translate_captions(captions, language):
    language = str(langcodes.find(language))
    for caption in captions:
        new_line = translator.translate(caption.text, target_language=language)
        caption.text = new_line["translatedText"]
        captions.save('new_captions.vtt')
    return


# translate_captions(get_captions(), "es")


# def upload_captions(lang_string="spanish"):
#     lang_code = str(langcodes.find(lang_string))
#     request = youtube.captions().insert(
#         part="snippet",
#         body={
#             "snippet": {
#                 "language": lang_code,
#                 "name": lang_string + "-caps",
#                 "videoId": "m5-0OPEQNqA"
#             }
#         },
#         media_body=MediaFileUpload("new_captions.vtt")
#     )
#     response = request.execute()


