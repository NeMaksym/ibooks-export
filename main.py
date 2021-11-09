import os
import email
import imaplib
import utils
from dotenv import load_dotenv
from email.utils import parseaddr

load_dotenv()

try:
    # Login
    gmail = imaplib.IMAP4_SSL('imap.gmail.com')
    gmail.login(os.environ["GMAIL_EMAIL"], os.environ["GMAIL_PASS"])
    gmail.list()
    gmail.select()

    # Fetch IDs of "new" emails
    _, data = gmail.uid('search', None, "(UNSEEN)")
    email_ids = data[0].split()

    # If have at least 1 mail
    for email_id in email_ids:

        # Fetch email body (RFC822)
        _, data = gmail.uid('fetch', email_id, '(RFC822)')
        raw_email = data[0][1]

        email_message = email.message_from_bytes(raw_email)

        # Read the incoming email address
        incoming_email = parseaddr(email_message["From"])[1]
        if not incoming_email or "@" not in incoming_email:
            utils.save_to_log(f"Failed to read the incoming email address: {email_message['From']}")
            continue

        # Validate email's Subject
        if "notes_from" not in email_message["Subject"].lower():
            utils.save_to_log(f"Wrong email subject: {email_message['Subject']}")
            utils.send_email(to=incoming_email, content='Email subject should start with "Notes from"')
            continue

        # Validate email's maintype
        maintype = email_message.get_content_maintype()
        if maintype != 'multipart':
            utils.save_to_log(f"Wrong email maintype: {maintype}")
            utils.send_email(to=incoming_email, content=f'Email maintype should be "multipart" but got "{maintype}"')
            continue

        # Validate an email has HTML part
        parts = email_message.get_payload()
        html_part = next((part for part in parts if part.get_content_type() == 'text/html'), None)
        if not html_part:
            utils.save_to_log(f"HTML part is missing")
            utils.send_email(to=incoming_email, content="Email doesn't have the HTML part")
            continue

        # Parse HTML
        title, words, skyeng_email, skyeng_pass = utils.parse_html(html_part.get_payload())
        if not title:
            utils.save_to_log(f"Book title is missing")
            utils.send_email(to=incoming_email, content="Book has no title")
            continue
        if len(words) < 1:
            utils.save_to_log(f"Highlighted words are missing")
            utils.send_email(to=incoming_email, content="No highlighted words found. Highlights in purple are expected")
            continue

        # Fetch meanings
        meanings = utils.get_meanings(words)
        if len(meanings) < 1:
            utils.save_to_log(f"Meanings are missing")
            utils.send_email(to=incoming_email, content="Couldn't find a single word in Skyeng dictionary")
            continue

        # Fetch Skyeng access token
        access_token = utils.get_token(skyeng_email or incoming_email, skyeng_pass or os.environ["DEFAULT_SKYENG_PASS"])
        if not access_token:
            utils.save_to_log(f"Access token is missing")
            utils.send_email(to=incoming_email, content="Failed to use Skyeng credentials. "
                                                        "Check them out or try again later")
            continue

        # Get/create word set id
        word_set_id = utils.get_word_set_id(title, access_token) or utils.create_word_set_id(title, access_token)
        if not word_set_id:
            utils.save_to_log(f"Word set ID is missing")
            utils.send_email(to=incoming_email, content="Couldn't create a new word set")
            continue

        # Upload to Skyeng
        upload_status = utils.upload_meanings(access_token, word_set_id, meanings)
        if not upload_status:
            utils.save_to_log(f"Upload request failure")
            utils.send_email(to=incoming_email, content="Something went wrong on upload")
            continue

        # Success
        utils.save_to_log(f"SUCCESS")
        content = f'''
            Words provided: {len(words)}\n"
            Found of them in Skyeng dictionary: {len(meanings)}\n
            Word set name: "{title}"
        '''
        utils.send_email(to=incoming_email, content=content, status=1)

        # Delete successfully processed email
        gmail.uid("store", email_id, '+FLAGS', '\\Deleted')
        gmail.expunge()

    # Logout
    gmail.logout()

except Exception as e:
    utils.save_to_log(f"Something went wrong: {e}")
