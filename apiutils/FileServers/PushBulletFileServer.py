import json
import mimetypes
import os
import sys
import time
from datetime import date, datetime

import pytz
import requests
from tzlocal import get_localzone


def prettify(d: dict) -> str:
    return json.dumps(d, indent=4)

class PushBulletFileServerException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class exceptions:
    class BadServerResponseError(PushBulletFileServerException):
        '''Thrown when PushBullet server response is not successful, returns information about the response if available'''
        def __init__(self, code, message=None):
            super().__init__('Code: {}{}'.format(code, ', Response: "{}"'.format(message) if message is not None else ''))


    class InvalidParameters(PushBulletFileServerException):
        '''Thrown when given method parameters are invalid or inadequate'''
        def __init__(self, msg):
            super().__init__(msg)

    class InvalidConfiguration(PushBulletFileServerException):
        '''Thrown when method encounters an error with the provided parametes'''
        def __init__(self, msg):
            super().__init__(msg)

    class UnreachableServerAddress(PushBulletFileServerException):
        '''Thrown when given server path is unreachable, i.e. outside address bounds'''
        def __init__(self, address):
            super().__init__(f'Provided address "{address}" is unreachable!')

    class InvalidServerAddress(PushBulletFileServerException):
        def __init__(self, address):
            super().__init__(f'Provided address "{address}" is invalid! Addresses must be absolute!')


class PushBulletFileServer():
    # simple file server using the pushbullet server as a save location
    PUSHBULLET_API = 'https://api.pushbullet.com/v2'
    __INDEX_PUSH_TITLE = 'PushBullet File Server File Index'
    __INDEX_FILE_NAME = 'PBFS_File_Index.json'
    __MODEL_INDEX_TAG = 'PBFS_INDEX'

    VERSION = 1.0
    DEVICE_MANUFACTURER = 'PushBullet File Server'
    
    def __init__ (  self, access_token, 
                    index: dict=None,
                    serverName: str=None, # server, corresponds to device on pushbullet
                    serverIden: str=None, # identity of the server
                    createServer:bool=False, # make the device if it does not exist
                    loadIndexFromServer: bool=False,
                    persistentStorage:bool=False
                ):
        '''
        PushBullet File Server Constructor
        - `access_token` is the access token for the PushBullet account
        - `index`is an input file index to initialize with
        - `serverName` is the name of the server device on PushBullet
        - `createServer` creates a device with the name `server_name` on PushBullet if it does not already exist
        - `serverIden` is the identifier string of the server device on PushBullet
        - `loadIndexFromServer` is used to load the file index from the server, will only work if file index was uploaded before using `upload_file_index()` or setting `persistent_storage`
        - `persistentStorage`, set to true if push bullet server storage should be persistent (i.e. file index is saved to server and loaded from server)
        '''
        # double underscore prepend means private members and methods
        self.__accessToken = access_token
        self.errorMsg = '' # used to track errors
        self.__serverIden = self.__getServerIden(serverName, serverIden, createServer)

        # if the storage is persistent, we want to upload the file index every time we do a file action
        # that way, the file index will always be the last thing uploaded to the server
        self.__persistentStorage = persistentStorage

        self.__index = {}
        self.__indexIden = None

        if index is not None:
            self.__index = index
        
        elif loadIndexFromServer or persistentStorage:
            retrievedIndex, iden = self.__getIndexFromServer()
            if retrievedIndex is not None:
                self.__index = retrievedIndex
                self.__indexIden = iden

        # print('Server Index:')
        # print(self.__index)

    def __getServerIden(self, name, iden, createServer):
        if iden is not None:
            return iden

        if name is not None:
            devInfo = self.getPBFSDevice(name=name)
            if devInfo is not None:
                return devInfo['iden']

            # did not find it, create server if required
            if createServer:
                return self.makePBFSDevice(name)['iden']
    
        return None

    def __makeRequestHeader(self):
        return {'Access-Token': self.__accessToken}

    def __getIndexFromServer(self):
        '''
        Returns the index uploaded to the file server if any,
        Returns None if nothing was found
        '''
        svrDev = self.getPBFSDevice(iden=self.__serverIden)
        if svrDev is None:
            return None, None
        
        model = svrDev['model']
        if not model.startswith(PushBulletFileServer.__MODEL_INDEX_TAG):
            return None, None
        
        indexIden = model.split(':')[1]

        if indexIden == 'None' or indexIden == '':
            return None, None
        
        # get the file index using the identifier
        indexFile = self.__pull(indexIden)

        return json.loads(indexFile['content'].decode('utf-8')), indexIden

    def successfulHTTPResponse(response:requests.Response):
        return 200 <= response.status_code and response.status_code <= 299

    def errIfBadResponse(response:requests.Response):
        # based on https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
        if not PushBulletFileServer.successfulHTTPResponse(response):
            # raise a bad server response error
            try:
                msg = response.json()
            except requests.exceptions.JSONDecodeError:
                msg = None
            raise exceptions.BadServerResponseError(response.status_code, message=msg)
        
        return True

    def __push(self, text=None, link: str = None, title: str=None, filepath: str =None, file=None, limitFileSize: bool = True) -> dict:
        """
        Pushes text, URLS (links) and files to the pushbullet server
        - `filepath` is the path to the file on the local system
        - `file` is a tuple which is in the format of ( <file name>, <file binary content> )
        - `limit_file_size` is a boolean which limits file sizes to 25 MB, set to false if you use pushbullet premium
        """
        if text is None and link is None and filepath is None and file is None:
            # Nothing to push
            raise exceptions.InvalidParameters('Nothing to push!')
        
        pushRequest = {
            # method is post
            'headers' : self.__makeRequestHeader(),
            'body' : {
                'type': '',
                'url': '',
                'body': '',
                'file_name' : '',
                'file_type' : '',
                'file_url' :''
            }
        }

        pushBody = pushRequest['body']

        if title is not None:
            pushBody['title'] = 'Test Title!'

        if self.__serverIden is not None:
            pushBody['source_device_iden'] = self.__serverIden

        if text is not None:
            pushBody['type'] = 'note'
            pushBody['body'] = str(text)

        elif link is not None:
            pushBody['type'] = 'link'
            pushBody['url'] = link

        elif filepath is not None or file is not None:
            if filepath is not None and file is not None:
                raise exceptions.InvalidParameters('Undetermined file source!')


            if filepath is not None:
                # check if the file exists
                if not os.path.exists(filepath):
                    raise exceptions.InvalidConfiguration(f'File "{filepath}" does not exist!')
                
                filename = os.path.split(filepath)[1]
                fileContents = open(filepath, 'rb').read()
            else:
                # we are doing file
                try:
                    filename , fileContents = file
                except ValueError:
                    raise exceptions.InvalidParameters('File tuple to push is used incorrectly!')

            fileMimeType, _ = mimetypes.MimeTypes().guess_type(filename)

            # check if its under the limit
            if limitFileSize:
                # checks if file is greater than 25 MB
                if ( (sys.getsizeof(fileContents) +33) / (1024*1024)) > 25:
                    raise exceptions.InvalidConfiguration('File size is too big!')

            # make upload request
            # by here should have filename, file_mime_type, file_contents

            response = requests.post(
                '{}/upload-request'.format(PushBulletFileServer.PUSHBULLET_API),
                headers = pushRequest['headers'],
                json = {
                    'file_name': filename,
                    'file_type': fileMimeType,
                }
            )

            PushBulletFileServer.errIfBadResponse(response)

            # get upload url from upload request
            # and us to upload acutal file
            uploadResponse = response.json()

            uploadURL = uploadResponse['upload_url']

            response = requests.post(
                uploadURL,
                headers = pushRequest['headers'],
                files = {
                    'file' : fileContents
                }
            )
            PushBulletFileServer.errIfBadResponse(response)

            # populate push body
            pushBody['type'] = 'file'
            pushBody['file_name'] = uploadResponse['file_name']
            pushBody['file_type'] = uploadResponse['file_type']
            pushBody['file_url'] = uploadResponse['file_url']
        
        # push the contents
        response = requests.post('{}/pushes'.format(PushBulletFileServer.PUSHBULLET_API), headers=pushRequest['headers'], json=pushBody)
        PushBulletFileServer.errIfBadResponse(response)

        # return good success
        return response.json()

    def __pull(self, identifier: str) -> dict:
        '''
        Returns the server contents for the given identifier.
    
        Returns dictionary which contains:
        
        `type`: the type of content for the identifier i.e. note,link or file

        `content`: The actual content, this would be the body, URL or binary file content

        `file_name`: Only included if the type is a file
        '''
        # get the response from the request
        response = requests.get('{}/pushes/{}'.format(PushBulletFileServer.PUSHBULLET_API, identifier), headers=self.__makeRequestHeader())
        PushBulletFileServer.errIfBadResponse(response)

        res = response.json()

        ret = {
            'type': res['type'],
            'file_name': '',
            'content': ''
        }

        if res['type'] == 'note':
            ret['content'] =  res['body']

        elif res['type'] == 'link':
            ret['content'] = ['url']

        elif res['type'] == 'file':
            # get the file content from the url
            ret['file_name'] = res['file_name']

            response = requests.get(res['file_url'])

            # return content in binary
            ret['content'] = response.content

        return ret

    def __delete(self, identifier):
        '''
        Deletes push with the given identifier
        '''
        res = requests.delete( '{}/pushes/{}'.format(PushBulletFileServer.PUSHBULLET_API, identifier), headers = self.__makeRequestHeader())

        PushBulletFileServer.errIfBadResponse(res)

    def __check_path( path:str):
        if not path.startswith('/'):
            raise exceptions.InvalidServerAddress(path)

    def __sanitize_path(path:str):
        '''
        Makes `path` a valid server path by:
        - Adding root address separator e.g. `path/to/file.txt` becomes `/path/to/file.txt`
        - Removing ending separator e.g. `path/to/dir/` becomes `/path/to/dir`
        - Removing multiple continuous slashes e.g. `/path//path` becomes `/path/path`
        '''

        # split the path by our address separator
        comps = path.split('/')

        # filter out the empty slots to account for multiple slashes
        sanitized_comps = list(filter(
            lambda part: part != '',
            comps
        ))

        # remake the address cleanly
        sanitized_path = '/' + '/'.join(sanitized_comps)

        return sanitized_path

    def __getParentDir(self, path:str, makeDirsOk=False) -> dict:
        ''' Returns the dict object in file `index` corresponding to the parent directory the given path'''
        path = PushBulletFileServer.__sanitize_path(path)
        paths = path.split('/')
        directoryStack = []
        curDir = self.__index

        for dir in paths[1:-1]: # not including last one as it is the leaf
            # push the current directory to the stack
            directoryStack.append(curDir)

            if dir == '.':
                # just pop what was last pushed to the stack
                curDir = directoryStack.pop()
            elif dir == '..':
                # get the upper address, pop two things from the stack
                directoryStack.pop()
                if len(directoryStack) < 1:
                       raise exceptions.UnreachableServerAddress(path)
                curDir = directoryStack.pop()

            else:
                curDir = curDir.get(dir)

            if curDir is None:
                # the directory does not exist
                if not makeDirsOk:
                    return None

                # then we have to create the directory at the upper addrss
                if len(directoryStack) < 1:
                    raise exceptions.UnreachableServerAddress(path)

                # make directory at upper address (last item on stack)
                directoryStack[-1][dir] = {}
                curDir = directoryStack[-1][dir]

        return curDir

    # PUBLIC MEMBERS ---------------------------------------------------------------

    def dateTimeToUnixTimestamp(date:datetime=None):
        if not date:
            # if no date is specified, use now
            return int(time.time())

        # get the UTC and current timezones
        utc_timezone = pytz.timezone("UTC")
        local_timezone = get_localzone()

        # initialize epoch date and put in UTC timezone
        epoch = datetime.strptime('Jan 01 1970 00:00:00 UTC', '%b %d %Y %H:%M:%S %Z')
        epoch = utc_timezone.localize(epoch)

        # Make date timezone aware if not already and localize to the current timezone
        if not date.tzinfo:	date.replace(tzinfo=local_timezone)

        # localize the date to the utc timezone
        date = date.astimezone(utc_timezone)

        # calculate the unix time stamp by subtracting current date and epoch
        difference = date - epoch
        unix_timestamp = difference.total_seconds()

        return unix_timestamp


    def getLatestPushes(self, limit:int=None, modifiedAfter:int=None):
        """
        Gets latest pushes from the server
        - `limit` is the maximum number of pushes to retrieve
        - `modified_after` is to retrieve pushes only modified after this time
        """
        # index should be last push to the server, of type note and title 'pbfs_index'
        body = {
            'active': 'true'
        }

        if limit is not None:
            body['limit'] = str(limit)

        if modifiedAfter is not None:
            body['modified_after'] = str(modifiedAfter)

        # make the request
        response = requests.get('{}/pushes'.format(PushBulletFileServer.PUSHBULLET_API), headers = self.__makeRequestHeader(), params = body)

        PushBulletFileServer.errIfBadResponse(response)

        return response.json()['pushes']

    def clear_server_from_time(self, dt:datetime=None, dtstr:str=None) -> int:
        """
        Clears any pushes to the server from this device made after the specified time. This does not update the file index and is only intended for easy server debugging and maintenance.
        Pushes will be deleted only if there is a device assigned to the PBFS object
        - `date_time` is a datetime object containing the specified time
        - `date_time_str` is a string of the specified time following the format: `%b %d %Y %H:%M` e.g. `Dec 29 2022 07:50`, `Oct 03 2011 21:43` etc
        - Returns the number of pushes deleted
        """

        if dt is None:
            if dtstr is None:
                return 0

            # parse the time from the datetime str
            dt = datetime.strptime(dtstr, '%b %d %Y %H:%M')
        
        if self.__serverIden is None:
            return 0

        # retrieve any pushes modified aft6er specified time
        pushes = self.getLatestPushes(modifiedAfter=PushBulletFileServer.dateTimeToUnixTimestamp(dt))

        # filter pushes where the device identity is the server
        pushes = list( filter(
            lambda push: push['source_device_iden'] == self.__serverIden,
            pushes
        ))

        if len(pushes) == 0:
            return 0

        # delete the pushes
        for p in pushes:
            self.__delete(p['iden'])

        return len(pushes)

    def makePBFSDevice(self, name:str) -> dict:
        '''
        Makes a PushBullet File Server device on the Push Bullet Server
        '''
        headers =  self.__makeRequestHeader()

        body = {
            'nickname': name,
            'model': f'{PushBulletFileServer.__MODEL_INDEX_TAG}:None',
            'manufacturer': PushBulletFileServer.DEVICE_MANUFACTURER,
            'push_token': '',
            'icon': 'system',
            'has_sms': False
        }

        response = requests.post('{}/devices'.format(PushBulletFileServer.PUSHBULLET_API), headers=headers, json=body)
        PushBulletFileServer.errIfBadResponse(response)

        return response.json()

    def getPBFSDevice(self, name:str=None, iden:str=None):
        '''
        Get a PushBullet File Server device from the PushBullet Server, using the device name `name` or the device identifier `iden`
        '''
        if name is None and iden is None:
            raise exceptions.InvalidParameters('No device name or device identifier')

        if name is not None and iden is not None:
            raise exceptions.InvalidParameters('Undetermined device search query (both name and identifier are set)')

        headers =  self.__makeRequestHeader()

        # filter by name and iden if they exist
        response = requests.get('{}/devices'.format(PushBulletFileServer.PUSHBULLET_API), headers=headers)
        PushBulletFileServer.errIfBadResponse(response)

        devices = response.json()['devices']

        applicable_devices = list(filter(
        lambda dev: (dev.get('manufacturer') == PushBulletFileServer.DEVICE_MANUFACTURER) and (name is None or dev.get('nickname') == name) and (iden is None or dev.get('iden') == iden), 
        devices))

        if len(applicable_devices) != 1:
            return None

        return applicable_devices[0]

    def deleteDevice(self, name:str=None, iden:str=None):
        '''
        Delete device from the PushBullet Server, using the device name `name` or the device identifier `iden`
        '''
        devInfo = self.getPBFSDevice(name=name, iden=iden)
        
        if devInfo is None:
            return 0

        devIden = devInfo['iden']

        response = requests.delete('{}/devices/{}'.format(PushBulletFileServer.PUSHBULLET_API, devIden), headers=self.__makeRequestHeader())
        PushBulletFileServer.errIfBadResponse(response)

    def pathExistsInIndex(self, path:str) -> bool:
        ''' Checks if the given path exists in the index'''
        # get the parent directory if it exists
        parentDir = None
        try:
            parentDir = self.__getParentDir(path)
        except exceptions.UnreachableServerAddress:
            return None

        # the parent directory does not exist
        if parentDir is None:
            return False

        if parentDir.get(path.split('/')[-1]) is None:
            # file does not exist in the parent directory
            return False

        return True    

    def createDirs(self, dirpath:str):
        # creates the given directory path
        # adding throwaway so that get parent directory can handle the making of the directory
        dirpath += "/throwaway"
        parent_dir = self.__getParentDir(dirpath, makeDirsOk=True)        
        return 0


    def deleteFile(self, filePath: str) -> int:
        '''
        Deletes file from server at given path
        '''
        # get the file identifier and parent directory
        if not self.pathExistsInIndex( filePath ):
            self.errorMsg = 'File does not exist!'
            return 1
        
        filename = filePath.split('/')[-1]
        parentDir = self.__getParentDir(filePath)
        fileIden = parentDir[filename]

        # delete the file from the server
        try:
            self.__delete(fileIden)
        except PushBulletFileServerException as e:
            self.errorMsg = 'Failed to delete file: {}'.format(e)
            return 1

        # remove the file from the index
        parentDir.pop(filename)

        if self.__persistentStorage:
            self.uploadFileIndex()

        return 0

    def write(self, destPath: str, fileBinary) -> str:
        ''' 
        Takes absolute file path using Linux addressing, e.g /path/to/file where / is the top most directory.
        `binary_contents` is the binary contents of the file to be uploaded
        Returns the uploaded path if successful
        '''

        destPath = PushBulletFileServer.__sanitize_path(destPath)
        
        # upload the contents to the pushbullet server first, make sure that is completed
        filename = destPath.split('/')[-1]
        svrResponse = None

        try:
            svrResponse = self.__push(file=(filename, fileBinary))
        except PushBulletFileServerException as e:
            # if something went wrong, then exit with the error
            self.errorMsg = 'Error: '+str(e)
            return None

        newFileIden = svrResponse['iden']

        # add the file path to the index, with the server file identifier
        parentDir = self.__getParentDir(destPath, makeDirsOk=True)

        # checks if there is a current file in the memory
        oldFileIden = parentDir.get(filename)

        # if there is then delete the old file since we are overwriting it
        if oldFileIden is not None:
             # delete the file from the server
            try:
                self.__delete(oldFileIden)
            except PushBulletFileServerException as e:
                self.errorMsg = 'Failed to delete file: {}'.format(e)

        # save the new file by updating the file index
        parentDir[filename] = newFileIden

        if self.__persistentStorage:
            self.uploadFileIndex()

        return destPath

    def read(self, file_path:str):
        ''' 
        Returns binary contents of file posted to server
        '''
        # get the file identifier
        if not self.pathExistsInIndex( file_path ):
            self.errorMsg = 'File does not exist!'
            return None
        
        filename = file_path.split('/')[-1]
        file_identifier = self.__getParentDir(file_path)[filename]

        # retrieve the file contents from the pushbullet server
        ret = None
        try:
            ret = self.__pull(file_identifier)
        except PushBulletFileServerException as e:
            self.errorMsg = str(e)
            return None

        return ret['content']

    def uploadFileIndex(self):
        '''
        Uploads the latest version of the index to the server, allows for persisitent file storage
        (Makes the server now act like actual storage instead of RAM)
        Also deletes an older version if it exists
        '''
        # Push the current version of the index and get the identifier
        resp = self.__push(file=(PushBulletFileServer.__INDEX_FILE_NAME, json.dumps(self.__index).encode()))
        newIden = resp['iden']


        # Store the identifier in the model of the server (JANK AF)
        updatedDevice = {
            'model': f'{PushBulletFileServer.__MODEL_INDEX_TAG}:{newIden}'
        }
        requests.post(f'{PushBulletFileServer.PUSHBULLET_API}/devices/{self.__serverIden}', headers=self.__makeRequestHeader(), json=updatedDevice)
        
        if self.__indexIden is not None:
            self.__delete(self.__indexIden)
            self.__indexIden = newIden
        

    def resetIndex(self):
        '''
        Resets the file index to an empty repository
        '''
        self.__index = {}
        self.uploadFileIndex()

    def writeFrom(self, local_path, server_path):
        '''
        Uploads file at `local_path` on local device to `server_path` on server
        '''
        with open(local_path, 'rb') as file:
            return self.write(server_path, file.read())

    def readTo(self, server_path, local_path):
        '''
        Downloads file at `server_path` on server to `local_path` on local device
        '''
        with open(local_path, 'wb') as file:
            content = self.read(server_path)
            if content is not None:
                file.write(content)


    def getFileIndex(self):
        return dict(self.__index)

    def getServerIdentifier(self):
        return self.__serverIden
    
    def publicPush(self, text=None, link: str = None, title: str=None, filepath: str =None, file=None, limitFileSize: bool = True):
        self.__push(text=text, link=link, title=title, filepath=filepath, file=file, limitFileSize=limitFileSize)



def main():
    return 0
    

if __name__ == "__main__":
    sys.exit(main())
