import sys
from itertools import takewhile
from sortedcontainers import SortedSet
import matplotlib.pyplot as plt
import numpy as np

open_brackets = ("(", "{", "[")
closing_brackets = (")", "}", "]")
func_strs = ["ln", "sqrt", "sin", "cos", "tan"]
interval = [float(-10), float(10)]
y_cutoff = [float(-10), float(10)]

def Usage():
    print("Usage:")
    print("Accepted functions: a^b, e^a, a+b, a*b, a/b,", ", ".join(f'{s}' for s in func_strs) + ".")
    print("Accepted bracket types:", ", ".join(f'{s0}{s1}' for s0,s1 in zip(open_brackets,closing_brackets)) + ".")
    print("Optional function domain interval [a, b] specification for plotting via -a{Float} and -b{Float}")
    print("and the same for the y cutoff with -ya{Float} and -yb{Float}, where a < b applies for both.")
    exit() 

def IsNumeric(string : str):
    try:
        float(string)
        return True
    except ValueError:
        return False

class BaseFunction:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def GetChildren(self):
        return []

class Constant(BaseFunction): # a
    def __init__(self, a):
        super().__init__(a, 0)
    
    def Derivative(self):
        return self
    
    def __mul__(self, other):
        if type(other) is Constant:
            new_a = self.a * other.a
            return Constant(new_a)
        return Multiplication(self, other)
        
    def __add__(self, other):
        if type(other) is Constant:
            new_a = self.a + other.a
            return Constant(new_a)
        return Addition(self, other)
    
    def __eq__(self, other):
        if type(other) is Constant:
            return self.a == other.a
        return False

    def String(self):
        if int(self.a) == self.a:
            return str(int(self.a))
        return str(self.a)
    
    def Simplify(self):
        return self

    def Plot(self, x):
        return self.a
    
    def Contains(self, other):
        return type(other) is type(self)

class EulerConstant(Constant):
    def __init__(self):
        super().__init__(np.e)

    def Derivative(self):
        return self

    def __mul__(self, other):
        if type(other) is EulerConstant:
            return Potentiation(EulerConstant(), Constant(2))
        return Multiplication(self, other)
        
    def __add__(self, other):
        if type(other) is EulerConstant:
            return Multiplication(EulerConstant(), Constant(2))
        return Addition(self, other)
    
    def __eq__(self, other):
        return type(other) is EulerConstant

    def String(self):
        return "e"
    
    def Plot(self, x):
        return np.e
    
    def Contains(self, other):
        return type(other) is type(self)
    
class Pi(Constant):
    def __init__(self):
        super().__init__(np.pi)

    def __mul__(self, other):
        if type(other) is Pi:
            return Potentiation(Pi(), Constant(2))
        return Multiplication(self, other)
        
    def __add__(self, other):
        if type(other) is Pi:
            return Multiplication(Pi(), Constant(2))
        return Addition(self, other)
    
    def __eq__(self, other):
        return type(other) is Pi

    def String(self):
        return "pi"
    
    def Plot(self, x):
        return np.pi
    
    def Contains(self, other):
        return type(other) is type(self)

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
    
    def Plot(self, x):
        return x
    
    def Contains(self, other):
        return type(other) is type(self)

class Addition(BaseFunction): # a+b
    def __init__(self, a, b):
        super().__init__(a, b)
    
    def Derivative(self):
        if not self.a.Contains(Variable()) and not self.b.Contains(Variable()):
            return Constant(0)

        if not self.a.Contains(Variable()):
            return self.b.Derivative()
        if not self.b.Contains(Variable()):
            return self.a.Derivative()
        
        return Addition(self.a.Derivative(), self.b.Derivative())

    def __mul__(self, other):
        self.a *= other
        self.b *= other
        return self
    
    def __add__(self, other):
        self.a += other
        return self

    def __eq__(self, other):
        if type(other) is Addition:
            if self.a == other.a and self.b == other.b:
                return True
            elif self.a == other.b and self.b == other.a:
                return True
        return False

    def String(self):
        return "({} + {})".format(self.a.String(), self.b.String())
    
    def Simplify(self):
        self.a = self.a.Simplify()
        self.b = self.b.Simplify()

        if isinstance(self.a, Constant) and isinstance(self.b, Constant):
            return self.a + self.b

        sin_2 = Potentiation(Sin(Variable()), Constant(2))
        cos_2 = Potentiation(Cos(Variable()), Constant(2))
        for first, second in [(self.a, self.b), (self.b, self.a)]:
            if first == sin_2 and second == cos_2:
                return Constant(1)
        
        if type(self.a) is Multiplication and type(self.b) is Multiplication:
            for first, second in [(self.a, self.b), (self.b, self.a)]:
                if first.a == second.a:
                    return Multiplication(first.a, Addition(first.b, second.b))
                elif first.a == second.b:
                    return Multiplication(first.a, Addition(first.b, second.a))

        return self
    
    def Plot(self, x):
        return self.a.Plot(x) + self.b.Plot(x)
    
    def Contains(self, other):
        return self.a.Contains(other) or self.b.Contains(other)
    
    def GetChildren(self):
        return [self.a, self.b]

class Multiplication(BaseFunction): # a*b
    def __init__(self, a, b):
        super().__init__(a, b)

    def Derivative(self):
        if not self.a.Contains(Variable()) and not self.b.Contains(Variable()):
            return self
        
        for first, second in [(self.a, self.b), (self.b, self.a)]:
            if not first.Contains(Variable()):
                return Multiplication(first, second.Derivative())

        return Addition(
            Multiplication(self.a.Derivative(), self.b),
            Multiplication(self.a, self.b.Derivative())
        )

    def __mul__(self, other):
        if type(other) is Multiplication:
            self.a *= other
            return self
        return Multiplication(self, other)
    
    def __add__(self, other):
        return Addition(self, other)
    
    def __eq__(self, other):
        if type(other) is Multiplication:
            if self.a == other.a and self.b == other.b:
                return True
            elif self.a == other.b and self.b == other.a:
                return True
        return False

    def String(self):
        if type(self.b) is Potentiation and self.b.b == Constant(-1):
            return "{}/{}".format(self.a.String(), self.b.a.String())
        
        #if self.a == Constant(-1):
        #    return "-{}".format(self.b.String())
        #if self.b == Constant(-1):
        #    return "-{}".format(self.a.String())
        
        return "{} * {}".format(self.a.String(), self.b.String())
    
    def Simplify(self):
        self.a = self.a.Simplify()
        self.b = self.b.Simplify()

        if type(self.a) is Constant and type(self.b) is Constant:
            return self.a * self.b
        
        for first, second in [(self.a, self.b), (self.b, self.a)]:
            if type(first) is Potentiation and type(second) is Potentiation: # a^b * a^c
                if first.a == second.a:
                    first = Potentiation(first.a, Addition(first.b, second.b))
                    return first.Simplify()
            
            if type(first) is Potentiation: # a^b * a
                if first.a == second:
                    first.b = Addition(first.b, Constant(1))
                    return first.Simplify()
            
            if type(first) is Potentiation and type(second) is Constant: # 1/c * a
                if first.b == Constant(-1) and type(first.a) is Constant:
                    if int(first.a.a) == first.a.a and int(second.a) == second.a:
                        denom = np.gcd(int(second.a), int(first.a.a))
                        second.a /= denom
                        first.a.a /= denom
 
            if type(first) is Constant:
                if first == Constant(0):
                    return Constant(0)
                elif first == Constant(1):
                    return second
            
            if type(first) is Sin:
                if second == Potentiation(Cos(first.a), Constant(-1)):
                    return Tan(first.a)
            if type(first) is Cos:
                if second == Potentiation(Sin(first.a), Constant(-1)):
                    return Potentiation(Tan(first.a), Constant(-1))
            
            if first == Potentiation(second, Constant(-1)):
                return Constant(1)
            
        return self
    
    def Plot(self, x):
        return self.a.Plot(x) * self.b.Plot(x)
    
    def Contains(self, other):
        return self.a.Contains(other) or self.b.Contains(other)

    def GetChildren(self):
        return [self.a, self.b]

class Potentiation(BaseFunction): # a^b
    def __init__(self, a, b):
        super().__init__(a, b)

    def Derivative(self):
        if type(self.a) is not EulerConstant:
            if self.b.Contains(Variable()):
                new_func = Potentiation(EulerConstant(), Multiplication(self.b, NaturalLog(self.a)))
                return new_func.Derivative()

        if not self.a.Contains(Variable()) and not self.b.Contains(Variable()):
            return self

        if isinstance(self.b, Constant):
            old_b = self.b
            new_b = old_b + Constant(-1)
            return Multiplication(self.b, Potentiation(self.a, new_b))
        
        return Multiplication(self, self.b.Derivative())

    def __mul__(self, other):
        if type(other) is Potentiation:
            if self.a == other.a:
                self.b += other.b
                return self
        return Multiplication(self, other)
    
    def __add__(self, other):
        return Addition(self, other)
    
    def __eq__(self, other):
        if type(other) is Potentiation:
            return self.a == other.a and self.b == other.b
        return False

    def String(self):
        if self.b == Constant(-1):
            return "1/({})".format(self.a.String())
        if self.b == Constant(0.5):
            return "sqrt({})".format(self.a.String())
        if self.b == Constant(-0.5):
            return "1/sqrt({})".format(self.a.String())
        return "({})^({})".format(self.a.String(), self.b.String())
    
    def Simplify(self):
        self.a = self.a.Simplify()
        self.b = self.b.Simplify()

        if type(self.a) is Constant and type(self.b) is Constant:
            c = Constant(self.a.a ** self.b.a)
            if int(c.a) == c.a:
                return c
        
        if type(self.a) is Constant:
            if self.a == Constant(0):
                return Constant(0)
            if self.a == Constant(1):
                return Constant(1)
        elif type(self.b) is Constant:
            if self.b == Constant(0):
                return Constant(1)
            if self.b == Constant(1):
                return self.a
        
        if type(self.a) is Potentiation and type(self.b) is Constant:
            self.a = Potentiation(self.a.a, Multiplication(self.a.b, self.b))
            return self.a.Simplify()
        
        if self.a == EulerConstant():
            if type(self.b) is NaturalLog:
                return self.b.a
            if type(self.b) is Multiplication:
                if type(self.b.a) is NaturalLog:
                    return Potentiation(self.b.b, self.b.a.a)
                if type(self.b.b) is NaturalLog:
                    return Potentiation(self.b.a, self.b.b.a)
        
        return self

    def Plot(self, x):
        with np.errstate(invalid='ignore'):
            return np.pow(self.a.Plot(x), self.b.Plot(x))

    def Contains(self, other):
        return self.a.Contains(other) or self.b.Contains(other)

    def GetChildren(self):
        return [self.a, self.b]

class NaturalLog(BaseFunction): # ln(a)
    def __init__(self, a):
        super().__init__(a, 0)
        
    def Derivative(self):
        if not self.a.Contains(Variable()):
            return self

        new_a = self.a
        new_a = new_a.Derivative()
        return Multiplication(Potentiation(self.a, Constant(-1)), new_a)
    
    def __mul__(self, other):
        return Multiplication(self, other)
    
    def __add__(self, other):
        return Addition(self, other)

    def __eq__(self, other):
        if type(other) is NaturalLog:
            return self.a == other.a
        return False

    def String(self):
        return "ln({})".format(self.a.String())
    
    def Simplify(self):
        self.a = self.a.Simplify()
        if type(self.a) is Potentiation:
            if type(self.a.a) is EulerConstant:
                return self.a.b
    
        return self
    
    def Plot(self, x):
        return np.log(self.a.Plot(x))

    def Contains(self, other):
        return self.a.Contains(other)

    def GetChildren(self):
        return [self.a]

class Sin(BaseFunction): # sin(a)
    def __init__(self, a):
        super().__init__(a, 0)

    def Derivative(self):
        if not self.a.Contains(Variable()):
            return self

        a_diff = self.a.Derivative()
        return Multiplication(Cos(self.a), a_diff)
    
    def __mul__(self, other):
        return Multiplication(self, other)
    
    def __add__(self, other):
        return Addition(self, other)

    def __eq__(self, other):
        if type(other) is Sin:
            return self.a == other.a
        return False

    def String(self):
        return "sin({})".format(self.a.String())
    
    def Simplify(self):
        self.a = self.a.Simplify()
        #if isinstance(self.a, Constant) and self.a.a * 4 % np.pi == 0:
        #    return Constant(np.sin(self.a.a))
        return self

    def Plot(self, x):
        return np.sin(self.a.Plot(x))

    def Contains(self, other):
        return self.a.Contains(other)

    def GetChildren(self):
        return [self.a]
    
class Cos(BaseFunction): # cos(a)
    def __init__(self, a):
        super().__init__(a, 0)

    def Derivative(self):
        if not self.a.Contains(Variable()):
            return self

        a_diff = self.a.Derivative()
        return Multiplication(Sin(self.a), Multiplication(Constant(-1), a_diff))
    
    def __mul__(self, other):
        return Multiplication(self, other)
    
    def __add__(self, other):
        return Addition(self, other)

    def __eq__(self, other):
        if type(other) is Cos:
            return self.a == other.a
        return False

    def String(self):
        return "cos({})".format(self.a.String())
    
    def Simplify(self):
        self.a = self.a.Simplify()
        return self
    
    def Plot(self, x):
        return np.cos(self.a.Plot(x))

    def Contains(self, other):
        return self.a.Contains(other)

    def GetChildren(self):
        return [self.a]

class Tan(BaseFunction): # tan(a)
    def __init__(self, a):
        super().__init__(a, 0)

    def Derivative(self):
        if not self.a.Contains(Variable()):
            return self

        a_diff = self.a.Derivative()
        return Multiplication(Potentiation(Cos(self.a), Constant(-2)), a_diff)
    
    def __mul__(self, other):
        return Multiplication(self, other)
    
    def __add__(self, other):
        return Addition(self, other)

    def __eq__(self, other):
        if type(other) is Tan:
            return self.a == other.a
        return False

    def String(self):
        return "tan({})".format(self.a.String())
    
    def Simplify(self):
        self.a = self.a.Simplify()
        return self

    def Plot(self, x):
        return np.tan(self.a.Plot(x))

    def Contains(self, other):
        return self.a.Contains(other)

    def GetChildren(self):
        return [self.a]
    
def FindClosingBracket(term_str : str):
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

def IsInBrackets(term_str : str, idx):
    bracket_count = 0
    for open_bracket in open_brackets:
        bracket_count += term_str.count(open_bracket, 0, idx)
    for closing_bracket in closing_brackets:
        bracket_count -= term_str.count(closing_bracket, 0, idx)
    return bracket_count > 0

def FindNextToken(term_str : str, token : str):
    idx = 0
    while idx < len(term_str):
        idx = term_str.find(token, idx)
        if idx == -1:
            break

        if not IsInBrackets(term_str, idx):
            return idx
        idx += 1
    return -1

def ParseFunctionOneParam(term_str : str, func_name : str):
    idx = FindNextToken(term_str, func_name)
    if idx == -1:
        return ""
    
    a_idx = idx + len(func_name)
    bracket_a_idx = a_idx + FindClosingBracket(term_str[a_idx:])
    if bracket_a_idx == -1:
        raise Exception("No closing bracket found: " + term_str)
        
    bracket_term_a = term_str[a_idx+1:bracket_a_idx]
    if len(bracket_term_a) == 0:
        raise Exception("Empty brackets!", term_str)
        
    return bracket_term_a

def ParseTerm(term_str : str):
    #print("Curr term:", term_str)

    func = BaseFunction("", "")
    if len(term_str) == 0:
        raise Exception("Empty term!")

    if IsNumeric(term_str): # Constant
        return Constant(float(term_str))
    elif term_str == "x": # Variable
        return Variable()
    elif term_str == "e": # e
        return EulerConstant()
    elif term_str == "pi": # pi
        return Pi()

    # If whole term_str is brackets
    if term_str.startswith(open_brackets):
        if FindClosingBracket(term_str) == len(term_str)-1:
            return ParseTerm(term_str[1:-1])

    # Addition
    add_idx = FindNextToken(term_str, "+")
    if add_idx != -1:
        func = Addition(term_str[:add_idx], term_str[add_idx+1:])
        func.a = ParseTerm(func.a)
        func.b = ParseTerm(func.b)
        return func

    # Subtraction
    sub_idx = FindNextToken(term_str, "-")
    if sub_idx != -1:
        func = Multiplication(Constant(-1), term_str[sub_idx+1:])
        func.b = ParseTerm(func.b)
        if sub_idx > 0:
            func = Addition(term_str[:sub_idx], func)
            func.a = ParseTerm(func.a)
        return func

    # Multiplication
    mul_idx = FindNextToken(term_str, "*")
    if mul_idx != -1:
        func = Multiplication(term_str[:mul_idx], term_str[mul_idx+1:])
        func.a = ParseTerm(func.a)
        func.b = ParseTerm(func.b)
        return func

    # Division
    div_idx = FindNextToken(term_str, "/")
    if div_idx != -1:
        func = Multiplication(term_str[:div_idx], Potentiation(term_str[div_idx+1:], Constant(-1)))
        func.a = ParseTerm(func.a)
        func.b.a = ParseTerm(func.b.a)
        return func
    
    # Potentiation
    pot_idx = FindNextToken(term_str, "^")
    if pot_idx != -1:
        b_idx = pot_idx + len("^")
        bracket_b_idx = b_idx + FindClosingBracket(term_str[b_idx:])
        if bracket_b_idx == -1:
            raise Exception("Empty bracket after potantiation!", term_str[b_idx:])
        
        bracket_a_idx = FindOpenBracket(term_str[:pot_idx])
        if bracket_a_idx == -1:
            raise Exception("Empty bracket before potantiation!", term_str[:pot_idx])

        bracket_term_a = term_str[bracket_a_idx+1:pot_idx-1]
        bracket_term_b = term_str[b_idx+1:bracket_b_idx]
        if len(bracket_term_a) == 0 or len(bracket_term_b) == 0:
            raise Exception("Empty brackets at potantiation: " + term_str)

        func = Potentiation(bracket_term_a, bracket_term_b)
        func.a = ParseTerm(func.a)
        func.b = ParseTerm(func.b)
        return func
    
    # Ln
    ln_bracket_term = ParseFunctionOneParam(term_str, "ln")
    if len(ln_bracket_term) > 0:
        func = NaturalLog(ln_bracket_term)
        func.a = ParseTerm(func.a)
        return func
    
    # Sqrt
    sqrt_bracket_term = ParseFunctionOneParam(term_str, "sqrt")
    if len(sqrt_bracket_term) > 0:
        func = Potentiation(sqrt_bracket_term, Constant(0.5))
        func.a = ParseTerm(func.a)
        return func

    # Sin
    sin_bracket_term = ParseFunctionOneParam(term_str, "sin")
    if len(sin_bracket_term) > 0:
        func = Sin(sin_bracket_term)
        func.a = ParseTerm(func.a)
        return func

    # Cos
    cos_bracket_term = ParseFunctionOneParam(term_str, "cos")
    if len(cos_bracket_term) > 0:
        func = Cos(cos_bracket_term)
        func.a = ParseTerm(func.a)
        return func

    # Tan
    tan_bracket_term = ParseFunctionOneParam(term_str, "tan")
    if len(tan_bracket_term) > 0:
        func = Tan(tan_bracket_term)
        func.a = ParseTerm(func.a)
        return func

    raise Exception("No token found in: " + term_str)

def PrevTokenLen(term_str : str, closing_brackets : tuple):
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
    elif IsNumeric(term_str[-1]):
        new_open_bracket_idx = len(term_str)-1
        for i in range(len(term_str)-2, -1, -1):
            if not IsNumeric(term_str[i]):
                break
            new_open_bracket_idx = i
        return new_open_bracket_idx
    
    raise Exception("No suitable token found before function!", term_str)

def NextTokenLen(term_str : str, open_brackets : tuple):
    if term_str.startswith(open_brackets):
        closing_bracket_idx = FindClosingBracket(term_str)
        if closing_bracket_idx == -1:
            raise Exception("No suitable closing bracket found!")
        
        return closing_bracket_idx
    elif term_str.startswith("x") or term_str.startswith("e"):
        return 1
    elif IsNumeric(term_str[0]):
        return len(''.join(takewhile(IsNumeric, term_str)))
    
    for func_str in func_strs: # Find function and offset by it's length
        if term_str.startswith(func_str):
            closing_bracket_idx = FindClosingBracket(term_str[len(func_str):])
            if closing_bracket_idx == -1:
                raise Exception("No suitable closing bracket found: " + term_str[len(func_str):])
            
            return len(func_str) + 1 + closing_bracket_idx
    
    raise Exception("No suitable token found before function!", term_str)

def IsMultiplicationApplicable(term_str : str):
    if term_str.startswith(("x", "e", "pi") + tuple(func_strs) + open_brackets):
        return True
    if IsNumeric(term_str[0]):
        return True
    return False

def ImplicitFunctionTwoParams(term_str : str, token : str):
    offset = 0
    idx = term_str.find(token)
    while idx != -1:
        offset = idx+1

        # Brackets around a
        new_open_bracket_idx = PrevTokenLen(term_str[:idx], closing_brackets)
        if term_str[new_open_bracket_idx] != "(":
            term_str = term_str[:idx] + ")" + term_str[idx:]
            term_str = term_str[:new_open_bracket_idx] + "(" + term_str[new_open_bracket_idx:]
            offset += 2

        term_str = term_str[:new_open_bracket_idx] + "(" + term_str[new_open_bracket_idx:]
        offset += 1

        # Brackets around func(a, b)
        closing_bracket_ab_idx = offset + NextTokenLen(term_str[offset:], open_brackets)

        term_str = term_str[:closing_bracket_ab_idx] + ")" + term_str[closing_bracket_ab_idx:]

        if term_str[offset] != "(":
            term_str = term_str[:closing_bracket_ab_idx] + ")" + term_str[closing_bracket_ab_idx:]
            term_str = term_str[:offset] + "(" + term_str[offset:]
            offset += 2
        
        offset += 1

        idx = term_str.find(token, offset)
    return term_str

def InsertImplicitTokens(term_str : str):
    # Implicit function parentheses
    for i in range(len(term_str)-1, 0, -1):
        for func_str in func_strs:

            if term_str[:i].endswith(func_str) and not term_str[i].startswith(open_brackets):
                term_str = term_str[:i] + "(" + term_str[i:]
                param_idx = i+1

                closing_bracket_idx = -1
                if term_str[param_idx] == "x":
                    closing_bracket_idx = param_idx+1
                elif IsNumeric(term_str[param_idx]):
                    numeric_substr_len = 1 + len(''.join(takewhile(IsNumeric, term_str[param_idx+1:])))
                    closing_bracket_idx = param_idx+numeric_substr_len
                elif term_str[param_idx:].startswith(tuple(func_strs)):
                    closing_bracket_idx = 1 + param_idx + FindClosingBracket(term_str[param_idx:])
                else:
                    raise Exception("No suitable token found after function!", term_str[param_idx:])

                term_str = term_str[:closing_bracket_idx] + ")" + term_str[closing_bracket_idx:]

    # Implicit potentiation parentheses
    term_str = ImplicitFunctionTwoParams(term_str, "^")
    
    # Implicit division parentheses
    term_str = ImplicitFunctionTwoParams(term_str, "/")
    
    # Implicit multiplication
    mul_insertion_indicies = SortedSet()
    for i in range(0, len(term_str)-1):
        mul_idx = -1

        if term_str[i] == "x" or term_str[i].startswith(closing_brackets):
            if IsMultiplicationApplicable(term_str[i+1:]):
                mul_idx = i+1
        elif IsNumeric(term_str[i]):
            numeric_substr_len = 1 + len(''.join(takewhile(IsNumeric, term_str[i+1:])))

            if IsMultiplicationApplicable(term_str[i+numeric_substr_len:]):
                mul_idx = i+numeric_substr_len
        
        if mul_idx != -1:
            mul_insertion_indicies.add(mul_idx)

    for i, indices in enumerate(mul_insertion_indicies):
        indices += i
        term_str = term_str[:indices] + "*" + term_str[indices:]
            
    return term_str

def Simplify(term):
    term = term.Simplify()

    term_idx = 0
    breadth_first_terms = [term]
    while term_idx < len(breadth_first_terms):
        breadth_first_terms.extend(breadth_first_terms[term_idx].GetChildren())
        term_idx += 1
    
    for t in breadth_first_terms:
        print(t.String())

    print("Simplified:", term.String())
    return term

def ParseArgs():
    if len(sys.argv) <= 1 or sys.argv[1] == "--help":
        Usage()

    if len(sys.argv) >= 3:
        for i in range(2, len(sys.argv)):
            if sys.argv[i].startswith("-a"):
                interval[0] = float(sys.argv[i][2:])
            elif sys.argv[i].startswith("-b"):
                interval[1] = float(sys.argv[i][2:])
            elif sys.argv[i].startswith("-ya"):
                y_cutoff[0] = float(sys.argv[i][3:])
            elif sys.argv[i].startswith("-yb"):
                y_cutoff[1] = float(sys.argv[i][3:])

    term_str = sys.argv[1]
    term_str = term_str.replace(" ", "") # Remove spaces

    try:
        term_str = InsertImplicitTokens(term_str)
        print("Parsed res:", term_str)
    except Exception as exc:
        print("Error while parsing implicit tokens:", exc)
        exit(-1)

    try:
        return ParseTerm(term_str)
    except Exception as exc:
        print("Error while parsing to internal functions:", exc)
        exit(-1)

term = ParseArgs()

print("Parsed term:", term.String())

term = Simplify(term)

x = np.linspace(interval[0], interval[1], 10000)
if term.Contains(Variable()):
    fig = plt.figure(figsize = (14, 8))
    fx = term.Plot(x)
    fx = np.ma.masked_outside(fx, y_cutoff[0], y_cutoff[1])
    plt.plot(x, fx, 'g', label="f(x)="+term.String())
    plt.xlim(interval)
    plt.ylim(y_cutoff)

print("\nd/dx[", term.String(), "] =")
if term.Contains(Variable()):
    term = term.Derivative()
else:
    term = Constant(0)
print(term.String())

def RmOuterBrackets(term_str : str):
    if term_str.startswith(open_brackets):
        if FindClosingBracket(term_str) == len(term_str)-1:
            return term_str[1:-1]
    return term_str

term = Simplify(term)
print("Simplified:", RmOuterBrackets(term.String()))

if term.Contains(Variable()):
    f_diff_x = term.Plot(x)
    f_diff_x = np.ma.masked_outside(f_diff_x, y_cutoff[0], y_cutoff[1])
    plt.plot(x, f_diff_x, 'r:', label="f'(x)="+term.String())
    plt.grid(True, linestyle =':')
    plt.legend()
    plt.show()