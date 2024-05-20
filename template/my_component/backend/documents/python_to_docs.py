def python_to_docs(filepath):
    with open(filepath, "r") as f:
        file_content = f.read()

    docs = []
    start_index = 0
    while start_index != -1:
        found_index = file_content.find("def ", start_index)
        if found_index > -1:
            next_found_index = file_content.find("def ", found_index + 1)
        else:
            next_found_index = -1

        if next_found_index > -1:
            docs.append(file_content[found_index:next_found_index].strip())
        elif found_index > -1:
            docs.append(file_content[found_index:].strip())

        start_index = next_found_index

    return docs
