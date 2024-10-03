import random

from datasets import load_dataset

persona_dataset = None
persona_length = None
"""
personas.py

this file loads persona data from huggingface. The personas are randomly selected and used in prompt generation.
"""


def load_persona_dataset():
    global persona_dataset, persona_length
    if persona_dataset is None:
        ds = load_dataset(
            "sasuke-uchiha-13/phub", "persona", split="train", streaming=False
        )
        persona_dataset = list(ds)
    persona_length = len(persona_dataset)
    # print(persona_dataset["persona"][0], persona_length)
    return list(persona_dataset)


def get_random_persona():
    """
    Return a random persona from the given persona dataset as a string.

    Returns:
        str: A randomly selected persona as a string of traits.
    """
    global persona_dataset, persona_length

    if persona_dataset is None or persona_length is None:
        raise ValueError("Persona dataset not loaded.")

    random_index = random.randint(0, persona_length - 1)

    persona = persona_dataset[random_index]

    return persona["persona"]


# # main function for testing
# async def main():
#     # load persona dataset then print a random persona
#     load_persona_dataset()
#     random_persona = get_random_persona()
#     print("Random Persona:", random_persona)
#     # print(random_persona)


# if __name__ == "__main__":
#     import asyncio

#     asyncio.run(main())
