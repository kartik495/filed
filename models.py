from typing import Optional,List,Dict,Union
from datetime import datetime, time
from pydantic import BaseModel, Field,conlist,constr


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
    
