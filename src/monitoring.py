from datetime import datetime
from pathlib import Path

import pandas as pd


REPORTS_DIR = Path("reports")
RUN_HISTORY_FILE = REPORTS_DIR / "pipeline_run_history.csv"


def save_pipeline_run(
    status: str,
    age_rows: int,
    race_rows: int,
    duration_seconds: float,
    error_message: str = "",
) -> None:
    """
    Append one ETL execution record to the pipeline history file.
    """

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    run_record = pd.DataFrame(
        [
            {
                "run_time": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "status": status,
                "age_rows": age_rows,
                "race_rows": race_rows,
                "duration_seconds": round(
                    duration_seconds,
                    2,
                ),
                "error_message": error_message,
            }
        ]
    )

    if RUN_HISTORY_FILE.exists():
        run_record.to_csv(
            RUN_HISTORY_FILE,
            mode="a",
            header=False,
            index=False,
        )
    else:
        run_record.to_csv(
            RUN_HISTORY_FILE,
            index=False,
        )