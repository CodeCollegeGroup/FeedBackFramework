from hashlib import sha256
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.mail import EmailMessage


KEY_LENGTH = 64  # 256 bits in hexadecimal


class DomainAdministrator(User):

    def recover_password(self):
        """
        Reset password sending in e-mail
        """

        random_password = DomainAdministrator.objects.make_random_password()
        self.set_password(random_password)
        self.save()

        # message = """Olá,\nSua senha foi resetada, acesse
        #              a plataforma e troque a senha.\n
        #              Sua nova senha é:\n {}""".format(random_password)
        # self.send_email('Password Reset', message)

    def retrieve_denunciation_by_priority(self, priority_type=None):
        pass

    def send_email(self, title, message):
        email = EmailMessage(title, message, to=[self.email])
        email.send()


class Domain(models.Model):

    administrator = models.ForeignKey(
        'DomainAdministrator',
        on_delete=models.CASCADE,
        help_text='Refers to the administrator of the domain'
    )

    application_name = models.CharField(
        max_length=50,
        unique=True,
        help_text='Refers to the name of the application'
    )

    key = models.CharField(
        max_length=KEY_LENGTH,
        unique=True,
        editable=False,
        help_text='Refers to the key of the domain'
    )

    uri = models.URLField(
        max_length=150,
        help_text='Refers to the url of the domain')

    def __str__(self):
        return self.uri

    def save(self, *args, **kwargs):  # pylint: disable=arguments-differ
        self.key = self.generate_key()
        super(Domain, self).save(*args, **kwargs)

    def generate_key(self):
        return self._generate_key(
            self.application_name,
            self.administrator.id
        )

    @staticmethod
    def _generate_key(string, integer):
        microseconds = timezone.now().microsecond
        local_hash = abs(hash(string))

        key_seed = map(
            lambda c: str((ord(c)*microseconds)//integer + local_hash),
            list(string)
        )
        key_seed = '@'.join(key_seed)

        hash_obj = sha256(key_seed.encode())
        key = hash_obj.hexdigest()

        return key
