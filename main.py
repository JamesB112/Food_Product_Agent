from agent import food_health_agent

def run_local():
    print("\n🧪 Food Health Agent — Local Debug Mode")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        try:
            response = food_health_agent.run_sync(user_input)
            print(f"\n🔍 Agent Response:\n{response.text}\n")
        except Exception as e:
            print(f"\n❌ Error running agent: {e}\n")

if __name__ == "__main__":
    run_local()
