"""Script to create the FAISS vector index."""

from functions.index_utils import create_vector_index


def main() -> None:
    """Run the index creation process."""
    create_vector_index()


if __name__ == "__main__":
    main()
