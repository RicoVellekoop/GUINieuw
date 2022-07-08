import threading
import asyncio
import websockets
import json
import serial

page = None
soc = None

# serUno = serial.Serial()
# serUno.reset_input_buffer()
serMega = serial.Serial('COM3', 9600, timeout=1)
serMega.reset_input_buffer()

myDict = {}
myDict["temperature"]= []
myDict["humidity"]= []
myDict["sound"]= []
myDict["idk"]= []
myDict["idk2"]= []
myDictAvg = {}
myDictAvg["temperature"]= []
myDictAvg["humidity"]= []
myDictAvg["sound"]= []
myDictAvg["idk"]= []
myDictAvg["idk2"]= []
 
# create handler for each connection
async def handler(websocket):
    global page, soc
    soc = websocket
    page = await websocket.recv()
    print(page)
    sendList(myDictAvg[page])
    try:
        await websocket.wait_closed()
    finally:
        soc = None

async def sendList(list):
    if soc != None:
        await soc.send(json.dumps(list))

async def mainLoop():
    while True:
        for key, value in myDict.items():
            if len(value) >= 10:
                for j in value:
                    Average = j + Average
                Average = Average / len(value)
                value.clear()
                myDictAvg[key].append(Average)
                if key == page:
                    sendList(myDictAvg[key])
            if len(myDictAvg[key]) >= 10:
                myDictAvg[key].pop(0)
                print(myDictAvg[key])
        if serUno.in_waiting() > 0:
            data = serUno.readline()
            data = data.decode("utf-8")
            data = data.rstrip()
            data = data.split(":")
            for i in range(5):
                if data[0] == str(i):
                    myDict[str(i)].append(data[1])
        if serMega.in_waiting() > 0:
            data = serMega.readline()
            data = data.decode("utf-8")
            data = data.rstrip()
            data = data.split(":")
            for i in range(5):
                if data[0] == str(i):
                    myDict[str(i)].append(data[1])
        
def client():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(mainLoop())
    loop.run_forever() 


def startServer():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    ws_server = websockets.serve(handler, "localhost", 8000)
    loop.run_until_complete(ws_server)
    loop.run_forever() 


server = threading.Thread(target=startServer, daemon=True)
server.start()
mainlp = threading.Thread(target=client)
mainlp.start()
mainlp.join()





