import textx as tx
import sys



class Brick:
    def __init__(self, parent, name, child):
        self.parent = parent
        self.name = name
        self.child = child

    def setup_code(self):
        return self.child.setup_code()

    def __str__(self):
        return str(self.child)

class Actuator:
    def __init__(self, parent, pin):
        self.parent = parent
        self.pin = pin

    def setup_code(self):
        return "pinMode({}, OUTPUT);".format(self.parent.name)

    def __str__(self):
        return "int {} = {};".format(self.parent.name, self.pin)

class Sensor:
    def __init__(self, parent, pin):
        self.parent = parent
        self.pin = pin

    def setup_code(self):
        return "pinMode({}, INPUT);".format(self.parent.name)

    def __str__(self):
        return "int {} = {};".format(self.parent.name, self.pin)

class DigitalValue:
    def __init__(self, parent, value):
        self.parent=parent
        self.value=value

    def __str__(self):
        return 'HIGH' if self.value == 'ON' else "LOW"

class Action:
    def __init__(self, parent,type, var, value):
        self.parent = parent
        self.type = type
        self.var = var
        self.value = value

    def __str__(self):
        if self.type == "SET":
            return 'digitalWrite({}, {});\n'.format(self.var, self.value)
        if self.type == "PRINT":
            return '{lcd_name}.setCursor(0, 0);\n' \
                   '\t{lcd_name}.print("{value}");\n'.format(lcd_name=self.var,value=self.value.ljust(16))
        if self.type == "CLEAR":
            return '{lcd_name}.clear();\n'.format(lcd_name=self.var)

class Transition:
    def __init__(self, parent, cond, next_state):
        self.parent = parent
        self.cond = cond
        self.next_state = next_state

    def __str__(self):
        transition = open('templates/transition.amlt').read()
        return transition.format(condition=self.cond,
                                 next_state=self.next_state,
                                 current_state_name=self.parent.name)

class State:
    def __init__(self, parent, is_init_state, name,exprs):
        self.parent = parent
        self.is_init_state = is_init_state
        self.name = name
        self.exprs = exprs

    def __str__(self):
        state = open('templates/state.amlt').read()
        return state.format(name=self.name, code='\t'.join([str(expr) for expr in self.exprs]))

class Condition:
    def __init__(self,parent, l, r, op, single):
        self.parent = parent
        self.l = l
        self.r = r
        self.op = op
        self.single = single

    def __str__(self):
        if type(self.single) == Bexpr:
            return str(self.single)
        return '{} {} {}'.format(self.l, self.op, self.r)

class Bop:
    def __init__(self,parent, token):
        self.parent = parent
        self.token = token

    def __str__(self):
        ops = {'AND': '&&', 'OR': '||'}
        return ops[self.token]

class Bexpr:
    def __init__(self, parent, var,op, value):
        self.parent = parent
        self.var = var
        self.op = op
        self.value = value

    def __str__(self):
        return 'digitalRead({}) {} {}'.format(self.var, self.op, self.value)

class Lcd:
    def __init__(self, parent,bus_id):
        self.parent = parent
        self.bus_id = bus_id

    def get_bus_pins(self):
        if self.bus_id == 1:
            return '2, 3, 4, 5, 6, 7, 8'
        if self.bus_id == 2:
            return '10, 11, 12, 13, 14, 15, 16'
        else:
            raise ValueError('Invalid Bus for lcd {} must be 1 or 2'.format(self.parent.name))

    def setup_code(self):
        return "{}.begin(16, 2);".format(self.parent.name)

    def __str__(self):
        return 'LiquidCrystal lcd({});'.format(self.get_bus_pins())


class Model(object):
    def __init__(self, bricks, states):
        self.bricks = bricks
        self.states = states

        self.init_state = self.generate_loop_code()

    def generate_includes(self):
        out = set()
        for e in self.bricks:
            if type(e) == Lcd:
                out.add("LiquidCrystal.h")
        return '\n'.join(["#include <{}>".format(e) for e in out])

    def generate_setup_code(self):
        setup = open("templates/setup.amlt", 'r').read()
        return setup.format(setup_code='\n\t' + '\n\t'.join([e.setup_code() for e in self.bricks]))

    def generate_loop_code(self):
        init_states = list(map(lambda e: e.name,
                               list(filter(lambda e: e.is_init_state, self.states))))
        if len(init_states) != 1:
            raise SyntaxError("Invalid number of initial state")

        return 'void loop() {{ {init_state}(); }}'.format(init_state=init_states[0])

    def __str__(self):

        header = open("header.txt", 'r').read()
        return "{}\n{}\n{}\n{}\n{}\n{}".format(header,
                                               self.generate_includes(),
                                                '\n'.join([str(brick) for brick in self.bricks]),
                                                self.generate_setup_code(),
                                                '\n'.join([str(state) for state in self.states]),
                                                self.init_state)


def cname(o):
    return o.__class__.__name__

classes=[Model,Brick, Actuator, Sensor, DigitalValue, State, Transition, Action, Condition, Bop, Bexpr, Lcd]

mmodel = tx.metamodel_from_file('grammar.tx', classes=classes)

if len(sys.argv) < 2 :
    print(mmodel.model_from_file('tests/condition.aml'))
else:


    if len(sys.argv) > 1:
        model = mmodel.model_from_file(sys.argv[1])
        print(model)
        exit(0)

    data = sys.stdin.readlines()
    if len(data) > 0:

        for e in data:

            e = e.replace('\n', '')
            output_name = e.split('/')[-1].replace('.aml', '.ino')
            output_f = open('out/' + output_name, 'w')
            model = mmodel.model_from_file(e)
            print(model, file=output_f)