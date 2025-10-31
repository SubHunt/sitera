from django.core.management.base import BaseCommand
from apps.catalog.models import Category
import os


class Command(BaseCommand):
    help = 'Update category images from static/images/categories folder'

    def handle(self, *args, **options):
        # Mapping of category slugs to image filenames
        category_image_mapping = {
            'konferents-sistemy': 'conference-systems.svg',
            'sistemy-sinhronnogo-perevoda': 'sync-translation.svg',
            'oborudovanie-dlya-videokonferentssvyazi': 'video-conference.svg',
            'mikrofonnye-sistemy-i-mikrofony': 'microphones.svg',
            'naushniki': 'headphones.svg',
            'oborudovanie-zukousileniya': 'sound-amplification.svg',
            'professionalnye-displei': 'professional-displays.svg',
            'svetodiodnye-ekrany': 'led-screens.svg',
            'proektory': 'projectors.svg',
            'interaktivnye-ustroistva': 'interactive-devices.svg',
            'sistemy-digital-signage': 'digital-signage.svg',
            'videokamery-i-ustroistva-zapisi': 'cameras.svg',
            'dokument-kamery': 'document-cameras.svg',
            'resheniya-dlya-peregovornykh-komnat': 'meeting-rooms.svg',
            'av-kommutatsiya': 'av-switching.svg',
            'oborudovanie-upravleniya': 'control-equipment.svg',
            'shou-oborudovanie': 'show-equipment.svg',
            'svetovoe-oborudovanie': 'lighting-equipment.svg',
            'stsenicheskie-spetseffekty': 'stage-effects.svg',
            'krepleniya': 'mounts.svg',
            'gotovye-komplekty-oborudovaniya': 'complete-kits.svg',
            'kabeli': 'cables.svg',
            'tribuny-i-rekovye-shkafy': 'podiums-racks.svg',
            'arkhivnye-modeli': 'archived-models.svg',
            # Additional mappings for remaining categories
            'videokonferentsterminaly': 'video-conference-terminals.svg',
            'vnutrennie-led-ekrany': 'indoor-led-screens.svg',
            'diskussionnye-sistemy': 'sound-systems.svg',
            'interaktivnye-paneli': 'interactive-panels.svg',
            'kamery-dlya-vks': 'conference-cameras.svg',
            'kontrollery-dlya-led': 'video-walls.svg',
            'meditsinskie-monitory': 'medical-monitors.svg',
            'monitory-dlya-videonablyudeniya': 'security-monitors.svg',
            'nastolnye-mikrofony': 'desktop-microphones.svg',
            'petlichnye-mikrofony': 'headset-microphones.svg',
            'resheniya-dlya-peregovornyh-komnat': 'meeting-rooms-small.svg',
            'ruchnye-mikrofony': 'handheld-microphones.svg',
            'sistemy-golosovaniya': 'audio-systems.svg',
            'ulichnye-led-ekrany': 'outdoor-led-screens.svg',
            'konferents-zaly': 'conference-halls.svg',
            'videosteny-i-mediafaksady': 'media-facades.svg',
        }

        updated_count = 0
        not_found_count = 0

        for category in Category.objects.all():
            if category.slug in category_image_mapping:
                image_filename = category_image_mapping[category.slug]
                image_path = f'categories/{image_filename}'

                # Update the category image
                category.image = image_path
                category.save()
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Updated image for category: {category.name} -> {image_path}')
                )
            else:
                not_found_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'No image mapping found for category: {category.name} (slug: {category.slug})')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {updated_count} categories with images.')
        )

        if not_found_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'No image mapping found for {not_found_count} categories.')
            )
