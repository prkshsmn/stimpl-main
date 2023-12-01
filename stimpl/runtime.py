from typing import Any, Tuple, Optional

from stimpl.expression import *
from stimpl.types import *
from stimpl.errors import *

"""
Interpreter State
"""


class State(object):
    def __init__(self, variable_name: str, variable_value: Expr, variable_type: Type, next_state: 'State') -> None:
        self.variable_name = variable_name
        self.value = (variable_value, variable_type)
        self.next_state = next_state

    def copy(self) -> 'State':
        variable_value, variable_type = self.value
        return State(self.variable_name, variable_value, variable_type, self.next_state)

    def set_value(self, variable_name, variable_value, variable_type):
        return State(variable_name, variable_value, variable_type, self)

    def get_value(self, variable_name) -> Any:
        """ TODO: Implement. """
        if self.variable_name == variable_name:
            return self.value
        elif self.next_state is not None:
            return self.next_state.get_value(variable_name)
        else:
            # Variable not found in any state, indicate it's uninitialized
            return None
        
    def __repr__(self) -> str:
        return f"{self.variable_name}: {self.value}, " + repr(self.next_state)


class EmptyState(State):
    def __init__(self):
        pass

    def copy(self) -> 'EmptyState':
        return EmptyState()

    def get_value(self, variable_name) -> None:
        return None

    def __repr__(self) -> str:
        return ""


"""
Main evaluation logic!
"""


def evaluate(expression: Expr, state: State) -> Tuple[Optional[Any], Type, State]:
    match expression:
        case Ren():
            return (None, Unit(), state)

        case IntLiteral(literal=l):
            return (l, Integer(), state)

        case FloatingPointLiteral(literal=l):
            return (l, FloatingPoint(), state)

        case StringLiteral(literal=l):
            return (l, String(), state)

        case BooleanLiteral(literal=l):
            return (l, Boolean(), state)

        case Print(to_print=to_print):
            printable_value, printable_type, new_state = evaluate(
                to_print, state)

            match printable_type:
                case Unit():
                    print("Unit")
                case _:
                    print(f"{printable_value}")

            return (printable_value, printable_type, new_state)

        case Sequence(exprs=exprs) | Program(exprs=exprs):
            """ TODO: Implement. """
            if not exprs:
                return (None, Unit(), state)
            last_value, last_type = (None, Unit())
            current_state = state
            for expr in exprs:
                last_value, last_type, current_state = evaluate(expr, current_state)
            return (last_value, last_type, current_state)



        case Variable(variable_name=variable_name):
            value = state.get_value(variable_name)
            if value == None:
                raise InterpSyntaxError(
                    f"Cannot read from {variable_name} before assignment.")
            variable_value, variable_type = value
            return (variable_value, variable_type, state)

        case Assign(variable=variable, value=value):

            value_result, value_type, new_state = evaluate(value, state)

            variable_from_state = new_state.get_value(variable.variable_name)
            _, variable_type = variable_from_state if variable_from_state else (
                None, None)

            if value_type != variable_type and variable_type != None:
                raise InterpTypeError(f"""Mismatched types for Assignment:
            Cannot assign {value_type} to {variable_type}""")

            new_state = new_state.set_value(
                variable.variable_name, value_result, value_type)
            return (value_result, value_type, new_state)

        case Add(left=left, right=right):
            result = 0
            left_result, left_type, new_state = evaluate(left, state)
            right_result, right_type, new_state = evaluate(right, new_state)

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Add:
            Cannot add {left_type} to {right_type}""")

            match left_type:
                case Integer() | String() | FloatingPoint():
                    result = left_result + right_result
                case _:
                    raise InterpTypeError(f"""Cannot add {left_type}s""")

            return (result, left_type, new_state)

        case Subtract(left=left, right=right):
            """ TODO: Implement. """
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            if not (isinstance(left_type, type(right_type)) and (isinstance(left_type, Integer) or isinstance(left_type, FloatingPoint))):
                raise InterpTypeError("Subtraction requires operands of the same numeric type.")

            result = left_value - right_value
            return (result, left_type, new_state)

        case Multiply(left=left, right=right):
            """ TODO: Implement. """
            # Evaluate the left operand
            left_value, left_type, new_state = evaluate(left, state)
            # Evaluate the right operand
            right_value, right_type, new_state = evaluate(right, new_state)

            # Check if both operands are of numeric types (Integer or FloatingPoint)
            if not ((isinstance(left_type, Integer) and isinstance(right_type, Integer)) or 
                    (isinstance(left_type, FloatingPoint) and isinstance(right_type, FloatingPoint))):
                raise InterpTypeError("Multiplication requires operands of the same numeric type.")

            # Perform multiplication
            result = left_value * right_value

            # Determine the result type (keep it as Integer if both operands are integers, otherwise FloatingPoint)
            result_type = Integer() if isinstance(left_type, Integer) and isinstance(right_type, Integer) else FloatingPoint()

            return (result, result_type, new_state)



        case Divide(left=left, right=right):
            """ TODO: Implement. """
            # Evaluate the left operand
            left_value, left_type, new_state = evaluate(left, state)
            # Evaluate the right operand
            right_value, right_type, new_state = evaluate(right, new_state)

            # Check if both operands are of numeric types
            if isinstance(left_type, (Integer, FloatingPoint)) and isinstance(right_type, (Integer, FloatingPoint)):
                # Check for division by zero
                if right_value == 0:
                    raise InterpMathError("Division by zero error.")
                # Perform division and return the result with the appropriate type
                return (left_value / right_value, left_type if isinstance(left_type, Integer) else right_type, new_state)
            else:
                raise InterpTypeError("Division requires numeric types.")

        case And(left=left, right=right):
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for And:
            Cannot evaluate {left_type} and {right_type}""")
            match left_type:
                case Boolean():
                    result = left_value and right_value
                case _:
                    raise InterpTypeError(
                        "Cannot perform logical and on non-boolean operands.")

            return (result, left_type, new_state)

        case Or(left=left, right=right):
            """ TODO: Implement. """
            # Evaluate the left operand
            left_value, left_type, new_state = evaluate(left, state)

            # Short-circuit if the left operand is True
            if left_type == Boolean() and left_value is True:
                return (True, Boolean(), new_state)

            # Evaluate the right operand if the left operand is not True
            right_value, right_type, new_state = evaluate(right, new_state)

            # Perform logical OR and return the result
            result = (left_value or right_value) and left_type == Boolean() and right_type == Boolean()
            return (result, Boolean(), new_state)

        case Not(expr=expr):
            """ TODO: Implement. """
            # Evaluate the operand
            operand_value, operand_type, new_state = evaluate(expr, state)

            # Check if the operand is of boolean type
            if isinstance(operand_type, Boolean):
                # Perform logical negation and return the result
                return (not operand_value, Boolean(), new_state)
            else:
                raise InterpTypeError("Logical NOT requires a boolean type.")

        case If(condition=condition, true=true, false=false):
            """ TODO: Implement. """
            # Evaluate the condition
            condition_value, condition_type, new_state = evaluate(condition, state)

            # Check if the condition is of boolean type
            if not isinstance(condition_type, Boolean):
                raise InterpTypeError("Condition in If expression must be boolean")

            # Evaluate and return the result of the 'true' branch if condition is True
            if condition_value:
                return evaluate(true, new_state)
            
            # Otherwise, evaluate and return the result of the 'false' branch
            else:
                return evaluate(false, new_state)

        case Lt(left=left, right=right):
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            result = None

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Lt:
            Cannot compare {left_type} and {right_type}""")

            match left_type:
                case Integer() | Boolean() | String() | FloatingPoint():
                    result = left_value < right_value
                case Unit():
                    result = False
                case _:
                    raise InterpTypeError(
                        f"Cannot perform < on {left_type} type.")

            return (result, Boolean(), new_state)

        case Lte(left=left, right=right):
            """ TODO: Implement. """
            # Evaluate the left operand
            left_value, left_type, new_state = evaluate(left, state)
            # Evaluate the right operand
            right_value, right_type, new_state = evaluate(right, new_state)

            if left_value is None and right_value is None:
                result = True  
            elif left_value is None:
                result = True 
            elif right_value is None:
                result = False 
            else:
                result = left_value <= right_value

            return (result, Boolean(), new_state)



        case Gt(left=left, right=right):
            """ TODO: Implement. """
            # Evaluate the left operand
            left_value, left_type, new_state = evaluate(left, state)
            # Evaluate the right operand
            right_value, right_type, new_state = evaluate(right, new_state)

            if isinstance(left_value, (int, float, str)) and isinstance(right_value, (int, float, str)):
                result = left_value > right_value
            elif left_value is None or right_value is None:

                result = False if left_value is None else True
            else:
                raise InterpTypeError("Gt operation cannot compare these types.")

            return (result, Boolean(), new_state)


        case Gte(left=left, right=right):
            """ TODO: Implement. """
            # Evaluate the left operand
            left_value, left_type, new_state = evaluate(left, state)
            # Evaluate the right operand
            right_value, right_type, new_state = evaluate(right, new_state)

            # Ensure both operands are of numeric types
            if isinstance(left_type, (Integer, FloatingPoint)) and isinstance(right_type, (Integer, FloatingPoint)):
                # Perform the comparison and return the result
                return (left_value >= right_value, Boolean(), new_state)
            else:
                raise InterpTypeError("Gte operation requires numeric types.")

        case Eq(left=left, right=right):
            """ TODO: Implement. """
            # Evaluate the left operand
            left_value, left_type, new_state = evaluate(left, state)
            # Evaluate the right operand
            right_value, right_type, new_state = evaluate(right, new_state)

            # Perform the comparison for equality and return the result
            result = left_value == right_value
            return (result, Boolean(), new_state)


        case Ne(left=left, right=right):
            """ TODO: Implement. """
            # Evaluate the left operand
            left_value, left_type, new_state = evaluate(left, state)
            # Evaluate the right operand
            right_value, right_type, new_state = evaluate(right, new_state)

            # Perform the comparison for inequality and return the result
            result = left_value != right_value
            return (result, Boolean(), new_state)


        case While(condition=condition, body=body):
            # Initialize the result and type for the While loop
            result, result_type = None, None

            # Evaluate the condition
            condition_value, condition_type, new_state = evaluate(condition, state)

            # Check if the condition is of boolean type
            if not isinstance(condition_type, Boolean):
                raise InterpTypeError("Condition in While loop must be boolean")

            # Loop while the condition is True
            while condition_value:
                # Evaluate the body of the loop
                result, result_type, new_state = evaluate(body, new_state)

                # Re-evaluate the condition for the next iteration
                condition_value, condition_type, new_state = evaluate(condition, new_state)

            return (result, result_type, new_state)

        case _:
            raise InterpSyntaxError("Unhandled!")
    pass


def run_stimpl(program, debug=False):
    state = EmptyState()
    program_value, program_type, program_state = evaluate(program, state)

    if debug:
        print(f"program: {program}")
        print(f"final_value: ({program_value}, {program_type})")
        print(f"final_state: {program_state}")

    return program_value, program_type, program_state
