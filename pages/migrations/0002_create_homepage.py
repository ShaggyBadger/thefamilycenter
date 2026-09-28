from django.db import migrations


def create_homepage(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    Page = apps.get_model("wagtailcore", "Page")
    Locale = apps.get_model("wagtailcore", "Locale")
    Site = apps.get_model("wagtailcore", "Site")
    HomePage = apps.get_model("pages", "HomePage")
    EventsIndexPage = apps.get_model("events", "EventsIndexPage")

    generic_page_type = ContentType.objects.get(
        app_label="wagtailcore", model="page"
    )
    Page.objects.filter(
        content_type=generic_page_type,
        slug="home",
        depth=2,
    ).delete()

    homepage_content_type, _ = ContentType.objects.get_or_create(
        app_label="pages", model="homepage"
    )
    default_locale = Locale.objects.order_by("id").first()
    homepage = HomePage.objects.create(
        title="The Family Center",
        draft_title="The Family Center",
        slug="home",
        content_type=homepage_content_type,
        locale=default_locale,
        path="00010001",
        depth=2,
        numchild=1,
        url_path="/home/",
    )
    events_content_type, _ = ContentType.objects.get_or_create(
        app_label="events", model="eventsindexpage"
    )
    EventsIndexPage.objects.create(
        title="Events",
        draft_title="Events",
        slug="events",
        content_type=events_content_type,
        locale=default_locale,
        path="000100010001",
        depth=3,
        numchild=0,
        url_path="/home/events/",
        show_in_menus=True,
    )
    Site.objects.create(
        hostname="localhost",
        port=8000,
        root_page=homepage,
        is_default_site=True,
        site_name="The Family Center",
    )


def remove_homepage(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    HomePage = apps.get_model("pages", "HomePage")
    EventsIndexPage = apps.get_model("events", "EventsIndexPage")

    EventsIndexPage.objects.filter(path="000100010001").delete()
    HomePage.objects.filter(slug="home", depth=2).delete()
    ContentType.objects.filter(app_label="pages", model="homepage").delete()
    ContentType.objects.filter(app_label="events", model="eventsindexpage").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0001_initial"),
        ("events", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_homepage, remove_homepage),
    ]
