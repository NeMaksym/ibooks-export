import utils
import quopri
from lxml.html import fromstring


def parse_html(email_content):
    try:
        decoded_content = quopri.decodestring(email_content)
        html = fromstring(decoded_content)

        # Grab book's title
        h1 = html.find_class('booktitle')
        title = h1[0].text_content().strip() if h1 else None

        # Get Skyeng credentials from email
        skyeng_email = None
        skyeng_pass = None
        insertions = html.xpath('//p[@id="insertionheader"]')
        for el in insertions:
            el_content = el.text_content().strip().lower()
            email = el_content.partition("email: ")[2]
            password = el_content.partition("password: ")[2]
            if email and not skyeng_email: skyeng_email = email
            if password and not skyeng_pass: skyeng_pass = password

        # Find words in annotations
        annotations = html.find_class('annotation')
        words = []
        for annotation in annotations:
            if annotation.find_class('annotationselectionMarker purple'):
                text_node = annotation.find_class('annotationrepresentativetext')
                if text_node:
                    content = text_node[0].text_content()
                    if content:
                        word = content.strip()
                        if word not in words:
                            words.append(word)

        return title, list(dict.fromkeys(words)), skyeng_email, skyeng_pass

    except Exception as e:
        utils.save_to_log(f"Failed to parse HTML: {e}")
        return None, None, None, None
