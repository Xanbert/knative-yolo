#manage mongo

#https://www.runoob.com/python3/python-mongodb.html

import pymongo #pymongo-3.9.0 https://pypi.org/project/pymongo/
from bson.objectid import ObjectId

#run mongo server `$./mongod`

MONGO_HOST = "localhost"
MONGO_PORT = "27017"

class mongodbController:
    def __init__(self,MONGO_HOST=MONGO_HOST,MONGO_PORT=MONGO_PORT):
        url = "{}:{}".format(MONGO_HOST,MONGO_PORT)
        self.mongoclient = pymongo.MongoClient(url, username='test', password='password', authSource='comp4651')
        self.comp4651DB = self.mongoclient["comp4651"] #DB name
        self.processCol = self.comp4651DB["process"] #user process collection

    def getObjectId(self,idstring):
        return ObjectId(idstring)

    def listCollection(self):
        print(self.comp4651DB.list_collection_names())

    def dropCollection(self,colname):
        if colname in self.comp4651DB.list_collection_names():
            self.comp4651DB[colname].drop()
            print("remove: ",colname)

    #status: pending, done, removed
    #===================users process============================#

    #return objectid string
    def insertUserProcess(self,username,status="submitted"):
        return str(self.processCol.insert_one(
            {"username":username,"status":status}
        ).inserted_id)

    #status="done"
    #return True if updated
    def updateUserProcess(self,userid,status="done"):
        objectid = self.getObjectId(userid)
        if self.getUserProcess(objectid)=="removed":
            print("Userid{} data is removed".format(objectid))
            return False
        else:
            self.processCol.update_one(
                {"_id":objectid},
                {"$set": {"status":status}}
            )
            return True

    #return status
    def getUserProcess(self,userid):
        objectid = self.getObjectId(userid)
        result = self.processCol.find_one({"_id":objectid})
        if result == None:
            return False
        return result["status"]
    #print(getUserProcess(ObjectId("5de71d051d7cf1955bd01da5")))

    #return user objectId or False for not found
    def getUserID(self,username,status="pending"):
        result = self.processCol.find_one({"username":username,"status":status})
        # result = self.processCol.find({"username":username, "status" : {$not: "removed"}})
        # for x in result:
        #    #if x["status"]!="removed":
        #    return str(x["_id"])
        if result == None:
            return False
        return str(result["_id"])

    def dropUserProcessCol(self):
        self.dropCollection("process")

    #===================user image=============================#

    #return collection name
    def createuserdb(self,username,replace=False):
        colname = "user_"+str(username)
        if replace:
            #remove username status=submitted,pending,done
            self.processCol.update_many(
                {"username":username},
                { "$set": { "status": "removed" }}
            )
            self.dropCollection(colname)
        return colname

    #userid: user object id
    #return objectid
    def insertoneBase64(self,username,userid,frameno,imagename,base64):
        return self.comp4651DB["user_"+str(username)].insert_one(
            {"frameno":frameno,"name":imagename,"userid":userid,"base64":base64}
        ).inserted_id

    #return base64
    def getBase64(self,username,userid,frameno):
        result = self.comp4651DB["user_"+str(username)].find_one(
            {"frameno":frameno,"userid":userid}
        )
        return result["base64"]

    #find by objectid
    #return base64
    def getBase64ById(self,username,objectid):
        result = self.comp4651DB["user_"+str(username)].find_one(
            {"_id":objectid}
        )
        return result["base64"]

    def getAImage(self,username,userid,frameno):
        return self.comp4651DB["user_"+str(username)].find_one(
            {"frameno":frameno,"userid":userid}
        )

    #return all dict sort by frame number
    def getAllImage(self,username,userid):
        '''
        for x in result:
            print(x["frameno"],x["name"])
        '''
        return self.comp4651DB["user_"+str(username)].find({"userid":userid}).sort("frameno")

#db = mongodbController(gvar.MONGO_HOST,gvar.MONGO_PORT)
