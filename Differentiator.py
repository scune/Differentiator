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

def ParseBracketsAsSuffix(term_str : str):
    open_brackets = [ "(", "{", "[" ]
    closing_brackets = [ ")", "}", "]" ]

    for i, closing_bracket in enumerate(closing_brackets):
        if term_str.endswith(closing_bracket):
            open_bracket_idx = term_str.find(open_brackets[i])
            bracket_term_str = term_str[open_bracket_idx+1:-2]
            return bracket_term_str
    
    return ""

def IsInBrackets(term_str : str, idx : int):
    bracket_count = term_str.count(")", 0, idx)
    bracket_count += term_str.count("}", 0, idx)
    bracket_count += term_str.count("]", 0, idx)
    return (bracket_count % 2 == 1)

def ParseFunctionParameterAsStr(term_str : str):
    if term_str.startswith("ln"):
        bracket_term = ParseBracketsAsPrefix(term_str[len("ln")-1:])
        if len(bracket_term) > 0:
            return term_str[0:bracket_term]
    elif term_str.startswith("e^"):

    elif term_str.startswith("x"):
    

    numeric_substr = ''.join(takewhile(str.isdigit, term_str))
    if len(numeric_substr) > 0:


def Parse

def FindNextToken(term_str : str, token : str):
    idx = 0
    while idx < len(term_str) and idx != -1:
        idx = term_str.find(token, idx)
        if not IsInBrackets(term_str, idx):
            return idx
        idx += 1

    return -1

def ParseTerm(term_str : str, tokens, func = BaseFunction("", "")):
    add_idx = FindNextToken(term_str, "+")
    if add_idx != -1:
        func = Addition(term_str[0:add_idx], term_str[0:add_idx+1])
        func.a = ParseTerm(func.a)
        func.b = ParseTerm(func.b)
        return func

    mul_idx = FindNextToken(term_str, "*")
    if mul_idx != -1:
        func = Multiplication(term_str[0:mul_idx], term_str[0:mul_idx+1])
        func.a = ParseTerm(func.a)
        func.b = ParseTerm(func.b)
        return func
    
    # Functions
    pot_idx = FindNextToken(term_str, "^")
    if pot_idx != -1:
        b_idx = pot_idx + len("^")
        bracket_term_b = ParseBracketsAsPrefix(term_str[b_idx:])
        if len(bracket_term_b) == 0:
            bracket_term_b = ParseFunctionParameterAsStr(term_str[b_idx:])
        
        if pot_idx != 0:
            a_idx = pot_idx - 1
            bracket_term_a = ParseBracketsAsSuffix(term_str[0:a_idx])

             # TODO: Must either be function, constant or variable but not e^ or ^
            if len(bracket_term_a) > 0:
                func = Potentiation(bracket_term_a, bracket_term_b)
            elif term_str[a_idx] == "e":
                func = Exponential(bracket_term_b)
            elif term_str[a_idx] == "x":
                func = Potentiation(Variable(), bracket_term_b)


            func = Multiplication(term_str[0:expo_idx], func)
            func.a = ParseTerm(func.a)
        func.a = ParseTerm(func.a)


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