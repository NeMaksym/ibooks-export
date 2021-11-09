import urls
import utils
import requests


def upload_meanings(access_token, word_set_id, meanings):
    try:
        headers = {'Authorization': 'Bearer ' + access_token}
        params = {"sourceSetId": word_set_id, "sourceSetType": "page"}
        data = {"meaningIds": meanings}

        response = requests.post(urls.UPLOAD, headers=headers, params=params, json=data)
        response.raise_for_status()
        return True

    except Exception as e:
        utils.save_to_log(f"Failed to upload meanings: {e}")
        return False
