from fa import FA, get_alphabet
from tompson_algorithm import TompsonAlgorithm


class DeterminizationAlgorithm:

    def __init__(self, nfa, alphabet):
        self.nfa = nfa    
        self.alphabet = alphabet


    def _build_subsets(self):
        last_state = 0
        gen_states = {}

        transition_table ={}

        closure = self._closure([self.nfa.initial_state], self.nfa.transition_table)
        gen_states = {last_state: set(closure)}
        last_state += 1
        print "closure:", closure
        print "gen states:", gen_states

        d_states = [set(closure)]
        print "d_states:", d_states
        unmarked = [set(closure)]
        print "unmarked:", unmarked

        while unmarked:
            print "==============================="
            T = unmarked.pop()
            print "t:", T
            print "closure:", closure
            print "unmarked:", unmarked
            print "gen_states:", gen_states
            print "************************************************"
            transitions = {}
            for a in self.alphabet:   
                print "a:", a        
                mv = self._move(list(T), a, self.nfa.transition_table)
                print "mv:", mv
                U = set(self._closure(mv, self.nfa.transition_table))
                print "u:", U
                if U:
                    print "d_states:", d_states
                    if U not in d_states:
                        d_states.append(U)
                        gen_states[last_state] = U
                        last_state += 1
                        unmarked.append(U)

                    print "d_states:", d_states
                    print "unmarked:", unmarked
                    transitions.update({a: [self.get_key_by_value(gen_states, U)]})
                    print "Dtran:", transition_table
                    print "************************************************"
            transition_table[self.get_key_by_value(gen_states, T)] = transitions   
        return FA(transition_table, self.nfa.initial_state, self.nfa.final_state)

    def get_key_by_value(self, dictionary, value):
        for key, item in dictionary.items():
            if item == value:
                return key
        raise Exception()

    def _closure(self, T, transition_table):
        stack = list(T)
        closure = list(T)
        while stack:
            t = stack.pop()
            for u in transition_table[t].get(FA.EMPTY, []):
                if u not in closure:
                    closure.append(u)
                    stack.append(u)
        return closure

    def _move(self, T, a, transition_table):
        result = set()
        for s in T:
            states = set(transition_table[s].get(a, []))
            result = result.union(states)
        return result

    def _clear(self, transition_table): 
        result = {}
        for key in transition_table.keys():
            transitions = transition_table.get(key, {})
            for ch in transitions.keys():
                states = {}
                if ch != FA.EMPTY and transitions[ch]:
                    states[ch] = transitions[ch]
                if states:
                    result[key] = states
        return result

regexp = "aaabbb"
alg1 = TompsonAlgorithm(regexp)
fa = alg1.buildNFA()
fa.draw('graph')

alg2 = DeterminizationAlgorithm(fa, ['a', 'b'])
fa2 = alg2._build_subsets()
fa2.draw('graph2') 
