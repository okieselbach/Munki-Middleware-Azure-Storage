## Azure Blob Storage Authentication for Munki

The Azure Blob Storage Middleware allows munki clients to connect securely, and directly to a munki repo hosted in an [Azure Blob Storage](https://azure.microsoft.com/en-us/services/storage/blobs/) account.

### Description
This module is meant to plug into munki as a middleware.
https://github.com/munki/munki/wiki

The latest version **middleware_azure.py** of the script will use the Shared Access Signature from the blob storage account.

Previous version with storage key (middleware_azure_storagekey_deprecated.py) generates the required http headers to interact with an protected Azure blob storage account.
Inspired by S3-Auth (https://github.com/waderobson/s3-auth). I have deprecated the old version as it needs more strict key handling to provide proper security. For research purpose I will keep it for some time here.

MS reference docs for Storage REST API Auth and interaction
https://docs.microsoft.com/en-us/azure/storage/common/storage-rest-api-auth

### Configuration
Defaults must be in place (replace with your account and example assumes containername = munki):

```
sudo defaults write /Library/Preferences/ManagedInstalls SoftwareRepoURL 'http://yourstorageaccount.blob.core.windows.net/munki'
sudo defaults write /Library/Preferences/ManagedInstalls SharedAccessSignature 'XXX'
```

### Configuration via MDM

```
<key>SoftwareRepoURL</key>
<string>http://yourstorageaccount.blob.core.windows.net/munki</string>
<key>SharedAccessSignature</key>
<string>XXX</string>
```

Use Powershell output from below to convert the Shared Access Signature (SAS) to be correctly escaped for usage in xml MDM profile above:
```
[Security.SecurityElement]::Escape("sp=r&st=2021-09-07T07:25:56Z&se=2025-09-07T15:25:56Z&spr=https&sv=2020-08-04&sr=c&sig=ThIsIsEnExAmPlEThIsIsEnExAmPlEThIsIsEnExAmPlE")
```

Check my [macOS GitHub](https://github.com/okieselbach/Intune/tree/master/macOS) repo for a sample MDM .mobileconfig file.

### Location
```
copy to '/usr/local/munki/middleware_azure.py'
```

### Permissions
```
sudo chown root /usr/local/munki/middleware*.py
sudo chmod 600 /usr/local/munki/middleware*.py
```

### Debugging
log files for munki are stored here:

```
/Library/Managed Installs/Logs/
```

If required set LoggingLevel higher than 1 e.g. 2 or 3
```
sudo defaults write /Library/Preferences/ManagedInstalls LoggingLevel -int 3
```

### Further reading
If you are interested in a blog article detailing a bit more of the middleware in action with Microsoft Intune then have a look here:

https://oliverkieselbach.com/2021/07/14/comprehensive-guide-to-managing-macos-with-intune/
