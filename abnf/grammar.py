# -*- coding: UTF-8 -*-
# Copyright (C) 2008 Juan David Ibáñez Palomar <jdavid@itaapy.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Import from the Standard Library
from collections import deque
import sys


# End Of Input
EOI = 0
# Epsilon (the empty alternative)
EPSILON = None
EPSILON_SET = frozenset([EPSILON])


def get_item_set_core(item_set):
    """Returns the core of a LR(1) item set (i.e. the LR(0) item set).
    """
    core = [ (name, i, j) for name, i, j, look_ahead in item_set ]
    return frozenset(core)


def merge_item_sets(a, b):
    """Given two LR(1) item sets merge their look-aheads to return an LALR(1)
    item set.
    """
    c = set()
    for name, i, j, a_look_ahead in a:
        for b_name, b_i, b_j, b_look_ahead in b:
            if b_name == name and b_i == i and b_j == j:
                look_ahead = frozenset(a_look_ahead | b_look_ahead)
                c.add((name, i, j, look_ahead))
                break
    return frozenset(c)


def add_item_to_item_set(item_set, item):
    """Insert the given item into the given item-set, where an item is
    identified by the tuple (name, i, j), the look-ahead is merged.
    """
    name, i, j, look_ahead = item
    for b_item in item_set:
        b_name, b_i, b_j, b_look_ahead = b_item
        if b_name == name and b_i == i and b_j == j:
            item_set.remove(b_item)
            item_set.add((name, i, j, look_ahead | b_look_ahead))
            return
    item_set.add(item)



class BaseContext(object):

    def __init__(self, data):
        self.data = data



class Grammar(object):

    def __init__(self):
        self.rules = {}
        self.symbols = set()
        # The lexical analyser
        self.tokens = [EOI]
        self.lexical_table = None
        # Parsing tables
        self.tables = {}


    #######################################################################
    # API Private
    #######################################################################
    def get_internal_rulename(self, name=None):
        symbols = self.symbols
        if name is None:
            # Used to expand terminal rules (produced while infering the
            # lexical analyser).
            suffixes = [ x[1:] for x in symbols if x[0] == '_']
            suffixes = [ int(x) for x in suffixes if x.isdigit() ]
            suffixes.sort()
            if suffixes:
                name = "_%s" % (suffixes[-1] + 1)
            else:
                name = "_0"
        else:
            # Used to expand repetition and optionality rules.
            n = len(name)
            prefixes = [ x[:-n] for x in symbols if x[-n:] == name ]
            prefixes = [ x for x in prefixes if x == len(x) * "_" ]
            if prefixes:
                prefixes.sort()
                name = '_' + prefixes[-1] + name
            else:
                name = '_' + name

        symbols.add(name)
        return name


    def _expand(self, item_set, first_table):
        rules = self.rules

        new_item_set = set()
        while item_set:
            item = item_set.pop()
            add_item_to_item_set(new_item_set, item)

            name, i, j, look_ahead = item
            rule = rules[name][i]
            # Reduce item
            if j == len(rule):
                continue
            # Terminal
            name = rule[j]
            if not isinstance(name, str):
                continue
            # Non Terminal
            # Find out the look-ahead set
            tail = tuple(rule[j+1:])
            if len(tail) > 0:
                first = first_table[tail]
                if EPSILON in first:
                    look_ahead = look_ahead | (first - EPSILON_SET)
                else:
                    look_ahead = first
            # Expand
            for i in range(len(rules[name])):
                new_item = (name, i, 0, look_ahead)
                add_item_to_item_set(item_set, new_item)

        return frozenset(new_item_set)


    def _find_handles(self, item_set):
        rules = self.rules

        handles = set()
        shift = False
        new_item_set = set()
        for name, i, j, look_ahead in item_set:
            if j == len(rules[name][i]):
                handles.add((name, i, look_ahead))
            else:
                shift = True

        return shift, tuple(handles)


    def _move_symbol(self, item_set, symbol, first_table):
        """In the context of this method, by a symbol we understand both
        non-terminals and terminals (including the End-Of-Input).
        """
        rules = self.rules

        next_item_set = set()
        for item in item_set:
            name, i, j, look_ahead = item
            rule = rules[name][i]
            # Move
            if j < len(rule) and rule[j] == symbol:
                next_item_set.add((name, i, j+1, look_ahead))

        return self._expand(next_item_set, first_table)


    def build_lexical_table(self):
        """Infere a lexical layer from the grammar.
        """
        rules = self.rules

        # Find out the set of terminals as defined in the grammar
        input_terminals = set()
        for symbol in rules:
            for rule in rules[symbol]:
                for element in rule:
                    if isinstance(element, frozenset):
                        input_terminals.add(element)
        input_terminals = list(input_terminals)

        # Compute the set of tokens, where a token is defined by a set of
        # characters that do not appear in any other token.
        tokens = []
        while input_terminals:
            t1 = input_terminals.pop()
            for i in range(len(input_terminals)):
                t2 = input_terminals[i]
                if t1 & t2:
                    del input_terminals[i]
                    input_terminals.append(t1 & t2)
                    if t1 - t2:
                        input_terminals.append(t1 - t2)
                    if t2 - t1:
                        input_terminals.append(t2 - t1)
                    break
            else:
                tokens.append(t1)

        # Build the lexical analyser, a table from character to token id, or
        # None if the character is not allowed in the grammar.
        lexical_table = 256 * [None]
        # Start at 1, the 0 is for End-Of-Input.
        token = 1
        for characters in tokens:
            self.tokens.append(token)
            for char in characters:
                lexical_table[ord(char)] = token
            token += 1
        self.lexical_table = lexical_table

        # Expand the grammar, replace character sets by tokens.
        map = {}
        symbols = rules.keys()
        for symbol in symbols:
            for rule in rules[symbol]:
                for j, element in enumerate(rule):
                    if isinstance(element, frozenset):
                        terminals = [
                            (token+1) for token, chars in enumerate(tokens)
                            if chars.issubset(element) ]
                        if len(terminals) == 1:
                            rule[j] = terminals.pop()
                        else:
                            if element in map:
                                rule[j] = map[element]
                            else:
                                aux = self.get_internal_rulename()
                                rule[j] = aux
                                map[element] = aux
                                rules[aux] = []
                                for terminal in terminals:
                                    rules[aux].append([terminal])


    def get_first_table(self):
        symbols = self.symbols
        rules = self.rules

        first = {}
        # Initialize
        for token in self.tokens:
            first[token] = frozenset([token])
        for symbol in symbols:
            first[symbol] = frozenset()
            for rule in rules[symbol]:
                for i in range(len(rule)):
                    alternative = tuple(rule[i:])
                    first[alternative] = frozenset()
        first[()] = EPSILON_SET
        # Closure
        changed = True
        while changed:
            changed = False
            for symbol in symbols:
                for rule in rules[symbol]:
                    # Inference rule 1: for each rule "N -> x", "first[N]"
                    # must contain "first[x]"
                    alternative = tuple(rule)
                    if not first[alternative].issubset(first[symbol]):
                        first[symbol] |= first[alternative]
                        changed = True
                    # Inference rules 2 and 3
                    for i in range(len(rule)):
                        # Inference rule 2: for each alternative "Ax",
                        # "first[Ax]" must contain "first[A]" (excluding
                        # epsilon).
                        alternative = tuple(rule[i:])
                        aux = first[alternative[0]] - EPSILON_SET
                        if not aux.issubset(first[alternative]):
                            first[alternative] |= aux
                            changed = True
                        # Inference rule 3: for each alternative "Ax" where
                        # "first[A]" contains epsilon, "first[Ax]" must
                        # contain "first[x]"
                        if EPSILON in first[alternative[0]]:
                            aux = first[alternative[1:]]
                            if not aux.issubset(first[alternative]):
                                first[alternative] |= aux
                                changed = True

        return first


    #######################################################################
    # API Private / Pretty Print
    #######################################################################
    def pformat_element(self, element):
        if element is EOI:
            return '$'
        elif isinstance(element, str):
            return element
        else:
            return str(element)


    def pformat_rule(self, name, rule):
        line = [name, '=']
        if len(rule) == 0:
            line.append("ε")
        else:
            for element in rule:
                line.append(self.pformat_element(element))
        return ' '.join(line)


    def pprint_grammar(self):
        symbols = list(self.symbols)
        symbols.sort()
        for name in symbols:
            for rule in self.rules[name]:
                print self.pformat_rule(name, rule)


    def pformat_item(self, item):
        name, i, j, look_ahead = item
        rule = self.rules[name][i]

        line = [name, '=']
        for element in rule[:j]:
            line.append(self.pformat_element(element))
        line.append('•')
        for element in rule[j:]:
            line.append(self.pformat_element(element))

        look_ahead = list(look_ahead)
        look_ahead.sort()
        look_ahead = [ (x == 0 and '$') or str(x) for x in look_ahead ]
        line.append('{%s}' % ','.join(look_ahead))
        return ' '.join(line)


    def pformat_item_set(self, item_set):
        lines = [ self.pformat_item(x) for x in item_set ]
        lines.sort()
        return lines


    def pformat_stack(self, stack, data):
        line = []
        for x in stack:
            # Tokens
            if isinstance(x, int):
                if x == 0:
                    line.append('$')
                    continue
                line.append(str(x))
                continue
            # Non-Terminals
            if isinstance(x[0], str):
                symbol, value = x
                line.append(symbol)
                continue
            # State
            state, start = x
            line.append('S%d' % state)
        return ' '.join(line)


    def pprint_paths(self, paths, data, file=None):
        if file is None:
            file = sys.stdout

        i = 0
        while i < len(paths):
            stack, data_idx = paths[i]
            line = self.pformat_stack(stack, data)
            file.write('(%s) %s\n' % (i, line))
            i += 1
        file.write('\n')


    def build_graph(self, map, token_table, symbol_table):
        lines = []
        lines.append('digraph G {\n')
        # The item sets
        for state in map:
            item_set = map[state]
            item_set = self.pformat_item_set(item_set)
            item_set = '\\l'.join(item_set)
            lines.append('    %s [label="S%s\\n%s\l",shape="box"];\n'
                         % (state, state, item_set))
        # The tokens transitions
        for key in token_table:
            src, label = key
            dst = token_table[key]
            lines.append('    %s -> %s [label="%s"];\n' % (src, dst, label))
        # The symbol transitions
        for key in symbol_table:
            src, label = key
            dst = symbol_table[key]
            lines.append('    %s -> %s [label="%s"];\n' % (src, dst, label))

        lines.append('}\n')

        # Write the file
        file = open('/tmp/graph.dot', 'w')
        file.write(''.join(lines))
        file.close()


    #######################################################################
    # API Public
    #######################################################################
    def add_rule(self, name, *elements):
        """Add a new rule to the grammar, where a rule is defined by its
        name and a sequence of elements:

          rule-name -> element-1 element-2 ...

        Where 'element' may be:

        - a grammar symbol (non terminal)
        - a terminal, expressed as a set of allowed characters
        - a three-elements tuple, to express repetition and optionality,
          like "(min, max, element)"

        For example:

          ABNF         elements
          ===========  ==============
          4 hexdig     (4, hexdig)
          1*4 hexdig   (1, 4, hexdig)

        """
        self.symbols.add(name)
        rules = self.rules.setdefault(name, [])

        stack = [elements]
        while stack:
            elements = stack.pop()
            for index, element in enumerate(elements):
                # Expand
                if isinstance(element, tuple):
                    left = tuple(elements[:index])
                    right = tuple(elements[index+1:])
                    max = element[0]
                    rest = element[1:]
                    if max is None:
                        # Case 1: max = infinitum
                        rest = tuple(rest)
                        aux = self.get_internal_rulename(name)
                        stack.append(left + (aux,) + right)
                        self.add_rule(aux, *(rest + (aux,)))
                        self.add_rule(aux)
                    else:
                        # Case 2: max = n
                        for i in range(max+1):
                            stack.append(left + (i * rest) + right)
                    break
            else:
                elements = list(elements)
                rules.append(elements)


    def get_table(self, start_symbol, context_class=None):
        """Build the parsing tables.
        """
        if start_symbol in self.tables:
            return self.tables[start_symbol]

        if self.lexical_table is None:
            self.build_lexical_table()

        # First table
        first = self.get_first_table()

        # Build the initial set (s0)
        rules = self.rules
        s0 = set()
        for i in range(len(rules[start_symbol])):
            s0.add((start_symbol, i, 0, frozenset([EOI])))
        s0 = self._expand(s0, first)
        # Initialize
        token_table = {}
        symbol_table = {}
        # Local variables
        symbols = rules.keys()
        # Build the shift-tables
        reduce_table = {1: s0}
        s0_core = get_item_set_core(s0)
        states = {s0_core: 1}
        stack = set([s0])
        done = set()
        next_state = 2
        while stack:
            src_item_set = stack.pop()
            done.add(src_item_set)
            core = get_item_set_core(src_item_set)
            src_state = states[core]
            # Reduce table
            a = reduce_table[src_state]
            reduce_table[src_state] = merge_item_sets(a, src_item_set)
            # Chars
            for token in self.tokens:
                dst_item_set = self._move_symbol(src_item_set, token, first)
                if not dst_item_set:
                    continue
                # Find out the destination state
                core = get_item_set_core(dst_item_set)
                if core in states:
                    dst_state = states[core]
                else:
                    states[core] = next_state
                    dst_state = next_state
                    next_state += 1
                    reduce_table[dst_state] = dst_item_set
                if dst_item_set not in done:
                    stack.add(dst_item_set)
                # Add transition
                token_table[(src_state, token)] = dst_state
            # Symbols
            for symbol in symbols:
                dst_item_set = self._move_symbol(src_item_set, symbol, first)
                if not dst_item_set:
                    continue
                # Find out the destination state
                core = get_item_set_core(dst_item_set)
                if core in states:
                    dst_state = states[core]
                else:
                    states[core] = next_state
                    dst_state = next_state
                    next_state += 1
                    reduce_table[dst_state] = dst_item_set
                if dst_item_set not in done:
                    stack.add(dst_item_set)
                # Add transition
                symbol_table[(src_state, symbol)] = dst_state

        # Debug
#        self.pprint_grammar()
#        self.build_graph(reduce_table, token_table, symbol_table)

        # The semantic side of things
        map = {}
        if context_class is not None:
            for name in symbols:
                method_name = name.replace('-', '_').replace("'", '_')
                map[name] = getattr(context_class, method_name, None)

        # Finish the reduce-table
        reduce_table[0] = frozenset()
        # Find handles, calculate rule length and change to a tuple
        aux = []
        for state in reduce_table:
            item_set = reduce_table[state]
            shift, handles = self._find_handles(item_set)
            # A handle is a 4 elements tuple:
            #
            #  rulename, stack-elements-to-pop, look-ahead, semantic-method
            #
            handles = [ (x, 2 * len(rules[x][y]), z, map.get(x))
                        for x, y, z in handles ]
            aux.append((state, (shift, handles)))
        aux.sort()
        aux = [ y for x, y in aux ]
        reduce_table = tuple(aux)

        # Update grammar
        table = token_table, symbol_table, reduce_table
        self.tables[start_symbol] = table
        return table


    def run(self, start_symbol, data, context=None):
        # Get the parsing table
        table = self.get_table(start_symbol)
        token_table, symbol_table, reduce_table = table
        lexical_table = self.lexical_table
        # Initialize the stack, where the stack is a list of tuples:
        #
        #   [(state, start), ...]
        #
        # The "start" field is a reference to the input stream.
        stack = [(1, 0)]
        paths = deque()
        paths.append((stack, 0))

#        file = open('/tmp/trace.txt', 'w')
        rules = self.rules
#        loops = reduces = conflicts = 0
        while paths:
#            loops += 1
#            self.pprint_paths(paths, data, file)
            stack, data_idx = paths.pop()
            # Stop condition
            state, start = stack[-1]
            if state == 0 and len(stack) == 3:
                last_symbol = stack[1]
                if isinstance(last_symbol, tuple):
                    if last_symbol[0] == start_symbol:
#                        print loops, reduces, conflicts
                        return last_symbol[1]

            # Next token
            if data_idx == len(data):
                token = EOI
            else:
                char = data[data_idx]
                n = ord(char)
                token = lexical_table[n]
                if token is None:
                    msg = 'lexical error, unexpected character "%s"'
                    raise ValueError, msg % char

            # Find handles
            shift, handles = reduce_table[state]

#            aux = 0
            # Reduce
            for name, n, look_ahead, method in handles:
                # LR(1): reduce only if next token in look-ahead
                if token not in look_ahead:
                    continue
#                aux += 1
                # Fork the stack
                if n == 0:
                    alt_stack = stack[:]
                    values = []
                else:
                    values = [ stack[x][1] for x in range(-n, 0, 2)
                               if isinstance(stack[x], tuple) ]
                    alt_stack = stack[:-n]
                # Callback (the semantic level)
                last_state, last_state_start = alt_stack[-1]
                if context is None:
                    value = None
                elif method is None:
                    value = values
                else:
                    value = method(context, last_state_start, data_idx,
                                   *values)
                # Reduce
                alt_stack.append((name, value))
                next_state = symbol_table.get((last_state, name), 0)
                alt_stack.append((next_state, data_idx))
                paths.append((alt_stack, data_idx))

#            reduces += aux
#            if shift and aux or aux > 1:
#                conflicts += 1

            # Shift
            if shift:
                if token != EOI:
                    data_idx += 1
                stack.append(token)
                state = token_table.get((state, token), 0)
                stack.append((state, data_idx))
                paths.append((stack, data_idx))

        raise ValueError, 'grammar error'


    def is_valid(self, start_symbol, data):
        try:
            self.run(start_symbol, data)
        except ValueError:
            return False

        return True