import logging

from django.core.management import BaseCommand

from common.data.tags import FINANCE, HOBBIES, PERSONAL, TECH, CLUB
from users.models.tags import Tag

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Reads tags from data files and upserts them into the database"

    def handle(self, *args, **options):
        update_tag_group(Tag.GROUP_FINANCE, FINANCE)
        self.stdout.write(f"{len(FINANCE)} finance")

        update_tag_group(Tag.GROUP_HOBBIES, HOBBIES)
        self.stdout.write(f"{len(HOBBIES)} hobbies")

        update_tag_group(Tag.GROUP_PERSONAL, PERSONAL)
        self.stdout.write(f"{len(PERSONAL)} personal")

        update_tag_group(Tag.GROUP_TECH, TECH)
        self.stdout.write(f"{len(TECH)} tech")

        update_tag_group(Tag.GROUP_CLUB, CLUB)
        self.stdout.write(f"{len(CLUB)} club")

        all_tag_keys = list(dict(FINANCE).keys()) \
            + list(dict(HOBBIES).keys()) \
            + list(dict(PERSONAL).keys()) \
            + list(dict(TECH).keys()) \
            + list(dict(CLUB).keys())
        Tag.objects.exclude(code__in=all_tag_keys).delete()

        self.stdout.write("Done 🥙")


def update_tag_group(group, tag_list):
    for index, (tag_code, tag_name) in enumerate(tag_list):
        Tag.objects.update_or_create(
            code=tag_code,
            defaults=dict(
                group=group,
                name=tag_name,
                index=index,
            )
        )
