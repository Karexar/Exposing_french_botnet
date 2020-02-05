import re
from tld_list import *

# Parse a text to retrieve a list of urls
def get_urls_from_text(text):
    if text is None:
        return None
    else:
        pattern = re.compile(r'(' +
                              '(?:https?:\/\/)?' + # protocol
                              '(?:www\.)?' + # www
                              '(?:[-a-zA-Z0-9@:%_\+~#=]{1,256}\.)+' + # (sub)domains
                              '(?:' + tld_list + ')' + #'[a-z]{2,6}' + # top level domain
                              '(?:\/[-a-zA-Z0-9@%_\+~#?&//=]*)*' + # subfolders and page
                              '(?:\:\d{1,4}\/?)?)' +#+ # port number
                              '(?:\s|\W|$)')
        urls = pattern.findall(text)
        return urls
