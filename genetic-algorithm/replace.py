import sys
import os
import time
import copy

class Formula:
    
    def __init__(self, raw_cnf):
        """
        Initialise a Formula from a raw CNF string.

        raw_cnf -- a string in the .cnf format
        """
        self.next_fresh = 0
        self.literal_locations = {}
        self.clauses = []
        lines = raw_cnf.split("\n")
        for line in lines:
            if len(line) == 0 or line[0] == "c" or line[0] == "p":
                pass
            else:
                parts = [int(part) for part in line.strip().split(" ") if part != ""]
                self.add_clause(parts[:-1])

    def clone(self):
        f = Formula("")
        f.next_fresh = self.next_fresh
        f.literal_locations = copy.deepcopy(self.literal_locations)
        f.clauses = copy.deepcopy(self.clauses)
        return f

    def add_clause(self, literals):
        self.clauses += [literals]
        # Add this clause to the location list for each literal so we
        # can find it quickly later
        for literal in literals:
            self.use_variable(abs(literal))
            try:
                self.literal_locations[literal] += [len(self.clauses) - 1]
            except:
                # That list didn't exist yet
                self.literal_locations[literal] = [len(self.clauses) - 1]

    def find_clauses_containing(self, literals):
        try:
            clause_numbers = self.literal_locations[literals[0]]
            for literal in literals[1:]:
                new_clause_numbers = []
                other_clause_numbers = self.literal_locations[literal]
                i, j = 0, 0
                while i < len(clause_numbers) and j < len(other_clause_numbers):
                    if clause_numbers[i] == other_clause_numbers[j]:
                        new_clause_numbers += [clause_numbers[i]]
                        i += 1
                        j += 1
                    elif clause_numbers[i] < other_clause_numbers[j]:
                        i += 1
                    else:
                        j += 1
                clause_numbers = new_clause_numbers
            return clause_numbers
        except:
            # We looked for literals that we don't have
            return []

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

    def extend(self, variables):
        """
        Perform the extension rule, introducting a new variable
        x = v1 or v2 or ... or vN for vi in variables.

        variables -- the list of variables to be disjoined in the extension
        """
        x = self.get_fresh_variable()
        var_set = set(variables)
        for clause_number in self.find_clauses_containing(variables):
            new_clause = [x]
            for literal in self.clauses[clause_number]:
                if literal not in var_set:
                    new_clause += [literal]
            self.clauses[clause_number] = new_clause
        self.add_clause([-x] + variables)
        for variable in variables:
            self.add_clause([-variable, x])

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

if __name__ == "__main__":
    formula_filename = sys.argv[1]
    subclause_filename = sys.argv[2]
    output_filename = sys.argv[3]

    start_time = time.time()
    with open(formula_filename) as formula_file:
        formula = Formula(formula_file.read())
    print "Time to open formula: ", time.time() - start_time

    start_time = time.time()
    try:
        with open(subclause_filename) as subclause_file:
            subclause_lines = subclause_file.readlines()
    except:
        subclause_lines = []
    print "Time to open subclauses: ", time.time() - start_time

    print "Variables before substitutions: ", formula.next_fresh

    start_time = time.time()
    for subclause_line in subclause_lines:
       subclause = subclause_line.split(" ")[:-1]
       formula.extend([int(l) for l in subclause])
    print "Time to make replacements: ", time.time() - start_time

    print "Variables after substitutions: ", formula.next_fresh

    with open(output_filename, "w") as output_file:
        output_file.write(formula.to_cnf_file())
