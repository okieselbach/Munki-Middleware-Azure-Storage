#!/usr/bin/env python

"""
Author: Oliver Kieselbach (oliverkieselbach.com)
Script: middleware_azure.py

Description:
This module is meant to plug into munki as a middleware.
https://github.com/munki/munki/wiki

The script will generate the required http headers to interact with an protected Azure blob storage account.
Inspired by S3-Auth (https://github.com/waderobson/s3-auth)

MS reference docs for Storage REST API Auth and interaction
https://docs.microsoft.com/en-us/azure/storage/common/storage-rest-api-auth

Defaults must be in place (replace with your account and example assumes containername = munki):

sudo defaults write /Library/Preferences/ManagedInstalls SoftwareRepoURL 'http://yourstorageaccount.blob.core.windows.net/munki'
sudo defaults write /Library/Preferences/ManagedInstalls StorageAccountKey 'XXX'

Via MDM profile (plist) also possible:

<key>SoftwareRepoURL</key>
<string>http://yourstorageaccount.blob.core.windows.net/munki</string>
<key>StorageAccountKey</key>
<string>XXX</string>

Location:
copy to '/usr/local/munki/middleware_azure.py'

Permissions:
sudo chown root /usr/local/munki/middleware*.py
sudo chmod 600 /usr/local/munki/middleware*.py

Debugging log files for munki are stored here:
/Library/Managed Installs/Logs/

If required set LoggingLevel higher than 1 e.g. 2 or 3
sudo defaults write /Library/Preferences/ManagedInstalls LoggingLevel -int 3

Release notes:
Version 1.0: 2021-06-10 - Original published version.

The script is provided "AS IS" with no warranties.
"""

from time import gmtime, strftime
import time
import hashlib
import hmac
import base64
from urllib.parse import urlparse

# pylint: disable=E0611
from Foundation import CFPreferencesCopyAppValue
# pylint: enable=E0611

__version__ = '1.0'
BUNDLE_ID = 'ManagedInstalls'


def pref(pref_name):
    # Return a preference. See munkicommon.py for details
    pref_value = CFPreferencesCopyAppValue(pref_name, BUNDLE_ID)
    return pref_value


STORAGE_ACCOUNT_KEY = pref('StorageAccountKey')
AZURE_ENDPOINT = pref('AzureEndpoint') or 'blob.core.windows.net'


def uri_from_url(url):
    parse = urlparse(url)
    return parse.path


def storage_account_name_from_url(url):
    parse = urlparse(url)
    return parse.hostname.replace('.{}'.format(AZURE_ENDPOINT),'')


def azure_blob_storage_auth_headers(url, etag, last_modified):
    # Here we are going to add the http headers for Azure blob storage authentication.

    date_time = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
    api_version = '2020-06-12'
    canonical_headers = 'x-ms-date:{}\nx-ms-version:{}\n'.format(date_time, api_version)

    storage_account_name = storage_account_name_from_url(url)
    uri = uri_from_url(url)
    canonical_resource = '/{}{}'.format(storage_account_name, uri)

    # reference implemention for simple GET does not need all the headers, it needs only this:
    # message_signature = 'GET\n\n\n\n\n\n\n\n\n\n\n\n{}{}'.format(canonical_headers, canonical_resource)

    # as Munki middleware has an option 'download_only_if_changed = True' we need to take care of the 
    # 'last-modified' and 'etag' header in the signature otherwise we get an error similar to this: 
    # The MAC signature found in the HTTP request '<used-encoded-signature>' is not the same as any computed signature. 
    # Server used following string to sign: <signature-string>
    message_signature = 'GET\n\n\n\n\n\n\n{}\n\n{}\n\n\n{}{}'.format(last_modified, etag, canonical_headers, canonical_resource)

    key = base64.b64decode(STORAGE_ACCOUNT_KEY)
    signed_string = hmac.new(key, message_signature.encode('utf-8'), hashlib.sha256).digest()
    signature = base64.b64encode(signed_string).decode('utf-8')

    authorization_header = ('SharedKey {}:{}').format(storage_account_name, signature)
    
    headers = {'x-ms-date': date_time,
               'x-ms-version': api_version,
               'Authorization': authorization_header}

    return headers


def process_request_options(options):
    # This is the fuction that munki calls.
    if AZURE_ENDPOINT in options['url']:
        etag = ''
        last_modified = ''
        
        if options['download_only_if_changed'] == True:
            etag = options['cache_data']['etag']
            last_modified = options['cache_data']['last-modified']

        headers = azure_blob_storage_auth_headers(options['url'], etag, last_modified)
        options['additional_headers'].update(headers)
    return options