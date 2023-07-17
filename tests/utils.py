import json
import os
from typing import Dict, Tuple


def get_dummy_search_data() -> Tuple[Dict, bytes]:
    """
    Load dummy search data
    """
    data = _read_data_from_file("search_item_dummy")
    return (
        data,
        f"""
             <script type="application/json" data-js-react-on-rails-store="MainStore">
            {{
                "items": {{
                    "catalogItems": {{
                        "byId": {{
                            "dummyId": {json.dumps(data)}
                        }}
                    }}
                }}
            }}
            </script>
""".encode(),
    )


def get_dummy_item_data() -> Tuple[Dict, bytes]:
    """
    Load dummy item data
    """
    data = _read_data_from_file("item_dummy")
    return (
        data,
        f"""
         <script type="application/json" data-component-name="ItemDetails">
        {{
            "item": {json.dumps(data)}
        }}
        </script>
""".encode(),
    )


def get_empty_data() -> bytes:
    """
    Get an empty HTML where no data can be scraped
    """
    return "<html><body><script><!-- --></script></body></html>".encode()


def _read_data_from_file(filename: str) -> Dict:
    """
    Read the test item from the samples' folder.
    """
    root_dir = os.getcwd()
    # Test are supposed to run from the makefile on the repository root.
    # `FROM_ROOT` is an env variable that I inject to understand if I have to apply this fix or not.
    if not os.getenv("FROM_ROOT", False):
        # If you run it from the `/test` folder I need to add `/../` to the path.
        root_dir = os.path.join(root_dir, "..")
    with open(
        os.path.join(root_dir, "tests", "samples", f"{filename}.json"), "r"
    ) as file:
        return json.load(file)
