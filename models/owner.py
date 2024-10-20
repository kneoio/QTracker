import logging

logger = logging.getLogger(__name__)

class Owner:
    def __init__(self, telegram_name):
        self.telegram_name = telegram_name
        self.email = None
        self.whatsapp_name = None
        self.phone = None
        self.country = None
        self.currency = None
        self.birth_date = None
        self.localized_name = None

    @classmethod
    def from_response(cls, data):
        owner = cls(data['telegramName'])
        owner.email = data.get('email')
        owner.whatsapp_name = data.get('whatsappName')
        owner.phone = data.get('phone')
        owner.country = data.get('country')
        owner.currency = data.get('currency')
        owner.birth_date = data.get('birthDate')
        owner.localized_name = data.get('localizedName')
        return owner
