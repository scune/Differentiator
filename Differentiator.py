import sys
from itertools import takewhile

def Usage():
    print("Accepted functions: ln(a), a^b, e^a, a+b, a*b, a, x(var)")
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

def ParseConstantPrefix(term_str : str):
    numeric_substr = ''.join(takewhile(str.isdigit, term_str))
    return float(numeric_substr)

def ParseConstantSuffix(term_str : str):
    numeric_substr_len = 0
    for i in range(len(term_str)-1, -1, -1):
        if not term_str[i].isdigit():
            break
        numeric_substr_len += 1
    
    if numeric_substr_len > 0:
        return ParseConstantPrefix(term_str[len(term_str)-numeric_substr_len-1:])
    return ""

def IsInBrackets(term_str : str, idx : int):
    bracket_count = term_str.count(")", 0, idx)
    bracket_count += term_str.count("}", 0, idx)
    bracket_count += term_str.count("]", 0, idx)
    return (bracket_count % 2 == 1)

def FindNextToken(term_str : str, token : str):
    idx = 0
    while idx < len(term_str) and idx != -1:
        idx = term_str.find(token, idx)
        if not IsInBrackets(term_str, idx):
            return idx
        idx += 1
    return -1

def ParseTerm(term_str : str):
    func = BaseFunction("", "")
    if len(term_str) == 0:
        return func

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
        
        if pot_idx == 0:
            raise Exception("No potentiation base!")
        
        a_idx = pot_idx - 1
        bracket_term_a = ParseBracketsAsSuffix(term_str[0:a_idx])

        if len(bracket_term_a) > 0:
            func = Potentiation(bracket_term_a, bracket_term_b)
            func.a = ParseTerm(func.a)
            func.b = ParseTerm(func.b)
        elif term_str[a_idx] == "e":
            func = Exponential(bracket_term_b)
            func.a = ParseTerm(func.a)
        elif term_str[a_idx] == "x":
            func = Potentiation(Variable(), bracket_term_b)
            func.b = ParseTerm(func.b)
        else:
            numeric_suffix = ParseConstantSuffix(term_str)
            if numeric_suffix == 0:
                raise Exception("Invalid potentiation base!")
            
            func = Potentiation(Constant(numeric_suffix), bracket_term_b)
            func.b = ParseTerm(func.b)
        # TODO parse functions not in a bracket but still under ^, wie ParseNextToken nur als suffix  
        return func
        
    return ParseNextToken(term_str)

def IsBracket(c : str):
    open_brackets = ("(", "{", "[")
    return c.startswith(open_brackets)

def FindClosingBracket(term_str : str):
    open_brackets = ("(", "{", "[")
    closing_brackets = (")", "}", "]")
    open_bracket_count = 0
    closing_bracket_count = 0
    for i in range(0, len(term_str)):
        if term_str[i].startswith(open_brackets):
            open_bracket_count += 1
        elif term_str[i].startswith(closing_brackets):
            closing_bracket_count += 1
            if open_bracket_count == closing_bracket_count:
                return i
    return -1

def FindOpenBracket(term_str : str):
    open_brackets = ("(", "{", "[")
    closing_brackets = (")", "}", "]")
    open_bracket_count = 0
    closing_bracket_count = 0
    for i in range(len(term_str)-1, -1, -1):
        if term_str[i].startswith(open_brackets):
            open_bracket_count += 1
            if open_bracket_count == closing_bracket_count:
                return i
        elif term_str[i].startswith(closing_brackets):
            closing_bracket_count += 1
    return -1

def PrevTokenLen(term_str : str, closing_brackets : tuple, func_strs : list):
    if term_str.endswith(closing_brackets): # Left token is function
        open_bracket_idx = FindOpenBracket(term_str)

        if open_bracket_idx == -1:
            raise Exception("No suitable open bracket found!")
            
        for func_str in func_strs: # Find function and offset by it's length
            if term_str[:open_bracket_idx].endswith(func_str):
                return open_bracket_idx-len(func_str)

        return open_bracket_idx
    elif term_str.endswith("x") or term_str.endswith("e"):
        return len(term_str)-1
    elif term_str[-1].isdigit():
        new_open_bracket_idx = len(term_str)-1
        for i in range(len(term_str)-2, -1, -1):
            if not term_str[i].isdigit():
                break
            new_open_bracket_idx = i
        return new_open_bracket_idx
    
    raise Exception("No suitable token found before potentiation!", term_str)

def NextTokenLen(term_str : str, open_brackets : tuple, func_strs : list):
    if term_str.startswith(open_brackets):
        closing_bracket_idx = FindClosingBracket(term_str)
        if closing_bracket_idx == -1:
            raise Exception("No suitable closing bracket found!")
        
        return closing_bracket_idx
    elif term_str.startswith("x") or term_str.startswith("x"):
        return 1
    elif term_str[0].isdigit():
        return len(''.join(takewhile(str.isdigit, term_str)))
    
    for func_str in func_strs: # Find function and offset by it's length
        if term_str.startswith(func_str):
            closing_bracket_idx = FindClosingBracket(term_str[len(func_str)+1:])
            if closing_bracket_idx == -1:
                raise Exception("No suitable closing bracket found!")
            
            return len(func_str) + 1 + closing_bracket_idx
    
    raise Exception("No suitable token found before potentiation!", term_str)

def IsMultiplicationApplicable(term_str : str, func_strs : list, open_brackets : tuple):
    if term_str.startswith("x"):
        return True
    if term_str.startswith("e"):
        return True
    if term_str[0].isdigit():
        return True
    if term_str.startswith(tuple(func_strs)):
        return True
    if term_str.startswith(open_brackets):
        return True
    return False

def InsertImplicitTokens(term_str : str, func_strs : list):
    # Implicit function parentheses
    for i in range(len(term_str)-1, 0, -1):
        for func_str in func_strs:
            param_idx = i-2+len(func_str)

            if term_str[:i].endswith(func_str) and not IsBracket(term_str[param_idx]):
                term_str = term_str[:param_idx] + "(" + term_str[param_idx:]
                param_idx += 1

                closing_bracket_idx = -1
                if term_str[param_idx] == "x":
                    closing_bracket_idx = param_idx+1
                elif term_str[param_idx].isdigit():
                    numeric_substr_len = 1 + len(''.join(takewhile(str.isdigit, term_str[param_idx+1:])))
                    closing_bracket_idx = param_idx+numeric_substr_len
                elif term_str[param_idx:].startswith(tuple(func_strs)):
                    closing_bracket_idx = 1 + param_idx + FindClosingBracket(term_str[param_idx:])
                else:
                    raise Exception("No suitable token found after function!", term_str[param_idx:])

                term_str = term_str[:closing_bracket_idx] + ")" + term_str[closing_bracket_idx:]

    # Implicit potentiation parentheses
    open_brackets = ("(", "{", "[")
    closing_brackets = (")", "}", "]")

    pot_offset = 0
    pot_idx = term_str.find("^")
    while pot_idx != -1:
        pot_offset = pot_idx+1

        # Brackets around a
        new_open_bracket_idx = PrevTokenLen(term_str[:pot_idx], closing_brackets, func_strs)
        if term_str[new_open_bracket_idx] != "(":
            term_str = term_str[:pot_idx] + ")" + term_str[pot_idx:]
            term_str = term_str[:new_open_bracket_idx] + "(" + term_str[new_open_bracket_idx:]
            pot_offset += 2

        term_str = term_str[:new_open_bracket_idx] + "(" + term_str[new_open_bracket_idx:]
        pot_offset += 1

        # Brackets around a^b
        closing_bracket_ab_idx = pot_offset + NextTokenLen(term_str[pot_offset:], open_brackets, func_strs)

        term_str = term_str[:closing_bracket_ab_idx] + ")" + term_str[closing_bracket_ab_idx:]

        if term_str[pot_offset] != "(":
            term_str = term_str[:closing_bracket_ab_idx] + ")" + term_str[closing_bracket_ab_idx:]
            term_str = term_str[:pot_offset] + "(" + term_str[pot_offset:]
            pot_offset += 2
        
        pot_offset += 1

        pot_idx = term_str.find("^", pot_offset)

    print(term_str)
    
    # Implicit multiplication
    for i in range(0, len(term_str)-1):
        mul_idx = -1

        if term_str[i] == "x" or term_str[i].startswith(closing_brackets):
            if IsMultiplicationApplicable(term_str[i+1:], func_strs, open_brackets):
                mul_idx = i+1
        elif term_str[i].isdigit():
            numeric_substr_len = 1 + len(''.join(takewhile(str.isdigit, term_str[i+1:])))
            if IsMultiplicationApplicable(term_str[i+numeric_substr_len:], func_strs, open_brackets):
                mul_idx = i+numeric_substr_len
        
        if mul_idx != -1:
            term_str = term_str[:mul_idx] + "*" + term_str[mul_idx:]
            
    return term_str

def ParseArgs():
    if len(sys.argv) <= 1 or sys.argv[1] == "--help":
        Usage()

    term_str = sys.argv[1]

    # Remove spaces
    term_str = term_str.replace(" ", "")

    func_strs = ["ln"]

    try:
        term_str = InsertImplicitTokens(term_str, func_strs)
        print("Parsed res:", term_str)
    except Exception as exc:
        print("Error while parsing implicit tokens:", exc)
        exit(-1)

    try:
        return ParseTerm(term_str)
    except Exception as exc:
        print("Error while parsing to internal functions:", exc)
        exit(-1)

    exit(0)

term = ParseArgs()

print("Parsed term:", term.String())

term = term.Simplify()
print("Simplified:", term.String())

print("d/dx[", term.String(), "] =")
term = term.Derivative()
print(term.String())

term = term.Simplify()
print("Simplified:", term.String())