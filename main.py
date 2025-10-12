from workflows.workflow_implementation import workflow

if __name__ == "__main__":
    while True:
        user_input = input("What analysis do you need? (type 'exit' to quit) ")
        if user_input.lower() == "exit":
            break
        workflow.print_response(user_input, markdown=True)
