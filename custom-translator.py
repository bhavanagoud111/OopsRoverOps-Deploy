import ast

# Define translation rules for each target language
translation_rules = {
    "JavaScript": {
        "print": "console.log",
        "def": "function",
        "for": "for",
        "if": "if",
        "else": "else",
        "range": "Array.from(Array",
        "True": "true",
        "False": "false",
    },
    "C": {
        "print": "printf",
        "def": "void",
        "for": "for",
        "if": "if",
        "else": "else",
        "range": "for (int i = 0; i <",
        "True": "1",
        "False": "0",
    },
    "C++": {
        "print": "std::cout",
        "def": "void",
        "for": "for",
        "if": "if",
        "else": "else",
        "range": "for (int i = 0; i <",
        "True": "true",
        "False": "false",
    },
    "Java": {
        "print": "System.out.println",
        "def": "public static void",
        "for": "for",
        "if": "if",
        "else": "else",
        "range": "for (int i = 0; i <",
        "True": "true",
        "False": "false",
    },
}

# Function to translate Python code to the target language
def translate_python_to_target(python_code, target_lang):
    rules = translation_rules.get(target_lang)
    if not rules:
        raise ValueError(f"Unsupported target language: {target_lang}")

    # Parse the Python code into an AST
    try:
        tree = ast.parse(python_code)
    except SyntaxError:
        raise ValueError("Invalid Python code")

    # Function to recursively translate nodes
    def translate_node(node):
        if isinstance(node, ast.FunctionDef):
            # Translate function definitions
            if target_lang == "Java":
                return f"{rules['def']} {node.name}({', '.join('String ' + arg.arg for arg in node.args.args)}) {{"
            else:
                return f"{rules['def']} {node.name}({', '.join(arg.arg for arg in node.args.args)}) {{"
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            # Translate function calls (e.g., print)
            if node.func.id in rules:
                args = ", ".join(translate_node(arg) for arg in node.args)
                if target_lang == "C":
                    return f'{rules[node.func.id]}("{args}\\n");'
                elif target_lang == "C++":
                    return f'{rules[node.func.id]} << "{args}" << std::endl;'
                else:
                    return f"{rules[node.func.id]}({args});"
        elif isinstance(node, ast.For):
            # Translate for loops
            target = translate_node(node.target)
            iterable = translate_node(node.iter)
            if target_lang in ["C", "C++", "Java"]:
                return f"{rules['for']} {iterable}; i++) {{"
            else:
                return f"{rules['for']} ({target} of {iterable}) {{"
        elif isinstance(node, ast.If):
            # Translate if statements
            condition = translate_node(node.test)
            return f"{rules['if']} ({condition}) {{"
        elif isinstance(node, ast.Expr):
            # Translate expressions
            return translate_node(node.value) + ";"
        elif isinstance(node, ast.Constant):
            # Translate constants (e.g., strings, numbers)
            return str(node.value)
        elif isinstance(node, ast.Name):
            # Translate variable names
            return rules.get(node.id, node.id)
        else:
            # Default case: return the unparsed node
            return ast.unparse(node)

    # Translate the AST into target code
    translated_code = []
    for node in ast.walk(tree):
        translated_code.append(translate_node(node))
    return "\n".join(translated_code)

# Main function to run the translator
def main():
    print("Python Code Translator")
    print("Supported Target Languages: JavaScript, C, C++, Java")

    # Get user input
    target_lang = input("Enter target language (JavaScript/C/C++/Java): ").strip()
    python_code = input("Enter Python code:\n")

    # Translate the code
    try:
        translated_code = translate_python_to_target(python_code, target_lang)
        print("\nTranslated Code:\n")
        print(translated_code)
    except Exception as e:
        print(f"Error: {e}")

# Run the program
if __name__ == "__main__":
    main()