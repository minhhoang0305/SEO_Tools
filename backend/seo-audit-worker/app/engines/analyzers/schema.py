import json
from bs4 import BeautifulSoup
def analyze_schema(
    html: str
):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    schemas = []

    scripts = soup.find_all(
        "script",
        attrs={
            "type":
            "application/ld+json"
        }
    )

    for script in scripts:

        try:

            data = json.loads(
                script.text
            )

            schemas.append(
                data
            )

        except Exception:

            pass

    schema_types = []

    for schema in schemas:

        if "@type" in schema:

            schema_types.append(
                schema["@type"]
            )

        if "@graph" in schema:

            for item in schema["@graph"]:

                if "@type" in item:

                    schema_types.append(
                        item["@type"]
                    )

    return {
        "count": len(
            schema_types
        ),
        "types": schema_types
    }