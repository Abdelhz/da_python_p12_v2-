from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission
from django.db import transaction
from Client.models import Client

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from Client.models import Client
from CustomUser.models import CustomUserAccount

CLIENT_FIELDS = ['full_name', 'email', 'phone_number', 'company_name', 'address', 'contact_sales_EE', 'information']

CLIENT_DESCRIPTIONS = {
    'full_name': "Enter client's full name: ",
    'email': "Enter client's email: ",
    'phone_number': "Enter client's phone number: ",
    'company_name': "Enter client's company name: ",
    'address': "Enter client's address: ",
    'contact_sales_EE': "Enter Epic Events contact's username: ",
    'information': "Enter additional information: ",
}

class Command(BaseCommand):
    help = 'Command lines to manage CRUD operations on Clients from the Client model.'

    def add_arguments(self, parser):
        parser.add_argument('-list', action='store_true', help='List all clients')
        parser.add_argument('-create', action='store_true', help='Create a new client')
        parser.add_argument('-delete', action='store_true', help='Delete a client')
        parser.add_argument('-update', action='store_true', help='Update a client')
        parser.add_argument('-read', action='store_true', help='Read a client details')
        for field in CLIENT_FIELDS:
            parser.add_argument(field, nargs='?', type=str)

    def handle(self, *args, **options):
        if options['list']:
            self.list_clients()
        elif options['create']:
            self.create_client(options)
        elif options['delete']:
            self.delete_client(options)
        elif options['update']:
            self.update_client(options)
        elif options['read']:
            self.read_client(options)
        else:
            raise CommandError('Invalid command')

    def list_clients(self):
        try:
            clients = Client.objects.all()
            if not clients:
                self.stdout.write('No clients exist.')
            else:
                for client in clients:
                    self.stdout.write(f'Client Name: {client.full_name}, Email: {client.email}, Company Name: {client.company_name}')
        except Exception as e:
            self.stdout.write('An error occurred: {}'.format(e))

    def create_client(self, options):
        full_name = options['full_name'] or input(CLIENT_DESCRIPTIONS['full_name'])
        email = options['email'] or input(CLIENT_DESCRIPTIONS['email'])
        phone_number = options['phone_number'] or input(CLIENT_DESCRIPTIONS['phone_number'])
        company_name = options['company_name'] or input(CLIENT_DESCRIPTIONS['company_name'])
        address = options['address'] or input(CLIENT_DESCRIPTIONS['address'])
        contact_sales_EE_username = options['contact_sales_EE'] or input(CLIENT_DESCRIPTIONS['contact_sales_EE'])
        information = options['information'] or input(CLIENT_DESCRIPTIONS['information'])

        try:
            contact_sales_EE = CustomUserAccount.objects.get(username=contact_sales_EE_username)
        except CustomUserAccount.DoesNotExist:
            raise CommandError('Epic Events contact does not exist')

        try:
            with transaction.atomic():
                client = Client.objects.create_client(full_name, email, phone_number, company_name, address, contact_sales_EE, information)
                self.stdout.write(f'Successfully created client {client.full_name}')
        except Exception as e:
            raise CommandError(str(e))

    def delete_client(self, options):
        full_name = options['full_name'] or input('Enter full name of client to delete: ')
        try:
            client = Client.objects.get(full_name=full_name)
            client.delete()
            self.stdout.write(f'Successfully deleted client {full_name}')
        except Client.DoesNotExist:
            raise CommandError('Client does not exist')

    def update_client(self, options):
        full_name = options['full_name'] or input('Enter full name of client to update: ')
        try:
            client = Client.objects.get(full_name=full_name)
            with transaction.atomic():
                for field in ['email', 'phone_number', 'company_name', 'address', 'contact_sales_EE', 'information']:
                    value = options[field] or input(f'Enter new {field}: ')
                    if value: # Check if value is not an empty string
                        if field == 'contact_sales_EE':
                            try:
                                contact_sales_EE = CustomUserAccount.objects.get(username=value)
                            except CustomUserAccount.DoesNotExist:
                                raise CommandError(f'Epic Events contact {value} does not exist')
                            value = contact_sales_EE
                        setattr(client, field, value)
                client.save()
                self.stdout.write(f'Successfully updated client {client.full_name}')
        except Client.DoesNotExist:
            raise CommandError('Client does not exist')

    def read_client(self, options):
        full_name = options['full_name'] or input('Enter full name of client to read: ')
        try:
            client = Client.objects.get(full_name=full_name)
            client_info = f"Full Name: {client.full_name}\n, Email: {client.email}\n, Phone Number: {client.phone_number}\n, Company Name: {client.company_name}\n, Address: {client.address}\n, Epic Events Contact: {client.contact_sales_EE.username}\n, Information: {client.information}\n"
            self.stdout.write(client_info)
        except Client.DoesNotExist:
            raise CommandError('Client does not exist')