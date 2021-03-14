from fastapi import FastAPI
from typing import Optional
from models import Song,Podcast,Audiobook,AudioCreate
from pymongo import MongoClient
from datetime import datetime
from fastapi.responses import JSONResponse
#List containing class of audio types
audio_types=[Song,Podcast,Audiobook]
app = FastAPI()

#Creating empty List of Available ID for each audio type class
available_uid={model.Config.classname:[] for model in audio_types}

#getting access to MongoDB Atlas cluster0
client=MongoClient('mongodb+srv://username:usernamepassword@cluster0.skudm.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')

#Getting Audio database from MongoDB Atlas 
db=client.get_database('Audio')


#Create API- Api for creating Audio file
@app.post('/create',response_model=AudioCreate)
def create(data:AudioCreate):
    ''' 
    Checks for which type of Audio file, API request has been created. Audiotype lower-case value is used for comparison to make it case-insensitive.
    If None the the Audio type Matches return response with status code 404 and message of incorrect audiotype.
    '''
    for model in audio_types:
        if model.Config.classname==data.audioType.lower():
            
            '''
            check if the metaData contains all the data required to create Audio file as per constraints for each field
            If it does not return response with status code 404 and required schema example of Audio type stored in variable audioType.
            '''
            try:
                obj=model(**data.metaData)
            except:
                return JSONResponse(content={'error':f'Incorrect metadata schema for audioType {data.audioType}','required schema':model.Config.schema_extra},status_code=404)
            
            # class object is converted into dictionary and real-time upload time value is added to dictionary.
            data=obj.dict()
            collection=db.get_collection(model.Config.collectionName)
            data['datetime']=datetime.now()
            
            '''
            checks if unique ID is available for respective audio-type.
            If not assign new unique ID. 
            '''            
            if available_uid[model.Config.classname]==[]:
                data['uid']=collection.count_documents({})
            else:
                data['uid']=available_uid[model.Config.classname][0]
                del available_uid[model.Config.classname][0]
            
            # insert data into collection as document and return response with status code 404 and success message.
            collection.insert_one(data)
            return JSONResponse(content={'message':'success'},status_code=200)
    
    return JSONResponse(content={'error':f'AudioType {data.audioType} does not exist'},status_code=404)
    
# Delete API- delete Audio file of id 'audio_id' and type 'audio_type'
@app.get('/delete/{audio_type}/{audio_id}')
def delete(audio_type:str,audio_id:str):
    
    '''
    check if audio_id is integer or not.
    If not return Response with status code 404 and message 'audio_id is not integer'
    '''
    try:
        audio_id=int(audio_id)
    except:
        return JSONResponse(content={'error':'audio_id is not integer'},status_code=404)


    ''' 
    Checks for which type of Audio file, API request has been created. Audiotype lower-case value is used for comparison to make it case-insensitive.
    If None the the Audio type Matches return response with status code 404 and message of incorrect audiotype.
    '''
    for model in audio_types:
        if model.Config.classname==audio_type.lower():
            
            # Get collection which contains documents for Audio Type 'audio_type'
            collection=db.get_collection(model.Config.collectionName)
            
            '''
            check if document with ID 'audio_id' exist in collection
            if not return response with status code 404 and message 
            '''
            if collection.find_one(filter={'uid':audio_id})==None:
                return JSONResponse(content={'error':f'Audio File {audio_type}/{audio_id} does not exist'},status_code=404)
            
            # delete the document 
            collection.delete_one(filter={'uid':audio_id})
            
            # add audio_id in respective list of available_uid so that it could be used when new document is created in respective audio_type.
            available_uid[model.Config.classname].append(audio_id)
            return JSONResponse(content={'message':'success'},status_code=200)

    return JSONResponse(content={'error':f'AudioType {audio_type} does not exist'},status_code=404)


# Update Api- update Audio file of id 'audio_id' and type 'audio_type'
@app.post('/update/{audio_type}/{audio_id}')
def update(audio_type:str,audio_id:str,data:AudioCreate):

        
    '''
    check if audio_id is integer or not.
    If not return Response with status code 404 and message 'audio_id is not integer'
    '''
    try:
        audio_id=int(audio_id)
    except:
        return JSONResponse(content={'error':'audio_id is not integer'},status_code=404)
    
    ''' 
    Checks for which type of Audio file, API request has been created. Audiotype lower-case value is used for comparison to make it case-insensitive.
    If None the the Audio type Matches return response with status code 404 and message of incorrect audiotype.
    '''
    for model in audio_types:
        if model.Config.classname==audio_type.lower():
            
            # Get collection which contains documents for Audio Type 'audio_type'
            collection=db.get_collection(model.Config.collectionName)
            
            '''
            check if document with ID 'audio_id' exist in collection
            if not return response with status code 404 and message 
            '''
            if collection.find_one(filter={'uid':audio_id})==None:
                return JSONResponse(content={'error':f'Audio File {audio_type}/{audio_id} does not exist'},status_code=404)
            
            '''
            check if the metaData contains all the data required to create Audio file as per constraints for each field
            If it does not return response with status code 404 and required schema example of Audio type stored in variable audioType.
            '''
            try:
                obj=model(**data.metaData)
            except:
                return JSONResponse(content={'error':f'Incorrect metadata schema for audioType {data.audioType}','required schema':model.Config.schema_extra},status_code=404)

            # convert object to dictionary
            data=obj.dict()

            # Getting real update date-time and storing in data
            data['datetime']=datetime.now()

            # Using audio_id to keep audio_id same while updating the document.
            data['uid']=audio_id
            
            # updating the document and returning success response
            collection.update_one(filter={'uid':audio_id},update={'$set':data})
            return JSONResponse(content={'message':f'success'},status_code=200)

    return JSONResponse(content={'error':f'AudioType {audio_type} does not exist'},status_code=404)


# Update Api- update Audio file of id 'audio_id' and type 'audio_type'
@app.get('/get')
def get(path:str):
    
    '''
    get audio_type and audio_id from path.
    if audio_id is not given then audio_id= None
    '''
    query=path.split('/')
    audio_type=query[0]
    try:
        audio_id=query[1]
        if audio_id=='':
            audio_id=None
    except:
        audio_id=None

    ''' 
    Checks for which type of Audio file, API request has been created. Audiotype lower-case value is used for comparison to make it case-insensitive.
    If none of the the Audio type matches then return response with status code 404 and message of incorrect audiotype.
    '''
    for model in audio_types:
        if model.Config.classname==audio_type.lower():
            
            # Get collection which contains documents for Audio Type 'audio_type'
            collection=db.get_collection(model.Config.collectionName)
            
            #If audio_id is None then return all the documents in collection with status code 200
            if audio_id==None:
                docs=[]
                for doc in list(collection.find({})):
                    del doc['_id']
                    doc['datetime']=str(doc['datetime'])
                    docs.append(doc)
                

                return JSONResponse(content={'document':docs},status_code=200)
            
            # return the requested doucument/ audio_file
            else:

                '''
                check if audio_id is integer or not.
                If not return Response with status code 404 and message 'audio_id is not integer'
                '''
                try:
                    audio_id=int(audio_id)
                except:
                    return JSONResponse(content={'error':'audio_id is not integer'},status_code=404)
            
            '''
            Get the requested document
            if it exist return response with status code 200 and document
            if it doesn't exist return response with status code 404 and resposne with error message 
            '''
            doc=collection.find_one(filter={'uid':audio_id})
            if doc==None:
                return JSONResponse(content={'error':f'Audio File {audio_type}/{audio_id} does not exist'},status_code=404)
            del doc['_id']
            doc['datetime']=str(doc['datetime'])
            return JSONResponse(content={'document':doc},status_code=200)
    
    return JSONResponse(content={'error':f'AudioType {audio_type} does not exist'},status_code=404)
