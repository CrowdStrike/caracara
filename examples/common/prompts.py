"""
Caracara Example Collection.

This file contains a pretty prompt_toolkit-based completer for devices.
"""
from typing import Dict, Iterable

from prompt_toolkit import prompt
from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document


class PrettyCompleter(Completer):
    """Prompt Toolkit Completer that provides a searchable list of items."""

    def __init__(self, data_dict: Dict[str, Dict]):
        """Create a new completer based on a dictionary that maps items to meta strings.

        Each item should be in the format:
        {
            "id1": "label",
            "id2": "label2",
            etc.
        }
        """
        self.data_dict = data_dict

    def get_completions(
        self,
        document: Document,
        complete_event: CompleteEvent,
    ) -> Iterable[Completion]:
        """Yield items that match the entered search string."""
        for item_id, item_label in self.data_dict.items():
            word_lower = document.current_line.lower()
            if word_lower in item_id.lower() or word_lower in item_label.lower():
                yield Completion(
                    item_id,
                    start_position=-len(document.current_line),
                    display=item_id,
                    display_meta=item_label,
                )


def choose_item(items: Dict[str, Dict], prompt_text="Item Search") -> str:
    """Visually choose an item ID from a dict of IDs mapped to strings."""
    completer = PrettyCompleter(data_dict=items)
    chosen_id = None
    while chosen_id not in items:
        chosen_id = prompt(f"{prompt_text} >", completer=completer)

    print(chosen_id)
    return chosen_id
