from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# Documentation tags
tags_metadata = [
    {
        "name": "addrouter",
        "description": "**Add** a **router** to the **graph**.",
    },
    {
        "name": "connect",
        "description": "**Add** a **connection** from the router **from** to router **to** with the weight **weight**."
    },
    {
        "name": "removerouter",
        "description": "**Remove** a **router**.",
    },
    {
        "name": "removeconnection",
        "description": "**Remove** a **connection** between **two routers**.",
    },
    {
        "name": "route",
        "description": "**Find** the **shortest path** between **two routers** in a graph.",
    }
]
app = FastAPI(openapi_tags=tags_metadata)

# Class assigning status model as a string type
class Status(BaseModel):
    status: str

class Graph():
    def __init__(self):
        self.vertices = [] # It is a point where multiple lines meet. It’s also known as the node.
        self.edges = {} #  It is a line that connects two vertices.
        self.weights = {}

    # Str function to display vertices and edges created.

    def __str__(self):
        return f"Vertices:\n{self.vertices}\nEdges:\n{self.edges}"

    # Function to add a vertex to the graph

    def add_vertex(self, vertex):
        # If it does not exist place it into the graph
        if vertex not in self.vertices:
            self.vertices.append(vertex)
            # Success
            return Status(status="success")
        else:
            # Otherwise it alreay exits and therefore print error
            return Status(status="Error, node already exists")
        
    # Function to add edges to vertices

    def add_edge(self, v1, v2, weight):
        # If vertices are same or either is not in vertices then print error
        if (v1 == v2) or (v1 not in self.vertices) or (v2 not in self.vertices):
            return Status(status="Error, router does not exist")
        
        # if both vertices exit print updated as well as the correct distance between them
        if (v1, v2) in self.edges:
            self.edges[(v1, v2)] = weight
            self.edges[(v2, v1)] = weight
            return Status(status="updated")
        # Otherwise assign the weights and print a success
        else:
            self.edges[(v1, v2)] = weight
            self.edges[(v2, v1)] = weight
            return Status(status="success")
    
    # function to remove a router from the graph

    def remove_router(self, node):
        # if it is in the vertices remove it
        if node in self.vertices:
            self.vertices.remove(node)
            # Iterates through the edges
            for edge in self.edges:
                # If it exists
                if node in self.edges:
                    # Delete it from the dictionary
                    del self.edges[node][edge]
        # Print success
        return Status(status="success")
    
    # Function to remove connection between vertices

    def remove_connection(self, from_, to):
        # If they're both the same or if they're not placed in edges
        if from_ == to or (from_, to) not in self.edges:
            # Print success
            return Status(status="success")
        # otherwise remove the connections between vertices
        self.edges.pop((from_, to))
        self.edges.pop((to, from_))
        # Print success
        return Status(status="success")
    
    # shortest path function to compute the shortest path between nodes.
    # With aid of https://benalexkeen.com/implementing-djikstras-shortest-path-algorithm-with-python/
    def shortest_path(self, initial, end):
        if initial == end:
            return {
                "from": initial,
                "to": end,
                "weight": 0,
                "route": [initial]
            }

        # shortest paths is a dict of nodes
        # whose value is a tuple of (previous node, weight)
        shortest_paths = {initial: (None, 0)}
        current_node = initial
        visited = set()
        
        while current_node != end:
            visited.add(current_node)
            destinations = []
            for edge in self.edges:
                if current_node == edge[0]:
                    destinations.append(edge[1])            
            weight_to_current_node = shortest_paths[current_node][1]


            for next_node in destinations:
                weight = self.edges[(current_node, next_node)] + weight_to_current_node
                if next_node not in shortest_paths:
                    shortest_paths[next_node] = (current_node, weight)
                else:
                    current_shortest_weight = shortest_paths[next_node][1]
                    if current_shortest_weight > weight:
                        shortest_paths[next_node] = (current_node, weight)
            
            next_destinations = {node: shortest_paths[node] for node in shortest_paths if node not in visited}
            if not next_destinations:
                return {
                        "from": initial,
                        "to": end,
                        "weight": -1,
                        "route": []
                    }
            # next node is the destination with the lowest weight
            current_node = min(next_destinations, key=lambda k: next_destinations[k][1])
        
        # Work back through destinations in shortest path
        path_nodes = []
        while current_node is not None:
            path_nodes.append(current_node)
            next_node = shortest_paths[current_node][0]
            current_node = next_node
        # Reverse path
        path_nodes = path_nodes[::-1]

        path = []
        total_weight = 0
        for i in range(len(path_nodes)-1):
            weight = self.edges[(path_nodes[i], path_nodes[i+1])]
            total_weight += weight
            current = {
                "from": path_nodes[i],
                "to": path_nodes[i+1],
                "weight": weight
            }
            path.append(current)

        return {
            "from": initial,
            "to": end,
            "weight": total_weight,
            "route": path
        }

# All classes and their BaseModeks and values assigned

class AddRouter(BaseModel):
    name: str

class connect(BaseModel):
    from_: str
    to: str
    weight: int

class RemoveRouter(BaseModel):
    name: str

class RemoveConnection(BaseModel):
    from_ : str
    to : str

class ShortestPath(BaseModel):
    from_ : str
    to : str

g = Graph()

# Functions where final operation takes place and where post responses occur according to each function

@app.post(
    "/addrouter",
    response_model=Status,
    tags=["addrouter"]

)
async def addrouter(info: AddRouter):
    resp = g.add_vertex(info.name)
    print(g)
    return resp

@app.post(
    "/connect",
    response_model=Status,
    tags=["connect"]
)
async def connect(info: connect):
    resp = g.add_edge(info.from_, info.to, info.weight)
    print(g)
    return resp

@app.post(
    "/removerouter",
    response_model=Status,
    tags=["removerouter"]
)
async def removerouter(info: RemoveRouter):
    resp = g.remove_router(info.name)
    print(g)
    return resp

@app.post(
    "/removeconnection",
    response_model=Status,
    tags=["removeconnection"]
)
async def removeconnection(info: RemoveConnection):
    resp = g.remove_connection(info.from_, info.to)
    print(g)
    return resp

@app.post(
    "/route",
    response_model=Status,
    tags=["route"]
)

async def route(info: ShortestPath):
    resp = g.shortest_path(info.from_, info.to)
    return resp

'''
references used to aid project
https://benalexkeen.com/implementing-djikstras-shortest-path-algorithm-with-python/
https://www.analyticsvidhya.com/blog/2018/09/introduction-graph-theory-applications-python/
https://stackabuse.com/dijkstras-algorithm-in-python/
https://www.educative.io/edpresso/how-to-implement-a-graph-in-python
https://www.bogotobogo.com/python/python_graph_data_structures.php
https://www.analyticsvidhya.com/blog/2018/09/introduction-graph-theory-applications-python/
https://stackoverflow.com/questions/34700207/adding-variables-to-dictionary
https://www.programcreek.com/python/?CodeExample=remove+edge
'''

if __name__ == "__main__":
    g = Graph()
    g.add_vertex("A")
    g.add_vertex("B")
    g.add_vertex("C")
    g.add_vertex("D")
    g.add_edge("A", "B", 6)
    g.add_edge("A", "C", 5)
    g.add_edge("B", "D", 1)
    g.add_edge("C", "D", 1)
    print(g.shortest_path("A", "A"))
    # uvicorn.run( app, port=8000 )
