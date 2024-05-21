import re


def _extract_function_name(code_string):
    """Extracts the name of a function from a code string.

    Args:
        code_string: A string containing the code to extract the function name from.

    Returns:
    The name of the function, or None if no function name is found.
    """
    pattern = re.compile(r"def\s+(\w+)\s*\(")
    match = pattern.search(code_string)
    if match:
        return match.group(1)
    else:
        return None


def extract_function_names(docs):
    extracted = [_extract_function_name(doc) for doc in docs]
    return [ex for ex in extracted if ex is not None]
