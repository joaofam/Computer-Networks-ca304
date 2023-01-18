from fastapi import FastAPI
from pydantic import BaseModel
import matplotlib.pyplot as plt

app = FastAPI()

class AddRouter(BaseModel):
    name: str

@app.post("/addrouter")
async def addrouter(info: AddRouter):
    d = {}

    f = "hello"

    d["Hello"] = f
    print("hello world")


'''
References
https://www.section.io/engineering-education/dijkstra-python/

'''