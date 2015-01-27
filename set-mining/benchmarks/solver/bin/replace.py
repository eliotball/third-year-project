import sys
import os

class Formula:
    
    def __init__(self, raw_cnf):
        """
        Initialise a Formula from a raw CNF string.

        raw_cnf -- a string in the .cnf format
        """
        self.next_fresh = 0
        self.clauses = []
        lines = raw_cnf.split("\n")
        for line in lines[1:]:
            fields = line.split(" ")
            self.add_clause(fields[:-1])

    def get_fresh_variable(self):
        """
        Get a fresh variable.
        """
        self.next_fresh += 1
        return self.next_fresh
    
    def use_variable(self, variable):   
        """
        Ensure that a variable will not be returned as a fresh variable later.

        variable -- the variable that shouldn't be returned later
        """
        if self.next_fresh < variable:
            self.next_fresh = variable

    def add_clause(self, literals):
        """
        Add a clause to the formula.

        literals -- a list of integers or strings represeting the literals in
                    the clause
        """
        if len(literals) == 0:
            return  # Don't add empty clauses
        clause = []
        for literal in literals:
            clause += [int(literal)]
            self.use_variable(abs(int(literal)))
        self.clauses += [clause]

    def extend(self, variables):
        """
        Perform the extension rule, introducting a new variable
        x = v1 or v2 or ... or vN for vi in variables.

        variables -- the list of variables to be disjoined in the extension
        """
        new_variable = self.get_fresh_variable()
        for index, clause in enumerate(self.clauses):
            remove_subclause = True
            for variable in variables:
                if variable not in clause:
                    remove_subclause = False
                    break
            if remove_subclause:
                replacement_clause = []
                for literal in clause:
                    if literal not in variables:
                        replacement_clause += [literal]
                self.clauses[index] = replacement_clause + [new_variable]
        self.add_clause([-new_variable] + variables)
        for variable in variables:
            self.add_clause([-variable, new_variable])

    def to_cnf_file(self):
        """
        Create a string representing the file in the .cnf file format.
        """
        result = "p cnf " + str(self.next_fresh) + " " + str(len(self.clauses))
        for clause in self.clauses:
            result += "\n" + " ".join(str(l) for l in clause) + " 0"
        return result


#test_str = """p cnf 5 3
#1 -5 4 0
#-1 5 3 4 0
#-3 -4 0"""
#
#f = Formula(test_str)

formula_filename = sys.argv[1]
subclause_filename = sys.argv[2]

with open(formula_filename) as formula_file:
    formula = Formula(formula_file.read())
try:
    with open(subclause_filename) as subclause_file:
        subclause_lines = subclause_file.readlines()
except:
    subclause_lines = []

for subclause_line in subclause_lines:
   subclause = subclause_line.split(" ")[:-1]
   formula.extend([int(l) for l in subclause])

print formula.to_cnf_file()
