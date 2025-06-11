"""Entry point to create the index and start the chatbot sequentially."""

from scripts.create_index import main as create_index
from scripts.chatbot import main as run_chatbot


def main() -> None:
    """Run index creation then launch the chatbot."""
    create_index()
    run_chatbot()


if __name__ == "__main__":
    main()
