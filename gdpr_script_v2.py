import json
import re
import requests
import ast
import time

class Globals():
    ZEN_DOMAIN = 'crunchyroll'
    JIRA_DOMAIN = 'ellation'
    VIEW_ID = '00000000'
    START_PAGE = 1
    SLEEP = 0.2
    ERR_AUTH = [400, 401, 402, 403, 404, 405

    # Function to parse request into JSON objects
    def iterparser(j):
        nonspace = re.compile(r'\S')
        decoder = json.JSONDecoder()
        pos = 0
        while True:
            matched = nonspace.search(j, pos)
            if not matched:
                break
            pos = matched.start()
            decoded, pos = decoder.raw_decode(j, pos)
            yield decoded

class Request_Obj():

    def __init__(self, ticket_id, description, requester_email, jira_id=None):
        self.ticket_id = ticket_id
        self.description = description
        self.requester_email = requester_email
        self.jira_id = jira_id

    def set_tick_id(self, tick):
        self.ticket_id = tick

    def set_descrip(self, descrip):
        self.description = descrip

    def set_requester(self, requester):
        self.requester_email = requester

    def set_jira_id(self, jira):
        self.jira_id = jira

    def get_object(self):
        new_obj = {'ticket_id': self.ticket_id, 'description': self.description, 'requester_email': self.requester_email, 'jira_id': self.jira_id}
        return new_obj

class Zendesk_Functions():

    def get_view_url(DOM, ID, page=1):
    return f'https://{DOM}.zendesk.com/api/v2/views/{ID}/tickets.json?page={str(page)}'

    # HTTP Request Stuff
    def retrieve_gdpr_view():
        #credentials = f'{}'
        headers = {'Authorization': f'Basic {credentials}'}
        try:
            r = requests.get(view_url, headers=headers)
            if (r.status_code == 200):
                print('View Retrieval Successful!')
                return r
        except Exception as e:
            print(str(e))
            return None

    def parse_parsed(parsed, li, page=None):
        # Go through each ticket in the object
        for ticket in parsed[0]['tickets']:
            #parse.append(Request_Obj(ticket['id']))
            try:
                # Create a new requester object using the credentials in the ticket and append it to the list
                new_request = Request_Obj(ticket['id'], ticket['description'], ticket['via']['source']['from']['address'])
                li.append(new_request)
            except Exception as e:
                print(f'Exception:: {str(e)}\n\tOn Ticket#:: {ticket["id"]}')
                return None
        # If there is another page to return...
        if parsed[0]['next_page'] != None:

            if page is None:
              page=1
            print(f'Completed Page {page}!')
            # Generate the url for the next page in the view
            n_view_url = get_view_url(ZEN_DOMAIN, VIEW_ID, page+1)

            try:
              n = requests.get(n_view_url, headers=headers)
              if (n.status_code == 200):
                print(f'Page {page+1}s Ticket Retrieval was Successful!')
            except Exception as e:
              print(f'Exception: {str(e)} -- When retreiving page {page+1}')
              return None
            return parse_parsed(list(iterparser(n.text)), li, page+1)
        else:
            print('Weve reached the last page')
        # return our completed list
        return li

    # Adds Jira Key as an internal note to a ticket...
    def zen_comment_internal(rq_obj, dom='crunchyroll'):
        #print(f'\n\nOBJECT::: {rq_obj} \n\n')
        heads = {'Authorization': f'Basic {creds}', 'Content-type': 'application/json'}
        tick_url = f'https://{dom}.zendesk.com/api/v2/tickets/{rq_obj["ticket_id"]}.json'
        tick_dat = {"ticket": {"status": "open", "comment": { "body": rq_obj['jira_id'], "public": False, "author_id": 0000 }}}

        try:
            ir = requests.put(tick_url, data=json.dumps(tick_dat), headers=heads)
            if (r.status_code not in ERR_AUTH):
                print('Comment Post Successful')
                print(str(tick_url))
                print(f'Status: {r.status_code}')
            return ir
        except Exception as e:
            print(str(e))
            print(str(tick_url))
            return None

    # Uses the GDPR Wipe Macro on a given ticket object
    # Also applies the 'gdpr' and 'gdpr_wipe' tags
    # and places the ticket on-hold
    def zen_comment_gdprwipe(rq_obj, dom='crunchyroll'):
        #print(f'\n\nOBJECT::: {rq_obj} \n\n')
        macro_text = 'Hi there. Thank you for \
        your continued patience!'
        macro_tags = ['gdpr', 'gdpr_wipe']
        heads = {'Authorization': f'Basic {creds}', 'Content-type': 'application/json'}
        tick_url = f'https://{dom}.zendesk.com/api/v2/tickets/{rq_obj["ticket_id"]}.json'
        tick_dat = {"ticket": {"status": "hold", "tags": macro_tags, "comment": { "body": macro_text, "public": True, "author_id": 0000 }}}

        try:
            ir = requests.put(tick_url, data=json.dumps(tick_dat), headers=heads)
            if (r.status_code not in ERR_AUTH):
                print('Comment Post Successful')
                print(str(tick_url))
                print(f'Status: {r.status_code}')
            return ir
        except Exception as e:
            print(str(e))
            print(str(tick_url))
            return None

class Jira_Functions():
    #given a request DICTIONARY object (defined above), this creates a
    #new jira issue of type 'Request' in the CS Project
    def jira_post_issue(rq_obj, J_KEY='CS', dom='ellation'):
        jira_post_url = f'https://{dom}.atlassian.net/rest/api/2/issue/'#/createmeta
        jira_post_data = { "fields": {
                                "project": {
                                    "key": J_KEY
                                },
                                "summary": f"GDPR // Wipe // Zendesk#{rq_obj['ticket_id']} // {rq_obj['requester_email']}",
                                "description": f"Customer Message: {{quote}}{rq_obj['description']} {{quote}}",
                                "issuetype": {
                                    "name": "Request"
                                },
                                "labels": [
                                    "gdpr",
                                    "wipe"
                                ]
                                }
                            }

        jhead = {'Content-type': 'application/json'}#,
        try:
            jira_request = requests.post(jira_post_url, headers=jhead, auth=jira_auth, data=json.dumps(jira_post_data))
            print(str(jira_request))
            return jira_request
        except Exception as e:
            print(str(e))
            return None

def main():
    zfun = Zendesk_Functions()
    view_url = zfun.get_view_url(ZEN_DOMAIN, VIEW_ID, START_PAGE
    r = zfun.retrieve_gdpr_view()


    parsed = list(iterparser(r.text))
    out_list = []
    # First confirm that there are additional pages
    out_list = parse_parsed(parsed, out_list)

    zlist = []
    for rq in out_list:
        #print(rq.ticket_id)
        zlist.append(rq.get_object())

    with open('gdpr_awaiting_jira.out', 'w+') as oFile:
        oFile.write(str(zlist))

    active_requests = []
    for item in zlist:
        zreq = jira_post_issue(item)
        if type(zreq) == requests.models.Response and zreq.status_code not in ERR_AUTH:
            print(f'Successfully Created {ast.literal_eval(zreq.text)["key"]} Jira Issue!')
            item['jira_id'] = ast.literal_eval(zreq.text)['key']
            active_requests.append(item)
        else:
            print(f'Error Occured On The Following Item: \n{item}')
        time.sleep(SLEEP)

    # For the Internal Note
    for tester in active_requests:
        try:
            rout = zen_comment_internal(tester)
            #print(f'{rout.text} \n******\n')
        except Exception as e:
            print(str(e))
        time.sleep(SLEEP)

    # For the GDPR Wipe Macro
    for tester in active_requests:
        try:
            rout = zen_comment_gdprwipe(tester)
            #print(f'{rout.text} \n******\n')
        except Exception as e:
            print(str(e))
        time.sleep(SLEEP)

    print('COMPLETE!')



























    # EOF
