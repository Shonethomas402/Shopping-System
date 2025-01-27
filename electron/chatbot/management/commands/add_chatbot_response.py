from django.core.management.base import BaseCommand
from chatbot.models import ChatbotResponse

class Command(BaseCommand):
    help = 'Add a new chatbot response'

    def add_arguments(self, parser):
        parser.add_argument('query', type=str)
        parser.add_argument('response', type=str)

    def handle(self, *args, **options):
        query = options['query']
        response = options['response']

        ChatbotResponse.objects.create(
            query=query,
            response=response
        )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully added response for query: {query}')
        ) 