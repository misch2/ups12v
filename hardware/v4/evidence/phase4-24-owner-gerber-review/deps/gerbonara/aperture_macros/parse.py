#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021 Jan Sebastian Götte <gerbonara@jaseg.de>

from dataclasses import dataclass, field, replace, fields
import operator
import re
import ast
import copy
import warnings
import math

from . import primitive as ap
from .expression import *
from ..apertures import ApertureMacroInstance
from ..utils import MM

# we make our own here instead of using math.degrees to make sure this works with expressions, too.
def rad_to_deg(x):
    return (x / math.pi) * 180

def _map_expression(node, variables={}, parameters=set()):
    if isinstance(node, ast.Constant):
        return ConstantExpression(node.value)

    elif isinstance(node, ast.BinOp):
        op_map = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}
        return OperatorExpression(op_map[type(node.op)],
                                  _map_expression(node.left, variables, parameters),
                                  _map_expression(node.right, variables, parameters))

    elif isinstance(node, ast.UnaryOp):
        if type(node.op) == ast.UAdd:
            return _map_expression(node.operand, variables, parameters)
        else:
            return NegatedExpression(_map_expression(node.operand, variables, parameters))

    elif isinstance(node, ast.Name):
        num = int(node.id[3:]) # node.id has format var[0-9]+
        if num in variables:
            return VariableExpression(variables[num])
        else:
            parameters.add(num)
            return ParameterExpression(num)

    else:
        raise SyntaxError('Invalid aperture macro expression')

def _parse_expression(expr, variables, parameters):
    expr = expr.lower().replace('x', '*')
    expr = re.sub(r'\$([0-9]+)', r'var\1', expr)
    try:
        parsed = ast.parse(expr, mode='eval').body
    except SyntaxError as e:
        raise SyntaxError('Invalid aperture macro expression') from e
    return _map_expression(parsed, variables, parameters)

@dataclass(frozen=True, slots=True)
class ApertureMacro:
    """ Definition of an aperture macro in a Gerber file.

        An aperture macro is a collection of shape primitives that are flashed all at once. The properties of these
        primitives such as their relative position and size can be given explicitly, or can be given as a basic
        arithmetic expression (so +/-/*/:, no higher functions) based on parameters. After the macro is defined in the
        Gerber file, it is *bound* to a particular set of parameter values in an aperture definition. One macro can be
        used by zero, or by multiple aperture definitions. To flash a macro, you must first bind it in an aperture
        definition, which can then be flash'ed.

        Gerbonara calls these apertures that bind a macro :py:class:`~..apertures.ApertureMacroInst`. You can bind a
        macro to a set of parameters by calling it:

        .. code-block: python

            # am is some instance of ApertureMacro
            aperture_def = am(1, 2, 3)
            gerber.objects.append(Flash(x=12, y=34, aperture=aperture_def))
        
        Internally, the aperture macro API uses millimeters though most functions allow you to pass an unit parameter.

        When you want to programmatically create aperture macros, we recommend using :py:meth:`~.ApertureMacro.map` on a
        dataclass-like class definition. Have a look at this code from :py:class:`~.GenericMacros`:

        .. code-block: python

            @ApertureMacro.map('GNR')
            class rect:
                w: float # width
                h: float # height
                hole_dia: float = 0
                rotation: float = 0

                def draw(self):
                    yield ap.CenterLine('mm', 1, self.w, self.h, 0, 0, self.rotation * -deg_per_rad)
                    yield ap.Circle('mm', 0, self.hole_dia, 0, 0)

            # rect now is an instance of ApertureMacro

        After this, you can bind this macro to an aperture by calling it. When you use this dataclass-like syntax,
        keyword arguments are supported, and default values work like with normal dataclasses:
            
        .. code-block: python

            # returns an instance of ApertureMacroInstance containing the given parameters
            my_rect = GenericMacros.rect(w=12, h=34)

            gerber.objects.append(Flash(x=12, y=34, aperture=my_rect))
        
        .. important::
            Use your own programmatically defined aperture macros sparingly. While support is getting better, many
            tools, including the expensive, commercial tools that PCB manufacturers use, still have bugs when handling
            aperture macros. When using advanced macros with many primitives or with complex, embedded arithmetic
            expressions, make sure to carefully check the manufacturing files provided by your PCB fab.

            gerbonara currently handles embedded arithmetic expressions by *always* calculating them out since we have
            recently seen high-end commercial tooling failing at issues as basic as operator precedence. This increases
            file sizes very very slightly, but it makes sure that you get correct results.

            This means that you can use gerbonara to calculate out aperture macros and hard-bake their values into the
            gerber source. This can be useful if you have a file that includes complex macros that some manufacturer's
            tooling can't handle on its own.
            """

    name: str = field(default=None, hash=False, compare=False)
    num_parameters: int = 0
    primitives: tuple = ()
    comments: tuple = field(default=(), hash=False, compare=False)
    _param_dataclass: object = field(default=None, hash=False, compare=False)

    def __post_init__(self):
        if self.name is None or re.match(r'GNX[0-9A-F]{16}', self.name):
            # We can't use field(default_factory=...) here because that factory doesn't get a reference to the instance.
            self._reset_name()

    def _reset_name(self):
        object.__setattr__(self, 'name', f'GNX{hash(self)&0xffffffffffffffff:016X}')

    @classmethod
    def map(our_kls, macro_name=None):
        def wrapper(kls):
            nonlocal our_kls, macro_name
            dc = dataclass(kls)
            
            # Construct a mock instance of the dataclass with every field bound to its correpsonding ParameterExpression,
            # then draw() it to get a list of bound macro primitives.
            primitives = tuple(dc(*[ParameterExpression(i+1) for i in range(len(fields(dc)))]).draw())
            name = macro_name if macro_name else f'GNM{kls.__name__}'

            # Python allows a lot more unicode in class names than the Gerber spec allows in aperture macro names
            if not re.fullmatch('[._$a-zA-Z][._$a-zA-Z0-9]{0,126}', name):
                raise ValueError(f'Name {name!r} is invalid as an aperture macro name')

            return our_kls(
                name = name,
                num_parameters = len(fields(dc)),
                primitives = primitives,
                comments = [l.strip() for l in dc.__doc__.strip().splitlines()],
                _param_dataclass = dc)
        return wrapper

    def __call__(self, *args, unit=MM, **kwargs):
        if self._param_dataclass:
            # Above, in map(), we construct the dataclass with the ParameterExpression(i) as params to draw the macro
            # primitives. Here, we construct it with the user's supplied concrete numeric parameters instead, and then
            # extract a list of these parameters. This should work great as long as the user doesn't get too fancy with
            # dataclass metaprogramming hackery.
            bound = self._param_dataclass(*args, **kwargs)
            return ApertureMacroInstance(macro=self, parameters=tuple(getattr(bound, f.name) or 0 for f in fields(bound)), unit=unit)

    @classmethod
    def parse_macro(kls, macro_name, body, unit):
        comments = []
        variables = {}
        parameters = set()
        primitives = []

        blocks = body.split('*')
        for block in blocks:
            if not (block := block.strip()): # empty block
                continue

            if block.startswith('0 '): # comment
                comments.append(block[2:])
                continue
            
            block = re.sub(r'\s', '', block)

            if block[0] == '$': # variable definition
                try:
                    name, _, expr = block.partition('=')
                    number = int(name[1:])
                    if number in variables:
                        warnings.warn(f'Re-definition of aperture macro variable ${number} inside aperture macro "{macro_name}". Previous definition of ${number} was ${variables[number]}.')
                    variables[number] = _parse_expression(expr, variables, parameters)
                except Exception as e:
                    raise SyntaxError(f'Error parsing variable definition {block!r}') from e

            else: # primitive
                primitive, *args = block.split(',')
                args = [ _parse_expression(arg, variables, parameters) for arg in args ]
                try:
                    primitives.append(ap.PRIMITIVE_CLASSES[int(primitive)].from_arglist(unit, args))
                except KeyError as e:
                    raise SyntaxError(f'Unknown aperture macro primitive code {int(primitive)}')

        return kls(macro_name, max(parameters, default=0), tuple(primitives), tuple(comments))

    def __str__(self):
        return f'<Aperture macro {self.name}, primitives {self.primitives}>'

    def __repr__(self):
        return str(self)

    def dilated(self, offset, unit=MM):
        new_primitives = []
        for primitive in self.primitives:
            try:
                if primitive.exposure.calculate():
                    new_primitives += primitive.dilated(offset, unit)
            except IndexError:
                warnings.warn('Cannot dilate aperture macro primitive with exposure value computed from macro variable.')
                pass
        return replace(self, primitives=tuple(new_primitives))

    def substitute_params(self, params, unit=None, macro_name=None):
        params = dict(enumerate(params, start=1))
        return replace(self,
                       num_parameters=0,
                       name=macro_name,
                       primitives=tuple(p.substitute_params(params, unit) for p in self.primitives),
                       comments=(f'Fully substituted instance of {self.name} macro',
                                 f'Original parameters: {"X".join(map(str, params.values())) if params else "none"}'))

    def to_gerber(self, settings):
        """ Serialize this macro's content (without the name) into Gerber using the given file unit """
        comments = [ f'0 {c.replace("*", "_").replace("%", "_")}' for c in self.comments ]

        subexpression_variables = {}
        def register_variable(expr):
            expr_str = expr.to_gerber(register_variable, settings.unit)
            if expr_str not in subexpression_variables:
                subexpression_variables[expr_str] = self.num_parameters + 1 + len(subexpression_variables)
            return subexpression_variables[expr_str]

        primitive_defs = [prim.to_gerber(register_variable, settings) for prim in self.primitives]
        variable_defs = [f'${num}={expr_str}' for expr_str, num in subexpression_variables.items()]
        return '*\n'.join(comments + variable_defs + primitive_defs)

    def to_graphic_primitives(self, offset, rotation, parameters : [float], unit=None, polarity_dark=True):
        parameters = dict(enumerate(parameters, start=1))
        for primitive in self.primitives:
            yield from primitive.to_graphic_primitives(offset, rotation, parameters, unit, polarity_dark)

    def rotated(self, angle):
        # aperture macro primitives use degree counter-clockwise, our API uses radians clockwise
        return replace(self, primitives=tuple(
            replace(primitive, rotation=primitive.rotation - rad_to_deg(angle)) for primitive in self.primitives))

    def scaled(self, scale):
        return replace(self, primitives=tuple(
            primitive.scaled(scale) for primitive in self.primitives))


var = ParameterExpression
deg_per_rad = 180 / math.pi

class GenericMacros:
    """NOTE:
       All generic macros have rotation values specified in **clockwise radians** like the rest of the user-facing API.
    """

    @ApertureMacro.map('GNC')
    class circle:
        """ Filled circle macro with an optional round hole
        
        :param float diameter: Diameter of the circle
        :param hole_dia: Diameter of the hole (optional)
        """
        diameter: float
        hole_dia: float = 0

        def draw(self):
            yield ap.Circle('mm', 1, self.diameter, 0, 0)
            yield ap.Circle('mm', 0, self.hole_dia, 0, 0)

    @ApertureMacro.map('GNR')
    class rect:
        """ Axis-aligned rectangle with an optional round center hole.

        :param float w: Width
        :param float h: Height
        :param float hole_dia: Diameter of the round hole (optional)
        :param float rotation: Rotation in clockwise radians (optional)
        """
        w: float # width
        h: float # height
        hole_dia: float = 0
        rotation: float = 0

        def draw(self):
            yield ap.CenterLine('mm', 1, self.w, self.h, 0, 0, self.rotation * -deg_per_rad)
            yield ap.Circle('mm', 0, self.hole_dia, 0, 0)

    @ApertureMacro.map('GRR')
    class rounded_rect:
        """ Rectangle with circular arc corners and an optional round center hole.

        :param float w: Width
        :param float h: Height
        :param float r: Corner radius
        :param float hole_dia: Diameter of the round hole (optional)
        :param float rotation: Rotation in clockwise radians (optional)
        """
        w: float # width
        h: float # height
        r: float # Corner radius
        hole_dia: float = 0
        rotation: float = 0

        def draw(self):
            yield ap.CenterLine('mm', 1, self.w-2*self.r, self.h, 0, 0, self.rotation * -deg_per_rad)
            yield ap.CenterLine('mm', 1, self.w, self.h-2*self.r, 0, 0, self.rotation * -deg_per_rad)
            yield ap.Circle('mm', 1, self.r*2, +(self.w/2-self.r), +(self.h/2-self.r), self.rotation * -deg_per_rad)
            yield ap.Circle('mm', 1, self.r*2, +(self.w/2-self.r), -(self.h/2-self.r), self.rotation * -deg_per_rad)
            yield ap.Circle('mm', 1, self.r*2, -(self.w/2-self.r), +(self.h/2-self.r), self.rotation * -deg_per_rad)
            yield ap.Circle('mm', 1, self.r*2, -(self.w/2-self.r), -(self.h/2-self.r), self.rotation * -deg_per_rad)
            yield ap.Circle('mm', 0, self.hole_dia, 0, 0)

    @ApertureMacro.map('GTR')
    class isosceles_trapezoid:
        """ Isosceles trapezoid with a wider bottom edge and narrower top edge, with an optional round center hole.

        :param float w: Width of the bottom (wider) edge
        :param float h: Height
        :param float d: Length difference between bottom and top edges; top width = w - d
        :param float hole_dia: Diameter of the round hole (optional)
        :param float rotation: Rotation in clockwise radians (optional)
        """
        w: float # width
        h: float # height
        d: float # length difference between narrow side (top) and wide side (bottom)
        hole_dia: float = 0
        rotation: float = 0
        
        def draw(self):
            yield ap.Outline('mm', 1, 4,
                          (self.w/-2,            self.h/-2,
                          self.w/-2+self.d/2,   self.h/2,
                          self.w/2-self.d/2,    self.h/2,
                          self.w/2,             self.h/-2,
                          self.w/-2,            self.h/-2,),
                          self.rotation * -deg_per_rad)
            yield ap.Circle('mm', 0, self.hole_dia, 0, 0)

    @ApertureMacro.map('GRTR')
    class rounded_isosceles_trapezoid:
        """ Isosceles trapezoid with rounded corners and an optional round center hole. Unlike the rounded rectangle, the shape is defined by first defining a non-rounded trapezoid, which is then offet to the outside by the given margin.

        :param float w: Width of the bottom (wider) edge
        :param float h: Height
        :param float d: Length difference between bottom and top edges; top width = w - d
        :param float margin: Corner rounding radius
        :param float hole_dia: Diameter of the round hole (optional)
        :param float rotation: Rotation in clockwise radians (optional)
        """
        w: float
        h: float
        d: float # length difference between narrow side (top) and wide side (bottom)
        margin: float
        hole_dia: float = 0
        rotation: float = 0

        def draw(self):
            rot = self.rotation * -deg_per_rad
            yield ap.Outline('mm', 1, 4,
                              (self.w/-2,            self.h/-2,
                               self.w/-2+self.d/2,   self.h/2,
                               self.w/2-self.d/2,    self.h/2,
                               self.w/2,             self.h/-2,
                               self.w/-2,            self.h/-2,),
                             rot)

            yield ap.VectorLine('mm', 1, self.margin*2, 
                               self.w/-2,            self.h/-2,
                               self.w/-2+self.d/2,   self.h/2,
                               rot)
            yield ap.VectorLine('mm', 1, self.margin*2, 
                               self.w/-2+self.d/2,   self.h/2,
                               self.w/2-self.d/2,    self.h/2,
                               rot)
            yield ap.VectorLine('mm', 1, self.margin*2, 
                                self.w/2-self.d/2,    self.h/2,
                                self.w/2,             self.h/-2,
                                rot)
            yield ap.VectorLine('mm', 1, self.margin*2,
                                self.w/2,             self.h/-2,
                                self.w/-2,            self.h/-2,
                                rot)

            yield ap.Circle('mm', 1, self.margin*2,
                                self.w/-2,            self.h/-2,
                            rot)
            yield ap.Circle('mm', 1, self.margin*2, 
                                self.w/-2+self.d/2,   self.h/2,
                            rot)
            yield ap.Circle('mm', 1, self.margin*2, 
                                self.w/2-self.d/2,    self.h/2,
                            rot)
            yield ap.Circle('mm', 1, self.margin*2, 
                                self.w/2,             self.h/-2,
                            rot)

            yield ap.Circle('mm', 0, self.hole_dia, 0, 0)

    @ApertureMacro.map('GNO')
    class obround:
        """ Rectangle with semicircular end caps (stadium shape), with an optional round center hole. The long axis is along the X axis when rotation is zero.

        :param float w: Total width including end caps; must satisfy w >= h
        :param float h: Height, equal to the end cap diameter
        :param float hole_dia: Diameter of the round hole (optional)
        :param float rotation: Rotation in clockwise radians (optional)
        """
        w: float
        h: float
        hole_dia: float = 0
        rotation: float = 0

        def draw(self):
            rot = self.rotation * -deg_per_rad
            yield ap.CenterLine('mm', 1, self.w - self.h, self.h, 0, 0, rot)
            yield ap.Circle('mm', 1, self.h, +(self.w-self.h)/2, 0, rot)
            yield ap.Circle('mm', 1, self.h, -(self.w-self.h)/2, 0, rot)
            yield ap.Circle('mm', 0, self.hole_dia, 0, 0)

    @ApertureMacro.map('GNP')
    class polygon:
        """ Regular n-sided polygon with an optional round center hole.

        :param int n: Number of sides
        :param float diameter: Diameter of the circumscribed circle
        :param float hole_dia: Diameter of the round hole (optional)
        :param float rotation: Rotation in clockwise radians (optional)
        """
        n: int
        diameter: float
        hole_dia: float = 0
        rotation: float = 0

        def draw(self):
            yield ap.Polygon('mm', 1, self.diameter, 0, 0, self.n, self.rotation * -deg_per_rad)
            yield ap.Circle('mm', 0, self.hole_dia, 0, 0)


if __name__ == '__main__':
    import sys
    #for line in sys.stdin:
        #expr = _parse_expression(line.strip())
        #print(expr, '->', expr.optimized())

    for primitive in parse_macro(sys.stdin.read(), 'mm'):
        print(primitive)

