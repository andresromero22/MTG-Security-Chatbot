"""Entry point to launch the interactive chatbot."""

from functions.chat_utils import build_chat_chain, chat_loop


def main() -> None:
    """Create the chat chain and start the chat loop."""
    chain = build_chat_chain()
    chat_loop(chain)


if __name__ == "__main__":
    main()
