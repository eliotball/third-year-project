import genetic
import replace

import os

def is_int(candidate):
    try:
        int(candidate)
        return True
    except ValueError:
        return False

def get_subclauses_from_file(file_name):
    os.system("mkfifo clauses.fifo lines.fifo")
    os.system("cat \"" + file_name + "\" | perl -pe 's/ 0 *$//g' | tail -n +2 > lines.fifo &")
    os.system("./apriori -m2 -n3 -s-30 lines.fifo clauses.fifo &")
    subclauses = []
    with open("clauses.fifo", "r") as fifo:
        for line in fifo:
            subclauses += [[int(literal) for literal in line.split(" ") if is_int(literal)]]
    os.system("rm clauses.fifo lines.fifo")
    return subclauses

def get_formula_from_file(file_name):
    with open(file_name) as cnf_file:
        return replace.Formula(cnf_file.read())

def run_solver_with_replacements(cnf, replacements):
    new_formula = cnf.clone()
    for replacement in replacements:
        new_formula.extend(replacement)
    with open("replaced.cnf", "w") as cnf:
        cnf.write(new_formula.to_cnf_file())
    output = os.popen("./minisat replaced.cnf").read()
    os.system("rm replaced.cnf")
    return output

def get_time_from_output(output):
    return float(output.split("CPU time")[1].split(": ")[1].split(" s")[0])

def get_subclauses_from_mask(subclauses, mask):
    used_subclauses = []
    for i in xrange(len(mask)):
        if mask[i]:
            used_subclauses += [subclauses[i]]
    return used_subclauses

def run_genetic_algorithm(formula, subclauses):
    population = genetic.Population(string_length=len(subclauses), size=5000, select_best=50)
    def scoring_function(mask):
        used_subclauses = get_subclauses_from_mask(subclauses, mask)
        return get_time_from_output(
                run_solver_with_replacements(formula,used_subclauses))
    return get_subclauses_from_mask(subclauses,
            population.get_good_example(scoring_function, threshold=0.005))

if __name__ == "__main__":
    subclauses = get_subclauses_from_file("goldb-heqc-term1mul.cnf")
    print str(len(subclauses)) + " repeated subclauses found"
    formula = get_formula_from_file("test.cnf")
    result = run_genetic_algorithm(formula, subclauses)
    print str(len(result)) + " of " + str(len(subclauses)) + " selected by genetic algorithm"
    print result
    before_time = get_time_from_output(run_solver_with_replacements(formula, []))
    dumb_time = get_time_from_output(run_solver_with_replacements(formula, subclauses))
    found_time = get_time_from_output(run_solver_with_replacements(formula, result))
    print "Found solution which is " + str(100 * (1 - found_time / dumb_time)) + "% better than using all the subclauses"
    print "  and " + str(100 * (1 - found_time / before_time)) + "% better than using the original formula"
