#!/usr/bin/env python3

import unittest
from main import Graph, Status

g = Graph()

class TestGraph( unittest.TestCase ):
    def test_add_vertex( self ):
        vertexes = "ABCDZ"
        for vertex in vertexes:
            response = g.add_vertex( vertex )
            self.assertEqual( response, Status(status="success") )
        response = g.add_vertex( "A" )
        self.assertEqual( response, Status(status="Error, node already exists") )

    def test_add_edge( self ):
        response = g.add_edge("A", "B", 5)
        self.assertEqual(response, Status(status="success"))
        # response = g.add_edge("A", "B", 2)
        # self.assertEqual(response, Status(status="updated"))
        # response = g.add_edge("Z", "Y", 1)
        # self.assertEqual(response, Status(status="Error, router does not exist"))
        # response = g.add_edge("A", "A", 99) # this should always be zero
        # self.assertEqual(response, Status(status="Error, router does not exist"))

    def test_remove_router( self ):
        response = g.remove_router("B")
        self.assertEqual(response, Status(status="success"))

    # def test_remove_connection( self ):
    #     response = g.remove_connection("A", "B")
    #     self.assertEqual(response, Status(status="success"))

    def test_route( self ):
        g.add_edge("A", "C", 1)
        g.add_edge("B", "D", 8)
        g.add_edge("C", "D", 1)
        expected_route = [
            FromToWeight(
                from_='A',
                to='C',
                weight=1,
            ),
            FromToWeight(
                from_='C',
                to='D',
                weight=1,
            	),
        ] 
        weight, route = g.route( "A", "D" )
        self.assertEqual(weight, 2)
        self.assertEqual(route, expected_route)