# this file will handle everything there is to handle in a project

# project class
class Project:
    
    # initialize a project's information
    def __init__(self, name, cost, benefit, category, description=""):
        self.name = name
        self.cost = cost
        self.set_benefit(benefit)  # this is used to validate the benefit score
        self.category = category
        self.description = description
        self.benefit_cost_ratio = cost > 0 and benefit / cost or 0
        self.is_emergency_priority = False
        self.emergency_priority_level = 5  # default lowest priority
    
    def set_benefit(self, benefit):

        # benefit score conditions
        if benefit > 10:
            raise ValueError(f"Benefit score cannot exceed 10. Current value: {benefit}")
        if benefit < 0:
            raise ValueError(f"Benefit score cannot be negative. Current value: {benefit}")
        
        self.benefit = benefit
        self.benefit_cost_ratio = self.cost > 0 and benefit / self.cost or 0
    
    # handling emergency situations
    def set_emergency_priority(self, is_emergency, emergency_type=None):
        self.is_emergency_priority = is_emergency
        if is_emergency:
            base_priorities = {
                "infrastructure": 1,
                "health": 2,
                "social services": 3,
                "environment": 4,
                "education": 5, 
                "economic development": 5
            }
            # set priorities if emergency mode was enabled
            category_lower = self.category.lower()
            if emergency_type:
                emergency_type_lower = emergency_type.lower()

                # if the emergency is health related, always put health first
                if emergency_type_lower == "health crisis":
                    if category_lower == "health":
                        self.emergency_priority_level = 1
                    elif category_lower == "social services":
                        self.emergency_priority_level = 2
                    elif category_lower == "infrastructure":
                        self.emergency_priority_level = 3
                    else:
                        self.emergency_priority_level = base_priorities.get(category_lower, 5) # priority level of the rest of the sectors
                # group all the non-health related emergencies
                elif emergency_type_lower in ["typhoon", "earthquake", "flood", "fire"]: 
                    if category_lower == "infrastructure":
                        self.emergency_priority_level = 1  # infrastructure have the highest priority
                    elif category_lower == "social services":
                        self.emergency_priority_level = 2
                    elif category_lower == "health":
                        self.emergency_priority_level = 3
                    else:
                        self.emergency_priority_level = base_priorities.get(category_lower, 5) # priority level of the rest of the sectors
                else:
                    self.emergency_priority_level = base_priorities.get(category_lower, 5) # if emergency type is not specifically handled
            else:
                self.emergency_priority_level = base_priorities.get(category_lower, 5) # just in case the emergency type was not provided due to other unforseen bugs
        else: 
            self.emergency_priority_level = 5 # if not emergency

    # end of set_emergency_priority
    def __str__(self):
        emergency_status = f" [EMERGENCY PRIORITY: {self.emergency_priority_level}]" if self.is_emergency_priority else ""
        return f"Project: {self.name} | Cost: ₱{self.cost:.2f} | Benefit: {self.benefit:.2f} | Ratio: {self.benefit_cost_ratio:.3f} | Category: {self.category}{emergency_status}"
