import sys
from itertools import takewhile

def Usage():
    print("Accepted functions: ln(a), sqrt(a), a^b, e^a, a+b, a*b, a, x(var)")
    exit() 

class BaseFunction:
    def __init__(self, a, b):
        self.a = a
        self.b = b

class Constant(BaseFunction): # a
    def __init__(self, a):
        super().__init__(a, 0)
    
    def Derivative(self):
        return self
    
    def __mul__(self, other):
        if type(other) == Constant:
            new_a = self.a * other.a
            return Constant(new_a)        
        else:
            print("Constant mul with", type(other), "!!!!!!!!!!!!!!!!")
        
    def __add__(self, other):
        if type(other) == Constant:
            new_a = self.a + other.a
            return Constant(new_a)
        else:
            print("Constant added with", type(other), "!!!!!!!!!!!!!!!!")
    
    def __eq__(self, other):
        if type(other) is Constant:
            return self.a == other.a
        return False

    def String(self):
        return self.a
    
    def Simplify(self):
        return self
    
    def Token():
        return ""

class Variable(BaseFunction): # x
    def __init__(self):
        super().__init__(0, 0)
    
    def Derivative(self):
        return Constant(1)
    
    def __mul__(self, other):
        if type(other) is Variable:
            return Potentiation(self, Constant(2))
        return Multiplication(self, other)
        
    def __add__(self, other):
        if type(other) is Variable:
            return Multiplication(self, Constant(2))
        return Addition(self, other)
    
    def __eq__(self, other):
        return type(other) is Variable

    def String(self):
        return "x"
    
    def Simplify(self):
        return self

    def Token():
        return "x"

class Addition(BaseFunction): # a+b
    def __init__(self, a, b):
        super().__init__(a, b)
    
    def Derivative(self):
        return Addition(self.a.Derivative(), self.b.Derivative())

    def __mul__(self, other):
        self.a *= other
        self.b *= other
        return self
    
    def __add__(self, other):
        self.a += other
        return self
    
    def String(self):
        return ("{} + {}").format(self.a.String(), self.b.String())
    
    def Simplify(self):
        self.a = self.a.Simplify()
        self.b = self.b.Simplify()
        if type(self.a) is Constant and type(self.b) is Constant:
            return self.a + self.b

        return self

    def Token():
        return "+"

class Multiplication(BaseFunction): # a*b
    def __init__(self, a, b):
        super().__init__(a, b)

    def Derivative(self):
        old_a = self.a
        old_b = self.b
        a_diff = old_a.Derivative()
        b_diff = old_b.Derivative()
        if type(self.a) is Constant or type(self.b) is Constant:
            return Multiplication(a_diff, b_diff)
        if type(self.a) is Variable or type(self.b) is Variable:
            return Multiplication(a_diff, b_diff)
        
        return Addition(Multiplication(a_diff, old_b),
                        Multiplication(old_a, b_diff))

    def __mul__(self, other):
        if type(other) is Multiplication:
            self.a *= other
            return self
        return Multiplication(self, other)
    
    def __add__(self, other):
        return Addition(self, other)
    
    def String(self):
        return ("{} * {}").format(self.a.String(), self.b.String())
    
    def Simplify(self):
        self.a = self.a.Simplify()
        self.b = self.b.Simplify()

        if type(self.a) is Constant and type(self.b) is Constant:
            return self.a * self.b
        
        elif type(self.a) is Potentiation and type(self.b) is Potentiation:
            if self.a.a == self.b.a:
                self.a = Potentiation(self.a.a, Addition(self.a.b, self.b.b))
                return self.a.Simplify()
            
        elif type(self.a) is Exponential and type(self.b) is Exponential:
            self.a.a += self.b.a
            return self.a.Simplify()
        
        elif type(self.a) is Potentiation:
            if type(self.a.a) is type(self.b):
                if self.a.a == self.b:
                    self.a.b = Addition(self.a.b, Constant(1))
                    return self.a.Simplify()

        elif type(self.b) is Potentiation:
            if type(self.b.a) is type(self.a):
                if self.b.a == self.a:
                    self.b.b = Addition(self.b.b, Constant(1))
                    return self.b.Simplify()
            
        if type(self.a) is Constant:
            if self.a == Constant(0):
                return Constant(0)
            elif self.a == Constant(1):
                return self.b
            
        if type(self.b) is Constant:
            if self.b == Constant(0):
                return Constant(0)
            elif self.b == Constant(1):
                return self.a
            
        return self
    
    def Token():
        return "*"

class Potentiation(BaseFunction): # a^b
    def __init__(self, a, b):
        super().__init__(a, b)

    def Derivative(self):
        old_b = self.b
        new_b = old_b + Constant(-1)
        if new_b == Constant(0) or self.a == Constant(1):
            return Constant(1)
        elif self.a == Constant(0):
            return Constant(0)
        old_a = self.a
        return Multiplication(old_b, Multiplication(Potentiation(self.a, new_b), old_a.Derivative()))

    def __mul__(self, other):
        if type(other) is Potentiation:
            if self.a == other.a:
                self.b += other.b
                return self
        return Multiplication(self, other)
    
    def __add__(self, other):
        return Addition(self, other)
    
    def String(self):
        return ("{}^({})").format(self.a.String(), self.b.String())
    
    def Simplify(self):
        self.a = self.a.Simplify()
        if type(self.a) is Constant:
            if self.a == Constant(0):
                return Constant(0)
            if self.a == Constant(1):
                return Constant(1)
        
        self.b = self.b.Simplify()
        if type(self.b) is Constant:
            if self.b == Constant(0):
                return Constant(1)
            if self.b == Constant(1):
                return self.b
        
        if type(self.a) is Potentiation and type(self.b) is Constant:
            self.a = Potentiation(self.a.a, Multiplication(self.a.b, self.b))
            return self.a.Simplify()
        
        return self
    
    def Token():
        return "^"

class NaturalLog(BaseFunction): # ln(a)
    def __init__(self, a):
        super().__init__(a, 0)
        
    def Derivative(self):
        new_a = self.a
        new_a = new_a.Derivative()
        return Multiplication(Potentiation(self.a, Constant(-1)), new_a)
    
    def __mul__(self, other):
        return Multiplication(self, other)
    
    def __add__(self, other):
        return Addition(self, other)
    
    def String(self):
        return ("ln({})").format(self.a.String())
    
    def Simplify(self):
        self.a = self.a.Simplify()
        if self.a == Constant(1):
            return Constant(0)
        if type(self.a) is Exponential:
            return self.a.a
        
        return self
    
    def Token():
        return "ln"
    
class Exponential(BaseFunction): # e^a
    def __init__(self, a):
        super().__init__(a, 0)

    def Derivative(self):
        if type(self.a) is Constant or type(self.a) is Variable:
            return self
        new_a = self.a.Derivative()
        return Multiplication(new_a, self)
    
    def __mul__(self, other):
        if type(other) is Exponential:
            return Exponential(self.a + other.a)
        return Multiplication(self, other)
    
    def __add__(self, other):
        return Addition(self, other)
    
    def String(self):
        return ("e^({})").format(self.a.String())
    
    def Simplify(self):
        self.a = self.a.Simplify()
        if self.a == Constant(0):
            return Constant(1)
        if type(self.a) is NaturalLog:
            return self.a.a
        
        return self
    
    def Token():
        return "e^"

def ParseBracketsAsPrefix(term_str : str):
    open_brackets = [ "(", "{", "[" ]
    closing_brackets = [ ")", "}", "]" ]

    for i, open_bracket in enumerate(open_brackets):
        if term_str.startswith(open_bracket):
            closing_bracket_idx = term_str.find(closing_brackets[i])
            bracket_term_str = term_str[1:closing_bracket_idx]
            return bracket_term_str
    
    return ""

def ParseTermPrefix(term_str : str, tokens, token_funcs, b_only_potentiation = False):
    numeric_substr = ''.join(takewhile(str.isdigit, term_str))
    if len(numeric_substr) > 0: # If numberic prefix

        if b_only_potentiation:
            return [term_str, BaseFunction(0, 0)]

        term_str = term_str.removeprefix(numeric_substr)
        return [term_str, Constant(float(numeric_substr))]
    
    bracket_term_str = ParseBracketsAsPrefix(term_str)
    if len(bracket_term_str) > 0: # Brackets

        if b_only_potentiation:
            return [term_str, BaseFunction(0, 0)]

        term_str = term_str[len(bracket_term_str) + 2:]

        # Parse bracket term
        [_, a] = ParseTermPrefix(bracket_term_str, tokens, token_funcs)

        # Check what's after the bracket
        [term_str, b] = ParseTermPrefix(term_str, tokens, token_funcs)
        if type(b) is BaseFunction:
            return  [term_str, a]
        elif type(b) is Potentiation:
            return [term_str, Potentiation(a, b)]
        elif type(b) is Addition:
            return [term_str, Addition(a, b)]
        else:
            return [term_str, Multiplication(a, b)]

    for i, token in enumerate(tokens):
        if term_str.startswith(token):

            if b_only_potentiation and not (token_funcs[i] is Potentiation):
                return [term_str, BaseFunction(0, 0)]
                
            term_str = term_str.removeprefix(token)

            # Get next func to check later if it is a potentiation
            term_str_old = term_str
            [next_term_str, next_func] = ParseTermPrefix(term_str, tokens, token_funcs, True)

            parsed_func = BaseFunction(0, 0)

            if token_funcs[i] is Exponential:
                bracket_term_str = ParseBracketsAsPrefix(term_str)
                if len(bracket_term_str) > 0: # Brackets
                    term_str = term_str[len(bracket_term_str) + 2:]

                    [_, a] = ParseTermPrefix(bracket_term_str, tokens, token_funcs)
                    parsed_func = Exponential(a)
                else: # No brackets
                    [term_str, a] = ParseTermPrefix(term_str, tokens, token_funcs)
                    parsed_func = Exponential(a)

            elif token_funcs[i] is Potentiation:
                bracket_term_str = ParseBracketsAsPrefix(term_str)
                if len(bracket_term_str) > 0: # Brackets
                    term_str = term_str[len(bracket_term_str) + 2:]

                    [_, b] = ParseTermPrefix(bracket_term_str, tokens, token_funcs)
                    parsed_func = Potentiation(0, b)
                else: # No brackets
                    [term_str, b] = ParseTermPrefix(term_str, tokens, token_funcs)
                    parsed_func = Potentiation(0, b)
            
            elif token_funcs[i] is NaturalLog:
                bracket_term_str = ParseBracketsAsPrefix(term_str)
                if len(bracket_term_str) > 0: # Brackets
                    term_str = term_str[len(bracket_term_str) + 2:]

                    [_, a] = ParseTermPrefix(bracket_term_str, tokens, token_funcs)
                    parsed_func = NaturalLog(a)
                else: # No brackets
                    [term_str, a] = ParseTermPrefix(term_str, tokens, token_funcs)
                    parsed_func = NaturalLog(a)
                
            elif token_funcs[i] is Variable:
                parsed_func = Variable()
            
            elif token_funcs[i] is Addition:
                [term_str, b] = ParseTermPrefix(term_str, tokens, token_funcs)
                parsed_func = Addition(0, b)
            
            elif token_funcs[i] is Multiplication:
                [term_str, b] = ParseTermPrefix(term_str, tokens, token_funcs)
                parsed_func = Multiplication(0, b)

            if type(next_func) is Potentiation:
                next_func.a = parsed_func
                parsed_func = next_func

                term_str = next_term_str

            return [term_str, parsed_func]
    
    return [term_str, BaseFunction(0, 0)]

def GlueFunctions(parsed_funcs : list):
    for i in range(len(parsed_funcs) - 1, 0, -1):
        func = parsed_funcs[i]
        if type(func) is Potentiation:
            if isinstance(func.a, int):
                prev_func = parsed_funcs.pop(i - 1)
                parsed_funcs[i - 1] = Potentiation(prev_func, func.b)

    for i in range(len(parsed_funcs) - 1, 0, -1):
        func = parsed_funcs[i]
        if type(func) is Multiplication:
            if isinstance(func.a, int):
                prev_func = parsed_funcs.pop(i - 1)
                parsed_funcs[i - 1] = Multiplication(prev_func, func.b)

    for i in range(len(parsed_funcs) - 1, 0, -1):
        func = parsed_funcs[i]
        if type(func) is Addition:
            if isinstance(func.a, int):
                prev_func = parsed_funcs.pop(i - 1)
                parsed_funcs[i - 1] = Addition(prev_func, func.b)

    while len(parsed_funcs) > 1:
        # Concatenate functions with implicit multiplication
        next_func = parsed_funcs.pop(1)
        parsed_funcs[0] = Multiplication(parsed_funcs[0], next_func)

    return parsed_funcs[0]

def ParseArgs():
    if len(sys.argv) <= 1 or sys.argv[1] == "--help":
        Usage()

    term_str = sys.argv[1]

    # Remove spaces
    term_str = term_str.replace(" ", "")

    # Get static function tokens
    tokens = []
    token_funcs = []
    for function in BaseFunction.__subclasses__():
        if function.Token() == "":
            continue
        tokens.append(function.Token())
        token_funcs.append(function)

    # Parse functions from term string
    parsed_funcs = []
    while len(term_str) > 0:
        [term_str, func] = ParseTermPrefix(term_str, tokens, token_funcs)
        if func is BaseFunction:
            break
        parsed_funcs.append(func)

    return GlueFunctions(parsed_funcs)

term = ParseArgs()

print("Parsed term:", term.String())
# TODO: Fix mul. and add. order:
# First, parse additions and put the a, b string terms from a+b in the addition class like: Addition(a, b)
# Second, parse multiplication stored inside the addition class a, b string terms
# Third, parse functions and parentheses, ln(x), e^x, (), etc. and if the functions x parameter is itself a function, then
# recursively call the whole parsing function

term = term.Simplify()
print("Simplified:", term.String())

print("d/dx[", term.String(), "] =")
term = term.Derivative()
print(term.String())

term = term.Simplify()
print("Simplified:", term.String())