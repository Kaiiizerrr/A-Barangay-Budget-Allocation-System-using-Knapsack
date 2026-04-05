# this file will handle the gui of the application

# import the necessary libraries
import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as patches
from collections import defaultdict
import numpy as np

# import the classes from other files (the files should be in the same directory)
from project import Project
from branch_and_bound import BranchAndBound

# Set the appearance mode and color theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# gui class of the application
class BudgetAllocationGUI:

    # initialize the gui
    def __init__(self, root):
        self.root = root
        self.projects = []
        self.solution = None
        self.emergency_mode = tk.BooleanVar(master=self.root)
        self.emergency_type = tk.StringVar(master=self.root, value="Typhoon")
        
        self.setup_gui()

    # setup the gui 
    def setup_gui(self):
        self.root.title("Group 4 Final Project - Pondong Planado")
        self.root.geometry("1400x900")
        self.root.configure(fg_color='#4682B4')
        
        # create the main frame
        main_frame = ctk.CTkFrame(self.root, fg_color='#9DCCDE', corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # title label
        title_label = ctk.CTkLabel(main_frame, text="Pondong Planado", 
                              font=('Roboto', 24, 'bold'), 
                              fg_color="transparent", text_color='black')
        title_label.pack(pady=10)
        
        # subtitle label
        subtitle_label = ctk.CTkLabel(main_frame, text="A Smart Budgeting System for Barangay Projects", 
                                 font=('Roboto', 14, 'italic'), 
                                 fg_color="transparent", text_color='black')
        subtitle_label.pack(pady=(0, 20))

        self.root.update_idletasks()
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # create tabs
        self.create_main_tab() # main tab where you define a project and allocate the budget
        self.create_chart_tab() # chart tab where you show the chart that visualizes the allocation

    # main tab  
    def create_main_tab(self):
        main_tab = ctk.CTkFrame(self.notebook, fg_color='#E6F3FF', corner_radius=10)
        self.notebook.add(main_tab, text="Budget Allocation")
        
        # top frame
        top_frame = ctk.CTkFrame(main_tab, fg_color='#D1E7F0', corner_radius=10)
        top_frame.pack(fill="x", padx=10, pady=5)
        
        # title for top frame
        top_title = ctk.CTkLabel(top_frame, text="Budget Configuration", 
                                font=('Arial', 12, 'bold'), text_color='black')
        top_title.pack(pady=(10, 5))
        
        # budget frame 
        budget_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        budget_frame.pack(side="left", padx=10, pady=5)
        
        ctk.CTkLabel(budget_frame, text="Total Budget (₱):", text_color='black').pack(side="left")
        self.budget_entry = ctk.CTkEntry(budget_frame, width=150, corner_radius=8)
        self.budget_entry.pack(side="left", padx=5)
        
        # emergency mode frame
        emergency_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        emergency_frame.pack(side="left", padx=20, pady=5)
        
        # check button
        emergency_check = ctk.CTkCheckBox(emergency_frame, text="Emergency Mode", 
                                       variable=self.emergency_mode,
                                       command=self.toggle_emergency_mode,
                                       font=('Arial', 10, 'bold'),
                                       text_color='black')
        emergency_check.pack(side="left")
        
        # combo box that contains the emergency types (keeping ttk since CTk combobox is different)
        self.emergency_combo = ttk.Combobox(emergency_frame, textvariable=self.emergency_type,
                                          values=["Typhoon", "Earthquake", "Flood", "Fire", "Health Crisis"],
                                          state="disabled", width=12)
        self.emergency_combo.pack(side="left", padx=5)
        
        # button frame
        button_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        button_frame.pack(side="right", padx=10, pady=5)
        
        ctk.CTkButton(button_frame, text="Optimize Allocation", command=self.optimize_budget,
                     fg_color='#2C4E2C', text_color='white', font=('Arial', 10, 'bold'),
                     hover_color='#3e6b3e', corner_radius=8, width=140).pack(side="left", padx=2)
        ctk.CTkButton(button_frame, text="Add Project", command=self.show_add_project_dialog,
                     fg_color='#4169E1', text_color='white', hover_color='#5a7ce6',
                     corner_radius=8, width=100).pack(side="left", padx=2)
        ctk.CTkButton(button_frame, text="Remove Selected", command=self.remove_selected_project,
                     fg_color='#DC143C', text_color='white', hover_color='#e6455a',
                     corner_radius=8, width=120).pack(side="left", padx=2)
        ctk.CTkButton(button_frame, text="Clear All", command=self.clear_all_projects,
                     fg_color='#FF6347', text_color='white', hover_color='#ff7a5c',
                     corner_radius=8, width=80).pack(side="left", padx=2)
        
        # middle frame
        middle_frame = ctk.CTkFrame(main_tab, fg_color="transparent")
        middle_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # projects table
        projects_frame = ctk.CTkFrame(middle_frame, fg_color='#D1E7F0', corner_radius=10)
        projects_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # projects frame title
        projects_title = ctk.CTkLabel(projects_frame, text="Available Projects", 
                                     font=('Arial', 12, 'bold'), text_color='black')
        projects_title.pack(pady=(10, 5))
        
        # projects tree view (keeping ttk since CTk doesn't have treeview)
        tree_frame = ctk.CTkFrame(projects_frame, fg_color='white', corner_radius=8)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.projects_tree = ttk.Treeview(tree_frame, 
                                        columns=('Name', 'Cost', 'Benefit', 'Ratio', 'Category', 'Priority'),
                                        show='headings', height=10)
        
        # configure table attributes
        self.projects_tree.heading('Name', text='Name')
        self.projects_tree.heading('Cost', text='Cost (₱)')
        self.projects_tree.heading('Benefit', text='Benefit')
        self.projects_tree.heading('Ratio', text='Ratio')
        self.projects_tree.heading('Category', text='Category')
        self.projects_tree.heading('Priority', text='Priority')
        
        self.projects_tree.column('Name', width=150, anchor='center')
        self.projects_tree.column('Cost', width=100, anchor='center')
        self.projects_tree.column('Benefit', width=80, anchor='center')
        self.projects_tree.column('Ratio', width=80, anchor='center')
        self.projects_tree.column('Category', width=120, anchor='center')
        self.projects_tree.column('Priority', width=100, anchor='center')
    
        projects_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.projects_tree.yview)
        self.projects_tree.configure(yscrollcommand=projects_scrollbar.set)
        
        self.projects_tree.pack(side="left", fill="both", expand=True)
        projects_scrollbar.pack(side="right", fill="y")
        
        # solution table
        solution_frame = ctk.CTkFrame(middle_frame, fg_color='#D1E7F0', corner_radius=10)
        solution_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # solution frame title
        solution_title = ctk.CTkLabel(solution_frame, text="Optimal Selection", 
                                     font=('Arial', 12, 'bold'), text_color='black')
        solution_title.pack(pady=(10, 5))
        
        # solution tree frame
        solution_tree_frame = ctk.CTkFrame(solution_frame, fg_color='white', corner_radius=8)
        solution_tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.solution_tree = ttk.Treeview(solution_tree_frame,
                                        columns=('Name', 'Cost', 'Benefit', 'Category', 'Priority'),
                                        show='headings', height=10)
        
        self.solution_tree.heading('Name', text='Selected Project')
        self.solution_tree.heading('Cost', text='Cost (₱)')
        self.solution_tree.heading('Benefit', text='Benefit')
        self.solution_tree.heading('Category', text='Category')
        self.solution_tree.heading('Priority', text='Priority')
        
        self.solution_tree.column('Name', width=150, anchor='center')
        self.solution_tree.column('Cost', width=100, anchor='center')
        self.solution_tree.column('Benefit', width=80, anchor='center')
        self.solution_tree.column('Category', width=120, anchor='center')
        self.solution_tree.column('Priority', width=100, anchor='center')

        solution_scrollbar = ttk.Scrollbar(solution_tree_frame, orient="vertical", command=self.solution_tree.yview)
        self.solution_tree.configure(yscrollcommand=solution_scrollbar.set)
        
        self.solution_tree.pack(side="left", fill="both", expand=True)
        solution_scrollbar.pack(side="right", fill="y")
        
        # bottom frame
        bottom_frame = ctk.CTkFrame(main_tab, fg_color='#D1E7F0', corner_radius=10)
        bottom_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # bottom frame title
        bottom_title = ctk.CTkLabel(bottom_frame, text="Optimization Results", 
                                   font=('Arial', 12, 'bold'), text_color='black')
        bottom_title.pack(pady=(10, 5))
        
        # text frame
        text_frame = ctk.CTkFrame(bottom_frame, fg_color='white', corner_radius=8)
        text_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.result_text = tk.Text(text_frame, height=8, wrap="word", bg='white', fg='black')
        result_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=result_scrollbar.set)
        
        self.result_text.pack(side="left", fill="both", expand=True)
        result_scrollbar.pack(side="right", fill="y")
        
        # status frame
        status_frame = ctk.CTkFrame(main_tab, fg_color='#B8D4E3', corner_radius=8)
        status_frame.pack(fill="x", side="bottom", padx=10, pady=5)
        
        self.status_label = ctk.CTkLabel(status_frame, text="Ready to optimize budget allocation", 
                                        anchor="w", text_color='black')
        self.status_label.pack(fill="x", padx=10, pady=5)
        
    # create the chart tab
    def create_chart_tab(self):
        chart_tab = ctk.CTkFrame(self.notebook, fg_color='#E6F3FF', corner_radius=10)
        self.notebook.add(chart_tab, text="Allocation Charts")
        
        # create the charts
        self.fig, ((self.ax1, self.ax2), (self.ax3, self.ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        self.fig.suptitle('Budget Allocation Analysis', fontsize=16, fontweight='bold')
        
        # create a canvas that displays the charts
        canvas_frame = ctk.CTkFrame(chart_tab, fg_color='white', corner_radius=10)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.canvas = FigureCanvasTkAgg(self.fig, canvas_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # initialize the empty charts
        self.update_charts()
        
    # emergency mode toggle function
    def toggle_emergency_mode(self):
        is_emergency = self.emergency_mode.get()
        self.emergency_combo.config(state="readonly" if is_emergency else "disabled")
        
        current_emergency_type = self.emergency_type.get()

        # update all projects once the emergency mode is enabled
        for project in self.projects:
            project.set_emergency_priority(is_emergency, current_emergency_type)
        
        self.update_projects_table()
        
        # emergency mode conditions
        if is_emergency:
            self.status_label.configure(text=" Emergency mode enabled - Priority given to critical sectors")
        else:
            self.status_label.configure(text="Normal mode - Standard optimization")
    
    # add projects using dialog
    def show_add_project_dialog(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Add New Project")
        dialog.geometry("450x450")
        dialog.configure(fg_color='#9DCCDE')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # center the dialog on the screen
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # main dialog frame
        main_dialog_frame = ctk.CTkFrame(dialog, fg_color='#D1E7F0', corner_radius=15)
        main_dialog_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # dialog title
        dialog_title = ctk.CTkLabel(main_dialog_frame, text="Add New Project", 
                                   font=('Arial', 16, 'bold'), text_color='black')
        dialog_title.pack(pady=(20, 10))
        
        # create fields that can be filled in
        fields = {}
        
        # name field
        name_frame = ctk.CTkFrame(main_dialog_frame, fg_color="transparent")
        name_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(name_frame, text="Project Name:", text_color='black', width=120, anchor="w").pack(side="left")
        fields['name'] = ctk.CTkEntry(name_frame, width=250, corner_radius=8)
        fields['name'].pack(side="right")
        
        # cost field
        cost_frame = ctk.CTkFrame(main_dialog_frame, fg_color="transparent")
        cost_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(cost_frame, text="Cost (₱):", text_color='black', width=120, anchor="w").pack(side="left")
        fields['cost'] = ctk.CTkEntry(cost_frame, width=250, corner_radius=8)
        fields['cost'].pack(side="right")
        
        # benefit score field
        benefit_frame = ctk.CTkFrame(main_dialog_frame, fg_color="transparent")
        benefit_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(benefit_frame, text="Benefit Score (0-10):", text_color='black', width=120, anchor="w").pack(side="left")
        fields['benefit'] = ctk.CTkEntry(benefit_frame, width=250, corner_radius=8)
        fields['benefit'].pack(side="right")
        
        # benefit score conditions
        warning_label = ctk.CTkLabel(main_dialog_frame, text="Benefit score must be between 0 and 10", 
                               text_color='red', font=('Arial', 9, 'italic'))
        warning_label.pack(pady=2)
        
        # category selection
        category_frame = ctk.CTkFrame(main_dialog_frame, fg_color="transparent")
        category_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(category_frame, text="Category:", text_color='black', width=120, anchor="w").pack(side="left")
        fields['category'] = ttk.Combobox(category_frame, width=35,
                                        values=["Infrastructure", "Health", "Education", 
                                               "Environment", "Social Services", "Economic Development"])
        fields['category'].pack(side="right")
        
        # description field
        desc_frame = ctk.CTkFrame(main_dialog_frame, fg_color="transparent")
        desc_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(desc_frame, text="Description:", text_color='black', width=120, anchor="nw").pack(side="left", anchor="n")
        fields['description'] = tk.Text(desc_frame, width=35, height=5, bg='white', fg='black')
        fields['description'].pack(side="right")
        
        # buttons
        button_frame = ctk.CTkFrame(main_dialog_frame, fg_color="transparent")
        button_frame.pack(pady=20)
        
        # add the project 
        def add_project():
            try:
                name = fields['name'].get().strip()
                cost = float(fields['cost'].get())
                benefit = float(fields['benefit'].get())
                category = fields['category'].get()
                description = fields['description'].get(1.0, "end").strip()
                
                # checks the conditions and also the required fields
                if not name:
                    messagebox.showerror("Error", "Please enter a project name.")
                    return
                
                if cost <= 0:
                    messagebox.showerror("Error", "Cost must be a positive number.")
                    return
                
                if not category:
                    messagebox.showerror("Error", "Please select a category.")
                    return
                
                # this will raise an error if the benefit score is not between 0 and 10
                project = Project(name, cost, benefit, category, description)
                
                # set the priorities if emergency mode is enabled
                if self.emergency_mode.get():
                    project.set_emergency_priority(True)
                
                # add the project to the list
                self.projects.append(project)
                self.update_projects_table()
                dialog.destroy() # close the dialog
                self.status_label.configure(text=f"Project added successfully. Total projects: {len(self.projects)}")

            # shows the errors   
            except ValueError as e:
                messagebox.showerror("Error", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Please enter valid numbers for cost and benefit.\n{str(e)}")
        
        # setting up the add project button
        ctk.CTkButton(button_frame, text="Add Project", command=add_project,
                     fg_color='#2C4E2C', text_color='white', font=('Arial', 10, 'bold'),
                     hover_color='#3e6b3e', corner_radius=8, width=120).pack(side="left", padx=5)
        # setting up the cancel button
        ctk.CTkButton(button_frame, text="Cancel", command=dialog.destroy,
                     fg_color='#DC143C', text_color='white', hover_color='#e6455a',
                     corner_radius=8, width=80).pack(side="left", padx=5)
    
    # optimize the budget allocation
    def optimize_budget(self):
        # check the projects and budget amount if valid
        try:
            budget = float(self.budget_entry.get())
            
            if not self.projects:
                messagebox.showerror("Error", "Please add some projects first.")
                return
            
            if budget <= 0:
                messagebox.showerror("Error", "Please enter a valid positive budget amount.")
                return
            
            self.status_label.configure(text="Optimizing budget allocation...")
            self.root.update()
            
            # optimization with emergency situation consideration
            self.solution = BranchAndBound.solve_knapsack(self.projects, budget, self.emergency_mode.get())
            self.display_solution(budget)
            self.update_charts()
            self.status_label.configure(text="Optimization completed successfully.")

        # handle the errors  
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid budget amount.")
        except Exception as e:
            messagebox.showerror("Error", f"Error during optimization: {str(e)}")
            self.status_label.configure(text="Optimization failed.")
    
    # display the solutions
    def display_solution(self, budget):
        # if there's no solution
        if not self.solution:
            return
        
        # update the solution table
        for item in self.solution_tree.get_children():
            self.solution_tree.delete(item)
        
        for project in self.solution.selected_projects:
            priority_text = f"Emergency P{project.emergency_priority_level}" if project.is_emergency_priority else "Normal"
            self.solution_tree.insert('', 'end', values=(
                project.name,
                f"₱{project.cost:,.2f}",
                f"{project.benefit:.2f}",
                project.category,
                priority_text
            ))
        
        # update the bottom text area
        result_text = "=== BUDGET ALLOCATION OPTIMIZATION RESULTS ===\n\n"
        
        if self.emergency_mode.get():
            result_text += f"EMERGENCY MODE: {self.emergency_type.get()}\n"
            result_text += "Priority given to critical infrastructure and services\n\n"
        
        result_text += f"Total Budget: ₱{budget:,.2f}\n"
        result_text += f"Allocated Amount: ₱{self.solution.total_cost:,.2f} ({(self.solution.total_cost / budget) * 100:.1f}%)\n"
        result_text += f"Remaining Budget: ₱{budget - self.solution.total_cost:,.2f}\n"
        result_text += f"Total Benefit Score: {self.solution.total_benefit:.2f}\n"
        result_text += f"Efficiency Ratio: {self.solution.efficiency:.3f}\n\n"
        
        result_text += "Selected Projects (Priority Order):\n"
        result_text += "─" * 60 + "\n"
        
        for project in self.solution.selected_projects:
            priority_indicator = f" P{project.emergency_priority_level}" if project.is_emergency_priority else ""
            result_text += f"• {project.name}{priority_indicator}\n"
            result_text += f"  Cost: ₱{project.cost:,.2f} | Benefit: {project.benefit:.2f} | Category: {project.category}\n"
        
        # breakdown the categories
        result_text += "\nCategory Breakdown:\n"
        category_totals = defaultdict(lambda: {'count': 0, 'cost': 0})
        for project in self.solution.selected_projects:
            category_totals[project.category]['count'] += 1
            category_totals[project.category]['cost'] += project.cost
        
        for category, data in category_totals.items():
            result_text += f"• {category}: {data['count']} projects, ₱{data['cost']:,.2f}\n"
        
        self.result_text.delete(1.0, "end")
        self.result_text.insert(1.0, result_text)
    
    # update the charts
    def update_charts(self):
        # clear all the axes
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.clear()
        
        if not self.solution or not self.solution.selected_projects:
            # show empty state if there's no solution
            self.ax1.text(0.5, 0.5, 'No data available\nRun optimization first', 
                         ha='center', va='center', transform=self.ax1.transAxes, fontsize=12)
            self.ax2.text(0.5, 0.5, 'No data available\nRun optimization first', 
                         ha='center', va='center', transform=self.ax2.transAxes, fontsize=12)
            self.ax3.text(0.5, 0.5, 'No data available\nRun optimization first', 
                         ha='center', va='center', transform=self.ax3.transAxes, fontsize=12)
            self.ax4.text(0.5, 0.5, 'No data available\nRun optimization first', 
                         ha='center', va='center', transform=self.ax4.transAxes, fontsize=12)
        else:
            self._create_budget_utilization_chart()
            self._create_category_breakdown_chart()
            self._create_project_comparison_chart()
            self._create_priority_distribution_chart()
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    # create the budget utilization pie chart
    def _create_budget_utilization_chart(self):
        budget = float(self.budget_entry.get()) if self.budget_entry.get() else 0
        if budget <= 0:
            return
        
        # calculate the allocated and remaining budget
        allocated = self.solution.total_cost
        remaining = budget - allocated
        
        # define the sizes, labels, and colors for the pie chart
        sizes = [allocated, remaining]
        labels = ['Allocated', 'Remaining']
        colors = ['#32CD32', '#FF6347']
        
        # plot the pie chart
        wedges, texts, autotexts = self.ax1.pie(sizes, labels=None, colors=colors, autopct='%1.1f%%', startangle=90, pctdistance=0.85)
        self.ax1.set_title('Budget Utilization')
        self.ax1.legend(wedges, labels, title="Status", loc="center left", bbox_to_anchor=(1,0,0.5,1))
        self.ax1.axis('equal')
    
    # create the category breakdown pie chart
    def _create_category_breakdown_chart(self):
        # calculate the total cost per category
        category_totals = defaultdict(float)
        for project in self.solution.selected_projects:
            category_totals[project.category] += project.cost
        
        if category_totals:
            categories = list(category_totals.keys())
            costs = list(category_totals.values())
            colors = plt.cm.Set3(np.linspace(0, 1, len(categories)))
            # plot the pie chart
            wedges, texts, autotexts = self.ax2.pie(costs, labels=None, colors=colors, autopct='%1.1f%%', startangle=90, pctdistance=0.85)
            self.ax2.set_title('Allocation by Category')
            self.ax2.legend(wedges, categories, title="Categories", loc="center left", bbox_to_anchor=(1,0,0.5,1))
            self.ax2.axis('equal')   

    # create the project comparison bar chart
    def _create_project_comparison_chart(self):
        # show top 10 projects by cost if there are more than 10 projects
        if len(self.solution.selected_projects) > 10:
            projects = sorted(self.solution.selected_projects, key=lambda x: x.cost, reverse=True)[:10]
        else:
            projects = self.solution.selected_projects
        
        # define the names, cost, and benefits for the bar chart
        names = [p.name[:15] + '...' if len(p.name) > 15 else p.name for p in projects]
        costs = [p.cost for p in projects]
        benefits = [p.benefit for p in projects]
        
        # define the bar chart
        x = np.arange(len(names))
        width = 0.15
        
        # create the bar chart for costs and benefits
        bars1 = self.ax3.bar(x - width/2, costs, width, label='Cost (₱)', color='#4169E1', alpha=0.7)
        bars2 = self.ax3.bar(x + width/2, [b * 1000 for b in benefits], width, label='Benefit (×1000)', color='#32CD32', alpha=0.7)
        
        # add labels and title
        self.ax3.set_xlabel('Projects')
        self.ax3.set_ylabel('Amount')
        self.ax3.set_title('Selected Projects - Cost vs Benefit')
        self.ax3.set_xticks(x)
        self.ax3.set_xticklabels(names, rotation=90, ha='right')
        self.ax3.legend()
    
    # create the emergency priority distribution chart
    def _create_priority_distribution_chart(self):
        # check if emergency mode is enabled and if there are projects selected
        if self.emergency_mode.get():
            priority_counts = defaultdict(int)
            for project in self.solution.selected_projects:
                if project.is_emergency_priority:
                    priority_counts[f"Priority {project.emergency_priority_level}"] += 1
                else:
                    priority_counts["Normal"] += 1 # normal priority projects
            
            # if there are emergency priority projects
            if priority_counts:
                priorities = list(priority_counts.keys())
                counts = list(priority_counts.values())
                colors = ['#FF4500', '#FF6347', '#FFA500', '#FFD700', '#90EE90', '#87CEEB']
                
                # plot the bar chart
                bars = self.ax4.bar(priorities, counts, color=colors[:len(priorities)])
                self.ax4.set_title('Emergency Priority Distribution')
                self.ax4.set_ylabel('Number of Projects')
                
                # edit the bars of the bar chart
                for bar in bars:
                    height = bar.get_height()
                    self.ax4.text(bar.get_x() + bar.get_width()/2., height,
                                f'{int(height)}', ha='center', va='bottom')
        else: # if emergency mode is not enabled
            self.ax4.text(0.5, 0.5, 'Emergency mode not enabled',
                         ha='center', va='center', transform=self.ax4.transAxes, fontsize=12)
            self.ax4.set_title('Emergency Priority Distribution')
    
    # update projects table
    def update_projects_table(self):

        # clear the existing projects in the table
        for item in self.projects_tree.get_children():
            self.projects_tree.delete(item)
        
        #  return project values to the table
        for project in self.projects:
            priority_text = f"Emergency P{project.emergency_priority_level}" if project.is_emergency_priority else "Normal"
            self.projects_tree.insert('', 'end', values=(
                project.name,
                f"₱{project.cost:,.2f}",
                f"{project.benefit:.2f}",
                f"{project.benefit_cost_ratio:.3f}",
                project.category,
                priority_text
            ))
    # remove selected project from the projects table
    def remove_selected_project(self):
        selection = self.projects_tree.selection()
        if not selection: # if there's no selected projects
            messagebox.showwarning("Warning", "Please select a project to remove.")
            return
        
        # store the project in a list and get the index of the selected project
        item = selection[0]
        index = self.projects_tree.index(item)
        project_name = self.projects[index].name
        
        # confirm the removal
        result = messagebox.askyesno("Confirm Removal", 
                                   f"Are you sure you want to remove project: {project_name}?")
        # if the user picked yes
        if result:
            del self.projects[index]
            self.update_projects_table()
            
            # clear the solution if the removed project was part of it
            for item in self.solution_tree.get_children():
                self.solution_tree.delete(item)
            self.result_text.delete(1.0, "end")
            self.solution = None
            self.update_charts()
            
            self.status_label.configure(text=f"Project removed. Total projects: {len(self.projects)}")
    
    # clear all projects from the projects table
    def clear_all_projects(self):
        # if there are no projects to clear
        if not self.projects:
            return
        
        # confirm the clearing operation
        result = messagebox.askyesno("Confirm Clear", 
                                   "Are you sure you want to clear all projects?")
        
        # if the user picked yes
        if result:
            self.projects.clear()
            self.update_projects_table()
            
            # clear the solution and result text
            for item in self.solution_tree.get_children():
                self.solution_tree.delete(item)
            self.result_text.delete(1.0, "end")
            self.solution = None
            self.update_charts()
            
            self.status_label.configure(text="All projects cleared.")

# main function
def main():
    root = ctk.CTk()
    app = BudgetAllocationGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
