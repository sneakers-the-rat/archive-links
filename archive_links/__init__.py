from pathlib import Path
import argparse
import re
import typing
import sys

import requests
import waybackpy
from tqdm import tqdm

url_pattern = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
url_re = re.compile(url_pattern)

user_agent = "Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0"

file_path = Path().cwd() / 'archive_links'/'test_doc.txt'

subs = (
    '\).*$',
    '^.*\('
)
"""
Regex patterns to try substituting in find_active_url
"""

def find_active_url(url:str, verbose:bool=False, timeout:float=1) -> typing.Union[bool, str]:
    """
    Since our regex matches every legal URL, but sometimes we will do silly
    things like write urls in ``(https://parentheses.com)`` we
    try to see if the url is active, then try a few string strips
    to make it work.

    Args:
        url (str): Url to test

    Returns:
        url that was active, or ``False`` if none
    """
    active_url = False

    r = requests.get(url,timeout=timeout)

    if r.status_code == 200:
        active_url = url
    else:
        # TODO: all combinations of replacement strs instead of iteratively which doesnt really make sense
        if verbose:
            print('no active url found, trying substrings')
        test_url = url
        for sub_str in subs:
            test_url = re.sub(sub_str, '', test_url)
            r = requests.get(test_url, timeout=timeout)
            if r.status_code == 200:
                active_url = test_url
                break

    return active_url


def get_archive_link(url:str, force_archive:bool=False,  verbose=False):
    """
    Test whether a url is in the wayback machine, if it's not,
    save it. then return the archive url

    Args:
        url ():

    Returns:

    """
    wb_url = waybackpy.Url(url)

    if wb_url.archive_url is None or force_archive:
        if verbose:
            print(f'Archiving {url}...')
        wb_url.save()

    return wb_url.archive_url

def replace_url(text, url, force_archive=False, verbose=False, timeout:float=1) -> str:
    if verbose:
        print(f'finding active url for {url}')
    active_url = find_active_url(url, verbose=verbose, timeout=timeout)
    if not active_url:
        # see if it has been archived before anyway
        # but don't try and save
        if verbose:
            print(f"no active url found for {url}, trying to get archive link anyway")
        archive_url = waybackpy.Url(url).archive_url
        if archive_url is None:
            raise Exception(f"url {url} was not active, and no existing archive.org link could be found")
        else:
            # well by jove it exists after all
            active_url = url

    else:
        if verbose:
            print(f"finding archive link for {active_url}")
        archive_url = get_archive_link(active_url, force_archive,verbose=verbose)

    return re.sub(re.escape(active_url), archive_url, text)

def archive_text(text:str,
                 force_archive:bool=False,
                 verbose:bool=False,
                 timeout:float=1.0):

    # find all urls in document
    urls = list(set(url_re.findall(text)))

    desc_pbar = tqdm(position=0)

    # hold urls that couldnt be archive converted
    bad_urls = []

    try:
        for url in tqdm(urls, position=1):
            desc_pbar.set_description(url)
            try:
                text = replace_url(text, url, force_archive=force_archive, verbose=verbose, timeout=timeout)
            except Exception as e:
                bad_urls.append(url)
                if verbose:
                    print(e)
    except KeyboardInterrupt:
        pass

    if len(bad_urls)>0:

        bad_print_str = '\n'.join(bad_urls)
        print(f'Couldnt convert {len(bad_urls)} urls:\n\n{bad_print_str}')


    return text




