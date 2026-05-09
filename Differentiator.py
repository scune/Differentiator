import sys

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
        if type(other) == Constant:
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
    
    def String(self):
        return "x"
    
    def Simplify(self):
        return self

    def Token():
        return ""

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
                self.a.b += self.b.b
                return self.a.Simplify()
        elif type(self.a) is Exponential and type(self.b) is Exponential:
            self.a.a += self.b.a
            return self.a.Simplify()
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
        
        return self
    
    def Token():
        return "e^"

def ParseArgs():
    if len(sys.argv) <= 1 or sys.argv[1] == "--help":
        Usage()

    term_str = sys.argv[2]
    term_str.replace(" ", "")
    
    tokens = []
    for function in BaseFunction.__subclasses__():
        tokens.append(function.Token())

term = ParseArgs()

print("d/dx[", term.String(), "] =")
term = term.Derivative()
print(term.String())
term = term.Simplify()
print("Simplified:", term.String())
# TODO: Simplify e^lnx and ln(e^x)