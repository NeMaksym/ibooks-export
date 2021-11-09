import urls
import json
import utils
import hashlib
import requests


def create_word_set_id(title, access_token):
    try:
        # source_set_id (aka word_set_id) == hashed word set title
        source_set_id = hashlib.sha1(title.encode("utf-8"))

        params = {"withWords": 1}  # Skyeng API just requires that
        headers = {'Authorization': 'Bearer ' + access_token}
        data = {
            "create_wordset": {
                "title": title,
                "subtitle": "",
                "imageUrl": "",
                "sourceSetId": source_set_id.hexdigest(),
                "sourceSetType": "page",
                "sourceSetMeta": {
                    "url": "",
                    "imageUrl": ""
                }
            }
        }

        response = requests.post(urls.WORD_SETS, params=params, headers=headers, json=data)
        response.raise_for_status()

        return json.loads(response.text).get("sourceSetId")

    except Exception as e:
        utils.save_to_log(f"Failed to create a word set id: {e}")
        return None
