from collections.abc import Sequence
from typing import Any

import numpy as np
from Orange.data import ContinuousVariable, Domain, StringVariable, Table


def create_orange_datatable(
    rows:Sequence[dict[str,Any]],
    columns:Sequence[str]
)-> Table | None:
    """Build an Orange datatable from a list of row dicts and columns order.

    Columns types are inferred from the first row's item. Numeric instances excluding
    bools become ContinuousVariable, everything else is considered StringVariable.

    Args:
        rows: The row dicts to convert
        columns: The explicit list of keys to extract from each row

    Returns:
        Optional[Table]: None if rows empty, the built Table otherwise
    """
    if not rows:
        return None

    metas = []
    for col in columns :
        first_value = rows[0][col]
        if isinstance(first_value, (float, int)) and not isinstance(first_value, bool):
            metas.append(ContinuousVariable(col))
        else:
            metas.append(StringVariable(col))

    # Domain creation
    domain = Domain(attributes=[], metas=metas)

    # Table creation
    metas_array = np.array(
        [[row[col] for col in columns] for row in rows],
        dtype=object,
    )
    return Table.from_numpy(domain, X=np.empty((len(rows), 0)), metas=metas_array)
