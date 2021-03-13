from fastapi import FastAPI
from typing import Optional
from models import Song,Podcast,Audiobook,AudioCreate
from pymongo import MongoClient
from datetime import datetime
from fastapi.responses import JSONResponse
audio_types=[Song,Podcast,Audiobook]
app = FastAPI()
available_uid={i.Config.classname:[] for i in audio_types}
client=MongoClient('mongodb+srv://username:usernamepassword@cluster0.skudm.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db=client.get_database('Audio')

@app.post('/create',response_model=AudioCreate)
def create(data:AudioCreate):
    for model in audio_types:
        if model.Config.classname==data.audioType.lower():
            try:
                obj=model(**data.metaData)
            except:
                return JSONResponse(content={'error':f'Incorrect metadata schema for audioType {data.audioType}','required schema':model.Config.schema_extra},status_code=404)

            data=obj.dict()
            collection=db.get_collection(model.Config.collectionName)
            data['datetime']=datetime.now()
            
            if available_uid[model.Config.classname]==[]:
                data['uid']=collection.count_documents({})
            else:
                data['uid']=available_uid[model.Config.classname][0]
                del available_uid[model.Config.classname][0]
            collection.insert_one(data)
            return JSONResponse(content={'message':f'success'},status_code=200)
    return JSONResponse(content={'error':f'AudioType "{data.audioType}" does not exist'},status_code=404)
    

@app.get('/delete/{audio_type}/{audio_id}')
def delete(audio_type:str,audio_id:str):
    try:
        audio_id=int(audio_id)
    except:
        return JSONResponse(content={'error':'audio_id is not integer'},status_code=404)
    for model in audio_types:
        if model.Config.classname==audio_type.lower():
            collection=db.get_collection(model.Config.collectionName)
            if collection.find_one(filter={'uid':audio_id})==None:
                return JSONResponse(content={'error':f'Audio File {audio_type}/{audio_id} does not exist'},status_code=404)
            collection.delete_one(filter={'uid':audio_id})
            available_uid[model.Config.classname].append(audio_id)
            return JSONResponse(content={'message':f'success'},status_code=200)

    return JSONResponse(content={'error':f'AudioType {audio_type} does not exist'},status_code=404)


@app.post('/update/{audio_type}/{audio_id}')
def update(audio_type:str,audio_id:str,data:AudioCreate):
    try:
        audio_id=int(audio_id)
    except:
        return JSONResponse(content={'error':'audio_id is not integer'},status_code=404)
    for model in audio_types:
        if model.Config.classname==audio_type.lower():
            collection=db.get_collection(model.Config.collectionName)
            if collection.find_one(filter={'uid':audio_id})==None:
                return JSONResponse(content={'error':f'Audio File {audio_type}/{audio_id} does not exist'},status_code=404)
            
            try:
                obj=model(**data.metaData)
            except:
                return JSONResponse(content={'error':f'Incorrect metadata schema for audioType {data.audioType}','required schema':model.Config.schema_extra},status_code=404)

            data=obj.dict()

            collection=db.get_collection(model.Config.collectionName)
            data['datetime']=datetime.now()
            data['uid']=audio_id
            
            collection.update_one(filter={'uid':audio_id},update={'$set':data})
            
            return JSONResponse(content={'message':f'success'},status_code=200)

    return JSONResponse(content={'error':f'AudioType {audio_type} does not exist'},status_code=404)



@app.get('/get')
def get(path:str):
    query=path.split('/')
    audio_type=query[0]
    try:
        audio_id=query[1]
        if audio_id=='':
            audio_id=None
    except:
        audio_id=None
    for model in audio_types:
        if model.Config.classname==audio_type.lower():
            collection=db.get_collection(model.Config.collectionName)
            if audio_id==None:
                docs=[]
                for doc in list(collection.find({})):
                    del doc['_id']
                    doc['datetime']=str(doc['datetime'])
                    docs.append(doc)
                

                return JSONResponse(content={'document':docs},status_code=200)
            else:
                try:
                    audio_id=int(audio_id)
                except:
                    return JSONResponse(content={'error':'audio_id is not integer'},status_code=404)
            doc=collection.find_one(filter={'uid':audio_id})
            del doc['_id']
            doc['datetime']=str(doc['datetime'])
            if doc==None:
                return JSONResponse(content={'error':f'Audio File {audio_type}/{audio_id} does not exist'},status_code=404)
            
            return JSONResponse(content={'document':doc},status_code=200)

    return JSONResponse(content={'error':f'AudioType {audio_type} does not exist'},status_code=404)
