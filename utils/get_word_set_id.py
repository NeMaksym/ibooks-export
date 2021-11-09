import json
import urls
import utils
import requests


def get_word_set_id(name, access_token):
    try:
        response = requests.get(
            urls.WORD_SETS,
            params={"withWords": 1},
            headers={'Authorization': 'Bearer ' + access_token}
        )

        word_sets = json.loads(response.text)

        for word_set in word_sets:
            if word_set["title"] == name:
                return word_set["sourceSetId"]

    except Exception as e:
        utils.save_to_log(f"Failed to get the word set ID: {e}")
        return None
