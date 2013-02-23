from grammar import (Symbol , EmptySymbol,Terminal, 
					 Nonterminal, ComplexNonterminal, Rule, Grammar)


def find_disappearing_nonterminals(grammar):
	# initialize disappearing nonterminals set
	disappearing_nonterminals = set()
	for rule in grammar.rules:
		if (len(rule.right_side) == 1 and
				rule.right_side[0] == EmptySymbol()):
			disappearing_nonterminals.add(rule.left_side[0])		
			
	# find other disappearing nonterminals
	new_disappearing_nonterminals = set(disappearing_nonterminals)
	disappearing_nonterminals = set()
	while disappearing_nonterminals != new_disappearing_nonterminals:
		disappearing_nonterminals = set(new_disappearing_nonterminals)
		for rule in grammar.rules:
			output_symbols = set(rule.right_side)
			if output_symbols.issubset(new_disappearing_nonterminals):
				new_disappearing_nonterminals.add(rule.left_side[0])

	return disappearing_nonterminals


def has_empty_chain(grammar):
	disappearing_nonterminals = find_disappearing_nonterminals(grammar)				
	return grammar.axiom in disappearing_nonterminals 


###############################################################################
def convert_grammar(grammar, disappearing_nonterminals):
	new_grammar = Grammar()

	# build new nonterminals set
	new_grammar.nonterminals = build_new_nonterminals_set(
		grammar, disappearing_nonterminals)

	# find new axiom
	if grammar.axiom in disappearing_nonterminals:
		# language has empty chain
		new_grammar.axiom = Nonterminal(grammar.axiom.name, False)
		new_grammar.nonterminals.add(new_grammar.axiom)
		new_grammar.nonterminals.remove(grammar.axiom)
	else:
		new_grammar.axiom = grammar.axiom

	# build new rules
	new_grammar.rules = build_new_rules(
		grammar, disappearing_nonterminals, new_grammar.nonterminals)

	# copy terminals	
	new_grammar.terminals = set(grammar.terminals)
	return new_grammar


def build_new_nonterminals_set(grammar, disappearing_nonterminals):
	new_nonterminals = set(grammar.nonterminals)
	for nonterminal in grammar.nonterminals:
		if nonterminal in disappearing_nonterminals:
			new_nonterminals.add(Nonterminal(nonterminal.name, False))
	return new_nonterminals	


def build_new_rules(grammar, disappearing_nonterminals, new_nonterminals):
	new_rules = []
	for rule in grammar.rules:
		if not rule.is_empty():
			idx = find_left_nonnullable_symbol_idx(rule)	

			adding_rules = build_adding_rules(rule, idx)
			new_rules.extend(adding_rules)			

			if rule.left_side[0] in disappearing_nonterminals:
				for adding_rule in adding_rules:
					left_side = [adding_rule.left_side[0].create_nonnullable_nonterminal()]
					right_side = list(adding_rule.right_side)
					new_rules.append(Rule(left_side, right_side))
		else:
			new_rules.append(rule)	

	new_cleared_rules = []
	for rule in new_rules:
		if rule.left_side[0] in new_nonterminals:
			new_cleared_rules.append(rule)

	return new_cleared_rules
	
def find_left_nonnullable_symbol_idx(rule):
	idx = 0
	for symbol in rule.right_side:
		if not symbol.is_nullable:
			return idx
		idx += 1
	return idx


def build_adding_rules(rule, idx):
	adding_rules = []
	for i in range(idx):
		left_side = list(rule.left_side)
		right_side = [rule.right_side[i].create_nonnullable_nonterminal()]
		right_side.extend(rule.right_side[i + 1:])
		adding_rules.append(Rule(left_side, right_side))

	if idx < len(rule.right_side):
		left_side = list(rule.left_side)
		right_side = rule.right_side[idx:]				
		adding_rules.append(Rule(left_side, right_side))
	return adding_rules
###############################################################################


###############################################################################
def delete_empty_rules(grammar):
	disappearing_nonterminals = find_disappearing_nonterminals(grammar)

	converted_grammar = convert_grammar(grammar, disappearing_nonterminals)
	print "converted_grammar:"
	print converted_grammar

	cleared_grammar = delete_useless_nonterminals(converted_grammar)
	print "cleared_grammar:"
	print cleared_grammar

	return build_new_grammar(cleared_grammar)


def find_rules_for_nonterminal(rules, nonterminal):
	selected_rules = []
	for rule in rules:
		if rule.left_side[0] == nonterminal:
			selected_rules.append(rule)
	return selected_rules


def replace_nonterminal(chain, idx, inserted_symbols):
	new_chain = []
	if idx > 0:
		new_chain = chain[:idx]
	new_chain.extend(inserted_symbols)
	if (idx + 1) < len(chain):
		new_chain.extend(chain[idx + 1:])
	return new_chain


def build_new_grammar(grammar):
	new_grammar = Grammar()
	new_grammar.terminals = set(grammar.terminals)
	new_grammar.axiom = ComplexNonterminal(
		[grammar.axiom], grammar.axiom.is_nullable)
	print "axiom:", new_grammar.axiom

	new_rules = []
	rules = grammar.rules
	unwatched = [new_grammar.axiom]
	watched = set()
	while unwatched:
		print "***************************************************************"
		print "unwatched:", [str(symbol) for symbol in unwatched]
		print "watched:", [str(symbol) for symbol in watched]

		complex_nonterminal = unwatched[0]
		unwatched.remove(complex_nonterminal)
		watched.add(complex_nonterminal)
		print "complex nonterminal:", str(complex_nonterminal)

		if complex_nonterminal.starts_with_nonterminal():
			print "starts_with_nonterminal"
			nonterminal_rules = find_rules_for_nonterminal(rules, complex_nonterminal.name[0])
			for rule in nonterminal_rules:
				if not rule.is_empty():
					print "rule:", rule
					left_side = [complex_nonterminal]

					new_name = replace_nonterminal(complex_nonterminal.name, 0, rule.right_side)
					new_complex_nonterminal = ComplexNonterminal(new_name)
					right_side = [new_complex_nonterminal]
					if (new_complex_nonterminal not in watched and
							new_complex_nonterminal not in unwatched):
						unwatched.append(new_complex_nonterminal)				

					new_rule = Rule(left_side, right_side)
					print "new_rule:", new_rule
					new_rules.append(new_rule)
			
		elif complex_nonterminal.starts_with_terminal():
			print "starts_with_terminal"
			symbols = complex_nonterminal.name
			for idx in range(1, len(symbols)):
				symbol = symbols[idx]
				print "symbol:", symbol

				if (isinstance(symbol, Terminal) or 
						(isinstance(symbol, Nonterminal) and not symbol.is_nullable)):
					break

				selected_rules = find_rules_for_nonterminal(rules, symbol)
				for rule  in selected_rules:
					if not rule.is_empty():
						print "rule:", rule
						left_side = [complex_nonterminal]

						new_name = list(rule.right_side)
						if (idx + 1) < len(symbols):
							new_name.extend(symbols[idx + 1:])
						new_complex_nonterminal = ComplexNonterminal(new_name)
						right_side = [symbols[0], new_complex_nonterminal]
						if (new_complex_nonterminal not in watched and
								new_complex_nonterminal not in unwatched):
							unwatched.append(new_complex_nonterminal)
					
						new_rule = Rule(left_side, right_side)
						print "new_rule:", new_rule
						new_rules.append(new_rule)

			new_rule = Rule([complex_nonterminal], [symbols[0]])
			print "new_rule:", new_rule
			new_rules.append(new_rule)

					
	new_grammar.rules = new_rules
	new_grammar.nonterminals = watched
	return new_grammar

#################################################
def delete_useless_nonterminals(grammar):
	new_rules = list(grammar.rules)
	new_nonterminals = set(grammar.nonterminals)

	while True:
		useless_nonterminals = find_useless_nonterminals(new_rules)
		if not useless_nonterminals:
			break

		new_rules = delete_useless_nonterminals_from_rules(new_rules, useless_nonterminals)
		new_rules = delete_useless_nonterminals_rules(new_rules, useless_nonterminals)
		new_nonterminals.difference_update(useless_nonterminals) 

	new_grammar = Grammar()
	new_grammar.axiom = grammar.axiom
	new_grammar.terminals = set(grammar.terminals)
	new_grammar.nonterminals = new_nonterminals
	new_grammar.rules = new_rules
	return new_grammar


def find_useless_nonterminals(rules):
	useless_nonterminals = set()
	normal_nonterminals = set()

	for rule in rules:
		nonterminal = rule.left_side[0]
		if not rule.is_empty():
			normal_nonterminals.add(nonterminal)
			if nonterminal in useless_nonterminals:
				useless_nonterminals.remove(nonterminal)
		elif nonterminal not in normal_nonterminals:
			useless_nonterminals.add(nonterminal)

	return useless_nonterminals


def delete_useless_nonterminals_from_rules(rules, useless_nonterminals):
	new_cleared_rules = []
	for rule in rules:
		right_side = rule.right_side
		if not rule.is_empty():
			rule = delete_useless_nonterminals_from_rule(rule, useless_nonterminals)
		new_cleared_rules.append(rule)
	return new_cleared_rules
		

def delete_useless_nonterminals_from_rule(rule, useless_nonterminals):
	left_side = list(rule.left_side)
	right_side = list(rule.right_side)
	for nonterminal in useless_nonterminals:
		while nonterminal in right_side:
			right_side.remove(nonterminal)
	if len(right_side) == 0:
		right_side = [EmptySymbol()]
	return Rule(left_side, right_side)
	

def delete_useless_nonterminals_rules(rules, useless_nonterminals):
	new_cleared_rules = []
	for rule in rules:
		nonterminal = rule.left_side[0]
		if nonterminal not in useless_nonterminals:
			new_cleared_rules.append(rule)
	return new_cleared_rules
################################################




###############################################################################

