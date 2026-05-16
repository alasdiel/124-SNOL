import re
from typing import Any, Dict, Optional, Sequence, Tuple

print("The SNOL environment is now active, you may proceed with giving your commands.")

command_var = "Command: "

snol_vars = {}

reserved_keywords = {"BEG", "PRINT", "EXIT!"}


def snol_print(message: Any) -> None:
    """Print a SNOL-prefixed message."""
    print(f"SNOL> {message}")


def is_valid_var_name(name: str) -> bool:
    """Validate SNOL variable names (alpha-starting, identifier-safe, not reserved)."""
    if name in reserved_keywords:
        return False
    if not name:
        return False
    if not name[0].isalpha():
        return False
    return name.isidentifier()


def is_identifier_token(token: str) -> bool:
    """Return True if token is a non-reserved identifier."""
    return token.isidentifier() and token not in reserved_keywords


def parse_token(
        token: str,
        variables: Dict[str, Any],
        require_defined: bool = False,
) -> Tuple[Optional[Any], Optional[str]]:
    """Parse a token into a value, enforcing SNOL number formats."""
    if token in variables:
        return variables[token], None
    if require_defined and is_identifier_token(token):
        return None, f"Error! [{token}] is not defined!"
    if re.match(r"^\d+$", token):
        return int(token), None
    if re.match(r"^\d+\.\d+$", token):
        return float(token), None
    if any(ch.isdigit() or ch == "." for ch in token):
        return None, "Error: invalid number format"
    return token, None


def apply_arithmetic(
        left_val: Any,
        op: str,
        right_val: Any,
) -> Tuple[Optional[Any], Optional[str]]:
    """Apply arithmetic to two numeric values."""
    if not isinstance(left_val, (int, float)) or not isinstance(right_val, (int, float)):
        return None, "Error: arithmetic requires numbers"

    if type(left_val) is not type(right_val):
        return None, "Error: cannot mix types in arithmetic"

    if op == "+":
        return left_val + right_val, None
    if op == "-":
        return left_val - right_val, None
    if op == "*":
        return left_val * right_val, None
    if op == "/":
        if right_val == 0:
            return None, "Error: division by zero"
        if isinstance(left_val, int) and isinstance(right_val, int):
            return left_val // right_val, None
        else:
            return left_val / right_val, None
    if op == "%":
        if not isinstance(left_val, int) or not isinstance(right_val, int):
            return None, "Error: modulo requires integers"
        if right_val == 0:
            return None, "Error: division by zero"
        return left_val % right_val, None

    return None, "Error: unknown operator"


def evaluate_chain(
        tokens: Sequence[str],
        variables: Dict[str, Any],
) -> Tuple[Optional[Any], Optional[str]]:
    """Evaluate an arithmetic chain with operator precedence (no parentheses)."""
    if len(tokens) < 3 or len(tokens) % 2 == 0:
        return None, "Error: invalid arithmetic expression"

    ops = {"+", "-", "*", "/", "%"}
    if any(token in reserved_keywords for token in tokens):
        return None, "Unknown command! Does not match any valid command of the language."
    for i in range(1, len(tokens), 2):
        if tokens[i] not in ops:
            return None, "Error: invalid arithmetic expression"

    values = []
    ops_list = []
    for i in range(0, len(tokens), 2):
        value, error = parse_token(tokens[i], variables, require_defined=True)
        if error:
            return None, error
        values.append(value)
        if i + 1 < len(tokens):
            ops_list.append(tokens[i + 1])

    high_ops = {"*", "/", "%"}
    idx = 0
    while idx < len(ops_list):
        op = ops_list[idx]
        if op in high_ops:
            result, error = apply_arithmetic(values[idx], op, values[idx + 1])
            if error:
                return None, error
            values[idx] = result
            del values[idx + 1]
            del ops_list[idx]
            continue
        idx += 1

    current = values[0]
    for i, op in enumerate(ops_list):
        current, error = apply_arithmetic(current, op, values[i + 1])
        if error:
            return None, error

    return current, None


while True:
    command_var = "Command: "
    command_var = input(command_var)
    split_command = command_var.split(sep=" ")

    if split_command == [""]:
        snol_print("Unknown command! Does not match any valid command of the language.")
        print("\n")
        continue

    if split_command[0] == "EXIT!":  # exit
        print("Interpreter is now terminated...")
        exit()

    if split_command[0] == "BEG":  # input variable on cli
        if len(split_command) < 2 or not split_command[1]:
            snol_print("Error: BEG requires a variable name")
            print("\n")
            continue
        snol_print(f"Please enter value for [{split_command[1]}]")
        print("Input: ", end="")
        beg_var = input()
        if not is_valid_var_name(split_command[1]):
            snol_print("Error: invalid variable name")
        else:
            value, _ = parse_token(beg_var, snol_vars)
            snol_vars[split_command[1]] = value
        print("\n")
        continue

    if split_command[0] == "PRINT":  # print variable
        if len(split_command) < 2 or not split_command[1]:
            snol_print("Error: PRINT requires a value or variable")
            print("\n")
            continue
        if len(split_command) >= 3:
            result, error = evaluate_chain(split_command[1:], snol_vars)
            if error:
                snol_print(error)
            else:
                snol_print(result)
            print("\n")
            continue
        if split_command[1] in snol_vars:
            snol_print("[{}]".format(split_command[1]) + " = " + str(snol_vars[split_command[1]]))
        elif is_identifier_token(split_command[1]):
            snol_print(f"Error! [{split_command[1]}] is not defined!")
        else:
            snol_print(split_command[1])  # print literal
        print("\n")
        continue

    ops = {"+", "-", "*", "/", "%"}
    if split_command[0] in ops:
        snol_print("Unknown command! Does not match any valid command of the language.")
        print("\n")
        continue
    if len(split_command) >= 3 and split_command[1] in ops:
        _, error = evaluate_chain(split_command, snol_vars)
        if error:
            snol_print(error)
            print("\n")
        continue

    if split_command[0] in snol_vars or is_valid_var_name(split_command[0]):  # variable assignment/overwrite
        if len(split_command) >= 3 and split_command[1] == "=":
            if not is_valid_var_name(split_command[0]):
                snol_print("Error: invalid variable name")
                print("\n")
                continue
            rhs = split_command[2:]
            if len(rhs) == 1:
                token = rhs[0]
                value, error = parse_token(token, snol_vars, require_defined=True)
                if error:
                    snol_print(error)
                    print("\n")
                    continue
                snol_vars[split_command[0]] = value
            elif len(rhs) >= 3:
                result, error = evaluate_chain(rhs, snol_vars)
                if error:
                    snol_print(error)
                    print("\n")
                    continue

                snol_vars[split_command[0]] = result
            print("\n")
            continue
        else:
            snol_print("Unknown command! Does not match any valid command of the language.")
            print("\n")
            continue

    if split_command[0] not in {"BEG", "PRINT", "EXIT!"} and not (len(split_command) >= 3 and split_command[1] in ops):
        if not (split_command[0] in snol_vars or is_valid_var_name(split_command[0])):
            snol_print("Unknown command! Does not match any valid command of the language.")
    print("\n")
