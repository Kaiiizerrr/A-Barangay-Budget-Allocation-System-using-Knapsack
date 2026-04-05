# this file implements the branch and bound algorithm to solve the knapsack problem

# import the necessary libraries
import heapq
from typing import List

# import the project class from project.py (must be in the same directory as this file)
from project import Project

# node solution, this will represent a state in the search tree
class Node:
    # initialize a node    
    def __init__(self, level, profit, weight, selected):
        self.level = level
        self.profit = profit
        self.weight = weight
        self.bound = 0
        self.selected = selected.copy()
    
    def __lt__(self, other):
        # for priority queue, higher bound means higher priority
        return self.bound > other.bound

# solution class, this will hold the final results of the optimization
class Solution:
    # initialize the solution, as well as it's other properties to be considered
    def __init__(self):
        self.selected_projects = []
        self.total_cost = 0
        self.total_benefit = 0
        self.efficiency = 0

# algorithmic approach class
class BranchAndBound:
    # static method to solve the knapsack problem using branch and bound
    @staticmethod
    # Solve the knapsack problem with emergency mode support
    def solve_knapsack(projects: List[Project], budget: float, emergency_mode: bool = False) -> Solution:
        # sort the projects based on benefit-cost ratio and emergency priority
        sorted_projects = BranchAndBound._sort_projects(projects, emergency_mode)
        
        # if there are no projects, return an empty solution
        n = len(sorted_projects)
        if n == 0:
            return Solution()
        
        # priority queue for the nodes
        pq = []
        
        # initialize the root node
        # level -1 means no project has been considered yet
        # profit and weight are both 0, and selected is a list of False
        root = Node(-1, 0, 0, [False] * n)
        # calculate the bound and push it in the priorite queue
        root.bound = BranchAndBound._calculate_bound(root, sorted_projects, budget, emergency_mode)
        heapq.heappush(pq, root)
        
        # initialize the max profit and best selection
        max_profit = 0
        best_selection = [False] * n
        
        # branch and bound process
        while pq:
            current = heapq.heappop(pq)
            
            if current.bound <= max_profit:
                continue  # prune this branch
            
            next_level = current.level + 1 # move to the next project/node
            if next_level >= n: # no more projects to consider/check
                continue
            
            # includet the next project if it fits in the budget
            if current.weight + sorted_projects[next_level].cost <= budget:
                include_selected = current.selected.copy()
                include_selected[next_level] = True
                
                project_benefit = sorted_projects[next_level].benefit
                
                # apply emergency and priority calculations
                if emergency_mode and sorted_projects[next_level].is_emergency_priority:
                    emergency_bonus = (6 - sorted_projects[next_level].emergency_priority_level) * 0.5
                    project_benefit += emergency_bonus
                
                # create a new node for including the next project
                include_node = Node(
                    next_level,
                    current.profit + project_benefit,
                    current.weight + sorted_projects[next_level].cost,
                    include_selected
                )
                
                # check if this node has a better profit
                if include_node.profit > max_profit:
                    max_profit = include_node.profit
                    best_selection = include_node.selected.copy()
                
                # calculate the bound for the include node and push it to the priority queue
                include_node.bound = BranchAndBound._calculate_bound(include_node, sorted_projects, budget, emergency_mode)
                if include_node.bound > max_profit:
                    heapq.heappush(pq, include_node)
            
            # exclude the next project
            exclude_selected = current.selected.copy()
            exclude_node = Node(next_level, current.profit, current.weight, exclude_selected)
            exclude_node.bound = BranchAndBound._calculate_bound(exclude_node, sorted_projects, budget, emergency_mode)
            
            # check if this node has a better profit and push it to the priority queue
            if exclude_node.bound > max_profit:
                heapq.heappush(pq, exclude_node)
        
        # build the solution
        solution = Solution()
        for i in range(n):
            if best_selection[i]:
                solution.selected_projects.append(sorted_projects[i])
                solution.total_cost += sorted_projects[i].cost
                solution.total_benefit += sorted_projects[i].benefit
        
        solution.efficiency = solution.total_cost > 0 and solution.total_benefit / solution.total_cost or 0
        return solution
    
    # static method to sort projects based on benefit-cost ratio and emergency priority
    @staticmethod
    def _sort_projects(projects: List[Project], emergency_mode: bool) -> List[Project]:
        # compare the projects for sorting
        def compare_projects(project):
            if emergency_mode:
                # sort by emergency priority first, then by benefit-cost ratio
                if project.is_emergency_priority:
                    return (0, project.emergency_priority_level, -project.benefit_cost_ratio)
                else:
                    return (1, 0, -project.benefit_cost_ratio) # emergency projects first
            else:
                # sort just by benefit-cost ratio
                return (0, 0, -project.benefit_cost_ratio)
        
        return sorted(projects, key=compare_projects)
    
    # static method to calculate the bound for a node/project
    @staticmethod
    def _calculate_bound(node: Node, projects: List[Project], budget: float, emergency_mode: bool) -> float:
        # if the current node is greater than the budget, ignore it
        if node.weight >= budget:
            return 0
        
        bound = node.profit # initialize the bound with the current profit
        level = node.level + 1 # move to the next project
        remaining_weight = budget - node.weight # remaining budget
        
        # add projects to the bound until the budget is exhausted
        while level < len(projects) and projects[level].cost <= remaining_weight:
            project_benefit = projects[level].benefit
            
            # apply emergency bonus for calculation if enabled
            if emergency_mode and projects[level].is_emergency_priority:
                emergency_bonus = (6 - projects[level].emergency_priority_level) * 0.5
                project_benefit += emergency_bonus
            
            
            bound += project_benefit # add the benefit of the project
            remaining_weight -= projects[level].cost # subtract the cost from the remaining budget
            level += 1 # move to the next project
        
        # add a fraction of the next project if it fits partially
        if level < len(projects):
            project_benefit = projects[level].benefit
            # if the next project is too expensive, we can't include it fully
            if emergency_mode and projects[level].is_emergency_priority:
                emergency_bonus = (6 - projects[level].emergency_priority_level) * 0.5
                project_benefit += emergency_bonus
            # if the remaining weight is positive, we can include a fraction of the next project
            bound += (remaining_weight / projects[level].cost) * project_benefit
        
        return bound
