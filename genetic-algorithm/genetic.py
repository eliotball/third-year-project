import random
import operator
import time

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

    def improve(self, scoring_function, mutation_probability=0.01):
        scores = []
        for member in self.members:
            scores += [(member, scoring_function(member))]
        total_fitness = sum([score[1] for score in scores])
        scores.sort(key=operator.itemgetter(1))  # smaller is better
        best_few = scores[:self.select_best]
        self.generate_new_members(best_few, mutation_probability)
        return total_fitness

    def generate_new_members(self, best_few, mutation_probability=0.01):
        self.members = [i[0] for i in best_few]
        for member_count in xrange(len(best_few), self.size):
            left_parent = random.choice(best_few)[0]
            right_parent = random.choice(best_few)[0]
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

    def get_good_example(self, scoring_function, threshold=0.001):
        start_time = time.time()
        last_fitness = self.improve(scoring_function)
        print "Iteration 1    Pop fitness: " + str(last_fitness)
        this_fitness = self.improve(scoring_function)
        print "Iteration 2    Pop fitness: " + str(this_fitness)
        iterations = 2
        converged_for = 0
        mutation_probability = 0.05
        while converged_for < 3:
            last_fitness = this_fitness
            mutation_probability *= 0.95  # decay mutations for tuning
            this_fitness = self.improve(scoring_function, mutation_probability)
            if 1 - threshold < float(this_fitness) / last_fitness < 1 + threshold:
                converged_for += 1
            else:
                converged_for = 0
            iterations += 1
            print "Iteration " + str(iterations) + "    Pop fitness: " \
                    + str(this_fitness) + "   Converging for " + str(converged_for) \
                    + "   Time: " + str(round(time.time() - start_time, 2)) + "s"
        return self.members[0]

p = Population()
