import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import uvicorn
from fastapi import FastAPI
import requests
import json
from src.settings import SERVICE_HOST, SERVICE_PORT, SERVICE_LOG_LEVEL

if not firebase_admin._apps:
    cred = credentials.Certificate('serviceAccountKey.json')
    firebase_admin.initialize_app(cred)

app = FastAPI()

URL = "https://6u3td6zfza.execute-api.us-east-2.amazonaws.com/prod/ad/vast"

@app.get("/getAd/{sdkVer}/{sessionId}/{platForm}/{usrName}/{countryCode}/")
async def getAd(sdkVer: str, sessionId: str, platForm: str, usrName: str, countryCode: str):

    dbconn = firestore.client()

    await insertOrUpdateUserNumOfADReq(usrName, dbconn)
    await insertOrUpdateSDKVerNumOfADReq(sdkVer, dbconn)

    # await request because while its waiting to response it can release resources for other process
    res = requests.get(URL)

    if res.status_code == 200:
        return res.text

@app.get("/getImpression/{sdkVer}/{sessionId}/{platForm}/{usrName}/{countryCode}/")
async def getImpression(sdkVer: str, sessionId: str, platForm: str, usrName: str, countryCode: str):

    dbconn = firestore.client()

    await insertOrUpdateUserNumOfImpReq(usrName, dbconn)
    await insertOrUpdateSDKVerNumOfImpReq(sdkVer, dbconn)

    return 'response return HTTP', 200

@app.get("/getStats/{filterType}/")
async def getStats(filterType: str):

    dbconn = firestore.client()
    user = dbconn.collection('users').where("name", "==", filterType).get()
    sdkver = dbconn.collection('SDKVersions').where("sdkVer", "==", filterType).get()

    if user:
        myvar = user[0]
        myStr = "user"
    if sdkver:
        myvar = sdkver[0]
        myStr = "SDKVersion"

    numofimpreq = myvar.to_dict()
    impreqper = numofimpreq['numOfImpReq']
    adreqper = numofimpreq['numOfADReq']
    fillrate = impreqper / adreqper
    myjson = {"Impressions per " + myStr: [impreqper], "Ad requests per " + myStr: [adreqper], "fillrate":[fillrate]}

    return json.dumps(myjson)


async def insertOrUpdateUserNumOfImpReq(userName, db):

    # read from firebase users
    docs = db.collection('users').where("name", "==", userName).get()
    for doc in docs:
        key = doc.id
        db.collection('users').document(key).update({"numOfImpReq": firestore.Increment(1)})

    if not docs:
        # insert to firebase user
        print("docs are empty")
        db.collection('users').add({'name': userName, 'numOfImpReq': 1})

async def insertOrUpdateSDKVerNumOfImpReq(sdkVer, db):

    # read from firebase sdk version
    docs = db.collection('SDKVersions').where("sdkVer", "==", sdkVer).get()
    for doc in docs:
        key = doc.id
        db.collection('SDKVersions').document(key).update({"numOfImpReq": firestore.Increment(1)})

    if not docs:
        # insert to firebase sdk version
        print("docs are empty")
        db.collection('SDKVersions').add({'sdkVer': sdkVer, 'numOfImpReq': 1})


async def insertOrUpdateSDKVerNumOfADReq(sdkVer, db):

    # read from firebase sdk version
    docs = db.collection('SDKVersions').where("sdkVer", "==", sdkVer).get()
    for doc in docs:
        key = doc.id
        db.collection('SDKVersions').document(key).update({"numOfADReq": firestore.Increment(1)})

    if not docs:
        # insert to firebase sdk version
        print("docs are empty")
        db.collection('SDKVersions').add({'sdkVer': sdkVer, 'numOfADReq': 1})


async def insertOrUpdateUserNumOfADReq(userName , db):

    # read from firebase users
    docs = db.collection('users').where("name", "==", userName).get()
    for doc in docs:
        key = doc.id
        db.collection('users').document(key).update({"numOfADReq": firestore.Increment(1)})

    if not docs:
        # insert to firebase user
        print("docs are empty")
        db.collection('users').add({'name': userName, 'numOfADReq': 1})

if __name__ == "__main__":
    uvicorn.run("app:app", host=SERVICE_HOST, port=SERVICE_PORT, log_level=SERVICE_LOG_LEVEL)
