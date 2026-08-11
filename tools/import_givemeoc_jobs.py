from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.manager import db_manager
from app.services.givemeoc_scraper import crawl_givemeoc
from app.services.recruitment import RecruitmentService


def main() -> None:
    parser = argparse.ArgumentParser(description="Import GivemeOC recruitment jobs.")
    parser.add_argument("--pages", type=int, default=30, help="How many pages to crawl.")
    parser.add_argument("--start-page", type=int, default=1, help="First page number.")
    parser.add_argument(
        "--delay",
        type=float,
        default=None,
        help="Seconds to wait between requests. Defaults to .env setting.",
    )
    args = parser.parse_args()

    db_manager.init_db()
    jobs = crawl_givemeoc(
        start_page=args.start_page,
        pages=args.pages,
        delay_seconds=args.delay,
    )
    created, updated = RecruitmentService.import_jobs(jobs)

    print(
        f"Fetched {args.pages} pages, parsed {len(jobs)} jobs, "
        f"created {created}, updated {updated}."
    )


if __name__ == "__main__":
    main()
