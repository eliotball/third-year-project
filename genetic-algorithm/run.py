import genetic
import replace
import sys

import os
import math

def is_int(candidate):
    try:
        int(candidate)
        return True
    except ValueError:
        return False

def get_subclauses_from_file(file_name):
    os.system("mkfifo clauses-%s.fifo lines-%s.fifo" % (file_name, file_name)
    os.system("cat \"" + file_name + "\" | perl -pe 's/ 0 *$//g' | tail -n +2 > lines-%s.fifo &" % file_name)
    os.system("./apriori -m2 -n3 -s-30 lines%s.fifo clauses-%s.fifo &" % (file_name, file_name))
    subclauses = []
    with open("clauses-%s.fifo" % file_name, "r") as fifo:
        for line in fifo:
            subclauses += [[int(literal) for literal in line.split(" ") if is_int(literal)]]
    os.system("rm clauses-%s.fifo lines-%s.fifo" % (file_name, file_name))
    return subclauses

def get_formula_from_file(file_name):
    with open(file_name) as cnf_file:
        return replace.Formula(cnf_file.read())


class SolverResult:
    def __init__(self, output):
        self.output = output
        self.restarts = self.get_stat("restarts", "\n", int)
        self.conflicts = self.get_stat("conflicts", "(", int)
        self.decisions = self.get_stat("decisions", "(", int)
        self.propagations = self.get_stat("propagations", "(", int)
        self.conflict_literals = self.get_stat("conflict literals", "(", int)
        self.time = self.get_stat("CPU time", "s", float)

    def get_stat(self, name, end_marker, finish=lambda x: x):
        return finish(self.output.split(name)[1].split(": ")[1].split(end_marker)[0].strip())
    
    def get_bundle(self):
        return {
            "restarts": self.restarts,
            "conflics": self.conflicts,
            "decisions": self.decisions,
            "propagations": self.propagations,
            "conflict_literals": self.conflict_literals,
            "time": self.time
        }
    
    def __lt__(self, other):
        return self.time < other.time


def run_solver_with_replacements(cnf, replacements):
    new_formula = cnf.clone()
    for replacement in replacements:
        new_formula.extend(replacement)
    with open("replaced.cnf", "w") as cnf:
        cnf.write(new_formula.to_cnf_file())
    output = os.popen("./minisat replaced.cnf").read()
    os.system("rm replaced.cnf")
    return SolverResult(output)

def get_subclauses_from_mask(subclauses, mask):
    used_subclauses = []
    for i in xrange(len(mask)):
        if mask[i]:
            used_subclauses += [subclauses[i]]
    return used_subclauses

def run_genetic_algorithm(formula, subclauses, log_name):
    threshold = 0.005
    print "INITIAL RUN"
    with open(log_name, "w") as log_file:
        population = genetic.Population(string_length=len(subclauses),
                size=50, select_best=25)  # should be 5000, 50
        def scoring_function(mask):
            used_subclauses = get_subclauses_from_mask(subclauses, mask)
            result = run_solver_with_replacements(formula, used_subclauses)
            return result.time, result.get_bundle()
        good_example = population.get_good_example(scoring_function,
                threshold=threshold, recording=True, log_file=log_file)
    print "CHECKING IF RESULT IS MAINTAINED"
    with open(log_name, "r") as log_file:
        # Check that the run is the same next time
        population.audit(scoring_function, log_file);
    return get_subclauses_from_mask(subclauses, good_example)

def get_time_distribution(formula, repeats=10):
    times = []
    for i in xrange(repeats):
        this_time = get_time_from_output(
                run_solver_with_replacements(formula, []))
        print "Run %s: %s" % (i + 1, this_time)
        times += [this_time]
    mean = sum(times) / repeats
    print ""
    print "Mean:    %6f (%6f)" % (mean, mean / mean)
    median = sorted(times)[repeats // 2]
    print "Median:  %6f (%6f)" % (median, median / mean)
    the_range = max(times) - min(times)
    print "Range:   %6f (%6f)" % (the_range, the_range / mean)
    print "  Max:   %6f (%6f)" % (max(times), max(times) / mean)
    print "  Min:   %6f (%6f)" % (min(times), min(times) / mean)
    std_dev = math.sqrt(sum([(val - mean)**2.0 for val in times]) / repeats)
    print "Std dev: %6f (%6f)" % (std_dev, std_dev / mean)

if __name__ == "__main__":
    formula_file = sys.argv[1]
    log_name = sys.argv[2]
    subclauses = get_subclauses_from_file(formula_file)
    print "RUN FOR %s" % formula_file
    print str(len(subclauses)) + " repeated subclauses found"
    formula = get_formula_from_file(formula_file)
    result = run_genetic_algorithm(formula, subclauses, log_name=log_name)
    print str(len(result)) + " of " + str(len(subclauses)) + " selected by genetic algorithm"
    print result
    before_time = time_accurately(formula, [])
    dumb_time = time_accurately(formula, subclauses)
    found_time = time_accurately(formula, result)
    print "Found solution which is " + str(100 * (1 - found_time / dumb_time)) + "% better than using all the subclauses"
    print "  and " + str(100 * (1 - found_time / before_time)) + "% better than using the original formula"
