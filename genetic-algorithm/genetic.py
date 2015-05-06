import random
import operator
import time
import json

def random_bit():
    return random.random() > 0.5

def bits_on(seq):
    # For testing
    count = 0
    for item in seq:
        if item == True:
            count += 1
    return count

class Population():
    def __init__(self, string_length=20, size=1000, select_best=50):
        self.size = size
        self.select_best = select_best
        self.members = [[random_bit() for j in xrange(string_length)] 
                        for i in xrange(size - 2)]
        self.members += [[True for i in xrange(string_length)]]
        self.members += [[False for i in xrange(string_length)]]

    def members_to_string(self, members):
        member_strings = []
        for member in members:
            member_strings += [""]
            for bit in member:
                if bit == True:
                    member_strings[-1] += "1"
                else:
                    member_strings[-1] += "0"
        member_strings.sort()
        return " ".join(member_strings)

    def __repr__(self):
        return self.members_to_string(self.members)

    def get_members_from_string(self, string):
        members = []
        for member_string in string.split(" "):
            members += [[]]
            for bit in member_string:
                if bit == "0":
                    members[-1] += [False]
                elif bit == "1":
                    members[-1] += [True]
        return members

    def get_best_few(self, scoring_function):
        scores = []
        for member in self.members:
            score, other_data = scoring_function(member)
            scores += [{
                "member": member,
                "score": score,
                "other_data": other_data
            }]
            scores.sort(key=lambda s: s["score"])  # smaller is better
        total_fitness = sum([score["score"] for score in scores])
        return total_fitness, [i["member"] for i in scores[:self.select_best]], scores

    def improve(self, scoring_function, mutation_probability=0.01,
            recording=False, log_file=None):
        total_fitness, best_few, all_scores = self.get_best_few(scoring_function)
        if recording:
            log_line = {}
            log_line["members"] = str(self)
            log_line["best_few"] = self.members_to_string(best_few)
            for score in all_scores:
                score["member"] = self.members_to_string([score["member"]])
            log_line["all_scores"] = all_scores
            log_file.write(json.dumps(log_line) + "\n")
        self.generate_new_members(best_few, mutation_probability)
        return total_fitness

    def audit(self, scoring_function, log_file):
        while True:
            next_line = log_file.readline()
            if next_line.strip() == "":
                break
            self.members = self.get_members_from_string(next_line)
            _, best_few = self.get_best_few(scoring_function)
            now_best_set = set(self.members_to_string(best_few).split(" "))
            earlier_best_set = set(log_file.readline().split(" "))
            diff = len(now_best_set ^ earlier_best_set)
            print "Difference from earlier run: %s" % diff

    def generate_new_members(self, best_few, mutation_probability=0.01):
        self.members = best_few
        for member_count in xrange(len(best_few), self.size):
            left_parent = random.choice(best_few)
            right_parent = random.choice(best_few)
            # Crossover
            assert len(left_parent) == len(right_parent)
            crossover_point = random.randint(0, len(left_parent))
            new_member = left_parent[:crossover_point] \
                    + right_parent[crossover_point:]
            # Mutation
            for i in xrange(len(new_member)):
                if random.random() < mutation_probability:
                    new_member[i] = not new_member[i]
            self.members += [new_member]

    def get_good_example(self, scoring_function, threshold=0.001,
            recording=False, log_file=None):
        start_time = time.time()
        last_fitness = self.improve(scoring_function, recording=recording,
                log_file=log_file)
        print "Iteration 1    Pop fitness: " + str(last_fitness)
        this_fitness = self.improve(scoring_function, recording=recording,
                log_file=log_file)
        print "Iteration 2    Pop fitness: " + str(this_fitness)
        iterations = 2
        converged_for = 0
        mutation_probability = 0.05
        while converged_for < 3:
            last_fitness = this_fitness
            mutation_probability *= 0.95  # decay mutations for tuning
            this_fitness = self.improve(scoring_function, mutation_probability,
                    recording=recording, log_file=log_file)
            if 1 - threshold < float(this_fitness) / last_fitness < 1 + threshold:
                converged_for += 1
            else:
                converged_for = 0
            iterations += 1
            print "Iteration " + str(iterations) + "    Pop fitness: " \
                    + str(this_fitness) + "   Converging for " + str(converged_for) \
                    + "   Time: " + str(round(time.time() - start_time, 2)) + "s"
        if recording:
            log_file.write(json.dumps({"final_population": str(self)}))
        return self.members[0]

p = Population()
