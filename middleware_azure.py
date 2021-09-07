#!/usr/bin/env python

"""
Author: Oliver Kieselbach (oliverkieselbach.com)
Script: middleware_azure_sas.py

Description:
This module is meant to plug into munki as a middleware.
https://github.com/munki/munki/wiki

The script will generate the required http headers to interact with an protected Azure blob storage account.
Inspired by S3-Auth (https://github.com/waderobson/s3-auth)

MS reference docs for Storage REST API Auth and interaction
https://docs.microsoft.com/en-us/azure/storage/common/storage-rest-api-auth

Defaults must be in place (replace with your account and example assumes containername = munki):

sudo defaults write /Library/Preferences/ManagedInstalls SoftwareRepoURL 'http://yourstorageaccount.blob.core.windows.net/munki'
sudo defaults write /Library/Preferences/ManagedInstalls SharedAccessSignature 'XXX'

Via MDM profile (plist) also possible:

<key>SoftwareRepoURL</key>
<string>http://yourstorageaccount.blob.core.windows.net/munki</string>
<key>SharedAccessSignature</key>
<string>XXX</string>

Location:
copy to '/usr/local/munki/middleware_azure_sas.py'

Permissions:
sudo chown root /usr/local/munki/middleware*.py
sudo chmod 600 /usr/local/munki/middleware*.py

Debugging log files for munki are stored here:
/Library/Managed Installs/Logs/

If required set LoggingLevel higher than 1 e.g. 2 or 3
sudo defaults write /Library/Preferences/ManagedInstalls LoggingLevel -int 3

Release notes:
Version 1.0: 2021-09-07 - Original published version.

Credits and many thanks to MaxXyzzy for triggering me to evaluate the SAS version once again.

The script is provided "AS IS" with no warranties.
"""

# pylint: disable=E0611
from Foundation import CFPreferencesCopyAppValue
# pylint: enable=E0611

__version__ = '1.0'
BUNDLE_ID = 'ManagedInstalls'


def pref(pref_name):
    # Return a preference. See munkicommon.py for details
    pref_value = CFPreferencesCopyAppValue(pref_name, BUNDLE_ID)
    return pref_value


SHARED_ACCESS_SIGNATURE = pref('SharedAccessSignature')
AZURE_ENDPOINT = pref('AzureEndpoint') or 'blob.core.windows.net'


def process_request_options(options):
    # This is the fuction that munki calls.
    if AZURE_ENDPOINT in options['url']:
        options['url'] = options['url'] + '?' + SHARED_ACCESS_SIGNATURE

    return options
