import json
import xbmc
from exception import QobuzXbmcError

def showNotification(**ka):
    rpc = XbmcRPC()
    return rpc.showNotification(**ka)

def ping(**ka):
    rpc = XbmcRPC()
    return rpc.ping(**ka)

"""
    @class: JsonRequest
"""
class JsonRequest:
    def __init__(self, method):
        self.method = method
        self.version = '2.0'
        self.parameters = {}
        self.id = None

    def add_parameters(self, kDict):
        for label in kDict:
            self.parameters[label] = kDict[label]

    def to_json(self):
        jDict = {
                'method': self.method,
                'jsonrpc': self.version,
                'params': self.parameters,
        }
        if self.id:
            jDict['id'] = self.id
        return json.dumps(jDict)

"""
    @class: XbmcRPC
"""
class XbmcRPC:
    def __init__(self):
        pass

    def send(self, request):
        if not request:
            raise QobuzXbmcError(
                who=self, what='missing_parameter', additional='request')
        
        ret = xbmc.executeJSONRPC(request.to_json())
        return ret

    def ping(self):
        request = JsonRequest('JSONRPC.Ping')
        request.id = 1
        return self.send(request)

    def showNotification(self, **ka):
        request = JsonRequest('GUI.ShowNotification')
        request.add_parameters({
            'title' : ka['title'],
            'message': ka['message']
        })
        if ka['displaytime']:
            request.add_parameters({'displaytime': ka['displaytime']})
        if ka['image']:
            request.add_parameters({'image': ka['image']})
        return self.send(request)


