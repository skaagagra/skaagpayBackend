from django.test import TestCase
from authentication.models import User
from .models import Wallet, Transaction
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal

class WalletTransferTests(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(phone_number='1111111111', full_name='Sender')
        self.sender.custom_user_id = 'sender@skaag'
        self.sender.save()
        self.sender_wallet = Wallet.objects.create(user=self.sender, balance=1000.00)

        self.recipient = User.objects.create_user(phone_number='2222222222', full_name='Recipient')
        self.recipient.custom_user_id = 'recipient@skaag'
        self.recipient.save()
        self.recipient_wallet = Wallet.objects.create(user=self.recipient, balance=0.00)

        self.client = APIClient()

    def test_successful_transfer(self):
        url = '/api/wallet/transfer/'
        data = {
            'recipient_id': 'recipient@skaag',
            'amount': 100.00,
            'description': 'Test Transfer'
        }
        
        # Simulate Authentication by setting header
        response = self.client.post(url, data, format='json', **{'HTTP_X_USER_ID': self.sender.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.sender_wallet.refresh_from_db()
        self.recipient_wallet.refresh_from_db()
        
        self.assertEqual(self.sender_wallet.balance, Decimal('900.00'))
        self.assertEqual(self.recipient_wallet.balance, Decimal('100.00'))
        
        # Check Transactions
        self.assertTrue(Transaction.objects.filter(wallet=self.sender_wallet, transaction_type='TRANSFER_SENT').exists())
        self.assertTrue(Transaction.objects.filter(wallet=self.recipient_wallet, transaction_type='TRANSFER_RECEIVED').exists())

    def test_insufficient_balance(self):
        url = '/api/wallet/transfer/'
        data = {
            'recipient_id': 'recipient@skaag',
            'amount': 2000.00,
            'description': 'Too much'
        }
        response = self.client.post(url, data, format='json', **{'HTTP_X_USER_ID': self.sender.id})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Insufficient balance', str(response.data))

    def test_invalid_recipient(self):
        url = '/api/wallet/transfer/'
        data = {
            'recipient_id': 'wrong@skaag',
            'amount': 10.00,
        }
        response = self.client.post(url, data, format='json', **{'HTTP_X_USER_ID': self.sender.id})
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_self_transfer(self):
        url = '/api/wallet/transfer/'
        data = {
            'recipient_id': 'sender@skaag',
            'amount': 10.00,
        }
        response = self.client.post(url, data, format='json', **{'HTTP_X_USER_ID': self.sender.id})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
