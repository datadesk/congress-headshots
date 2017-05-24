import os
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import json

class Command():

    request_headers = {
        "from": "LAT - Los Angeles Times Graphics (yyArtist@tronc.com)",
        "user_agent": "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/1.0.154.53 Safari/525.19",
        "X-API-Key": os.environ['PP_API_KEY'],
    }


    def generate_metadata_from(self, member_id):
        file_name = "/tmp/metadata_%s.json" % (member_id)
        request_prefix = "https://api.propublica.org/congress/v1/members/"
        request_suffix = ".json"
        request_url = "%s%s%s" % (request_prefix, member_id, request_suffix)
        json_data = self.send_request(request_url)
        if json_data["status"] == "OK":
            rep = json_data["results"][0]
            metadata = self.build_json_from(rep)
            print metadata
            with open(file_name, "wb") as f:
                json.dump(metadata, f)
            return file_name


    def send_request(self, url):
        session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        session.mount("http://", HTTPAdapter(max_retries=retries))
        response = session.get(
            url,
            headers=self.request_headers,
            timeout=10,
            allow_redirects=False
        )
        try:
            response.raise_for_status()
            json_response = json.loads(response.content)
            return json_response
        except requests.exceptions.ReadTimeout as exception:
            # maybe set up for a retry, or continue in a retry loop
            logger.error("%s: %s" % (exception, url))
            logger.error("will need to setup retry and then access archived file")
            raise
        except requests.exceptions.ConnectionError as exception:
            # incorrect domain
            logger.error("will need to raise message that we can't connect")
            logger.error("%s: %s" % (exception, url))
            raise
        except requests.exceptions.HTTPError as exception:
            # http error occurred
            logger.error("%s: %s" % (exception, url))
            logger.error("trying to access archived file via failsafe")
            raise
        except requests.exceptions.URLRequired as exception:
            # valid URL is required to make a request
            logger.error("%s: %s" % (exception, url))
            logger.error("will need to raise message that URL is broken")
            raise
        except requests.exceptions.TooManyRedirects as exception:
            # tell the user their url was bad and try a different one
            logger.error("%s: %s" % (exception, url))
            logger.error("will need to raise message that URL is broken")
            raise
        except requests.exceptions.RequestException as exception:
            # ambiguous exception
            logger.error("%s: %s" % (exception, url))
            logger.error("trying to access archived file via failsafe")
            raise


    def build_json_from(self, rep):
        output = {}
        list_of_keys = [
            "member_id",
            "first_name",
            "last_name",
            "gender",
            "date_of_birth",
            "current_party",
        ]
        for key, value in rep.iteritems():
            if key in list_of_keys:
                output[key] = value
        output["full_name"] = "%s %s" % (output["first_name"], output["last_name"])
        output["chamber"] = rep["roles"][0]["chamber"]
        output["title"] = rep["roles"][0]["title"]
        output["state"] = rep["roles"][0]["state"]
        if rep["roles"][0]["chamber"] == "House":
            output["district"] = rep["roles"][0]["district"]
        else:
            output["district"] = None
        output["start_date"] = rep["roles"][0]["start_date"]
        output["end_date"] = rep["roles"][0]["end_date"]
        return output