"""
controller/loop.py

Loop Controller: Orchestrates the research workflow.
"""

class LoopController:
    def __init__(self, max_iterations=3):
        self.max_iterations = max_iterations
    
    def run(self, entity):
        raise NotImplementedError("Loop Controller coming in Day 7")
