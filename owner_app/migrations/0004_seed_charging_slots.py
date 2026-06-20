from django.db import migrations


SLOTS = [
    (201, 'Slot 1', '06:00 AM', '07:00 AM'),
    (202, 'Slot 2', '07:00 AM', '08:00 AM'),
    (203, 'Slot 3', '08:00 AM', '09:00 AM'),
    (204, 'Slot 4', '09:00 AM', '10:00 AM'),
    (205, 'Slot 5', '10:00 AM', '11:00 AM'),
    (206, 'Slot 6', '11:00 AM', '12:00 PM'),
    (207, 'Slot 7', '12:00 PM', '01:00 PM'),
    (208, 'Slot 8', '01:00 PM', '02:00 PM'),
    (209, 'Slot 9', '02:00 PM', '03:00 PM'),
    (210, 'Slot 10', '03:00 PM', '04:00 PM'),
    (211, 'Slot 11', '04:00 PM', '05:00 PM'),
    (212, 'Slot 12', '05:00 PM', '06:00 PM'),
    (213, 'Slot 13', '06:00 PM', '07:00 PM'),
    (214, 'Slot 14', '07:00 PM', '08:00 PM'),
    (215, 'Slot 15', '08:00 PM', '09:00 PM'),
    (216, 'Slot 16', '09:00 PM', '10:00 PM'),
    (217, 'Slot 17', '10:00 PM', '11:00 PM'),
    (218, 'Slot 18', '11:00 PM', '12:00 AM'),
    (219, 'Slot 19', '12:00 AM', '01:00 AM'),
    (220, 'Slot 20', '01:00 AM', '02:00 AM'),
    (221, 'Slot 21', '02:00 AM', '03:00 AM'),
    (222, 'Slot 22', '03:00 AM', '04:00 AM'),
    (223, 'Slot 23', '04:00 AM', '05:00 AM'),
    (224, 'Slot 24', '05:00 AM', '06:00 AM'),
]


def seed_slots(apps, schema_editor):
    ChargingSlot = apps.get_model('owner_app', 'chargingslot')
    for slot_id, name, start, end in SLOTS:
        ChargingSlot.objects.update_or_create(
            slot_id=slot_id,
            defaults={'slot_name': name, 'start_time': start, 'end_time': end},
        )


class Migration(migrations.Migration):
    dependencies = [('owner_app', '0003_evstation_operational_status_and_more')]
    operations = [migrations.RunPython(seed_slots, migrations.RunPython.noop)]
