from typing import Optional,List,Dict,Union
from datetime import datetime, time
from pydantic import BaseModel, Field,conlist,constr

"""
These class define the structure, fields and contraints on each field.
Here 2 field are not added as per written in task 
* Upload time
* ID
These 2 field value will not be taken by Frontend. 
Real time Upload time is saved every time Audio file is created or Updated.
Since ID is primary key, Unique ID is given every time a new Audio File is created from Backend Side.
All the IDs for same Audio Type is Unique.

All the Audio Type class, Except for class Audio which act as base class contains sub-class Config which contains few required properties and data.
Properties-
* classname - contains name of the class so that we can check that the API request is for which type of the Audio File.
* collectionName - It store the collection name in which data is stored in MongoDB atlas cluster. If the name of the collection is changed in Atlas we change the name of collection here and APIs will work fine.

Data-
* schema_extra- It contain example of Schema of respective Audio Type classes which will help the Frontend Team while making API request.

One Extra class is here - AudioCreate
It contain fields for request body for Making Create Audio file request and Update Audio file request.
"""
class Audio(BaseModel):
    duration: int = Field(...,gt=0)

class Song(Audio):
    name: str = Field(...,max_length=100)
    
    class Config:
        classname='song'
        collectionName='Song'
        schema_extra = {
            "example": {
                "name": "dsa",
                "duration": 100,
               
            }
        }

class Podcast(Audio):
    host:str =Field(...,max_length=100)
    name: str = Field(...,max_length=100)
    participants : conlist(constr(max_length=100), min_items=None, max_items=10)=Field(exclusiveMaximum=10)
    
    class Config:
        classname='podcast'
        collectionName='Podcast'
        schema_extra = {
            "example": {
                "name": "abc",
                "duration": 100,
                "host":"sdasa",
                "participants":["scaac","avsdv"]
            }
        }


class Audiobook(Audio):
    title: str = Field(...,max_length=100)
    author:str=Field(...,max_length=100)
    narrator:str=Field(...,max_length=100)
    
    class Config:
        classname='audiobook'
        collectionName='Audiobook'

        schema_extra = {
            "example": {
                "title": "asd",
                "author": "dsfa",
                "narrator": "Cfaf",
                "duration": 100,
            }
        }

class AudioCreate(BaseModel):
    audioType:str
    metaData:dict
    
