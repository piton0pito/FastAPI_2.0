import pyjokes

def generate_random_joke(language='ru'):
    joke = pyjokes.get_joke(language=language)
    print(joke)

def generate_multiple_jokes(count=1, language='ru'):
    jokes = pyjokes.get_jokes(count=count, language=language)
    for joke in jokes:
        print(joke)
        print('-' * 30)

def main():
    print("Welcome to the Joke Generator!")
    print("Choose an option:")
    print("1. Generate a random joke")
    print("2. Generate multiple jokes")
    choice = input("Enter your choice (1/2): ")

    if choice == '1':
        language = input("Enter the language code (default: en): ")
        generate_random_joke(language)
    elif choice == '2':
        count = int(input("Enter the number of jokes to generate: "))
        language = input("Enter the language code (default: en): ")
        generate_multiple_jokes(count, language)
    else:
        print("Invalid choice. Exiting...")
