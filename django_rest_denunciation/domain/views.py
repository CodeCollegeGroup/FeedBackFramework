from smtplib import SMTPException
from django.urls import reverse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Domain, DomainAdministrator
from .serializers import DomainSerializer, DomainAdministratorSerializer


class DomainViewSet(viewsets.ModelViewSet):

    serializer_class = DomainSerializer
    queryset = Domain.objects.all()

    def create(self, request, *args, **kwargs):
        data = request.data.dict()
        username = data.pop('username')
        data['administrator'] = self._get_admin_pk(username)

        serialized_data = self.serializer_class(data=data)

        try:
            serialized_data.is_valid(raise_exception=True)
        except serializers.ValidationError:
            return Response(serialized_data.errors,
                            status.HTTP_400_BAD_REQUEST)

        serialized_data.save()
        # self._send_key_by_email(data.application_name)

        return Response({'ok': 'Domain registered!'})

    @staticmethod
    def _send_key_by_email(application_name):
        domain = Domain.objects.get(application_name=application_name)

        message = """Olá, obrigado por registrar um
                     domínio em nossa plataforma\n
                     A chave do seu domínio '{}' é\n
                     Chave: {}""".format(domain.uri, domain.key)

        admin = domain.administrator
        admin.send_email('Domínio registrado!', message)

    @staticmethod
    def _get_admin_pk(username):
        admin = get_object_or_404(DomainAdministrator, username=username)
        admin_url = reverse(
            'domainadministrator-detail',
            kwargs=dict(pk=admin.pk)
        )

        return admin_url


class DomainAdministratorViewSet(viewsets.ModelViewSet):

    serializer_class = DomainAdministratorSerializer
    queryset = DomainAdministrator.objects.all()

    @action(methods=['put'], detail=False)
    def reset_password(self, request):  # pylint: disable=no-self-use
        """Reset password sending in e-mail"""

        data = request.data
        try:
            user = get_object_or_404(
                DomainAdministrator,
                email=data.get('email'),
            )
            user.recover_password()
        except SMTPException:
            return Response(
                {'detail': 'error while sending email'},
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return Response({'ok': 'password reseted'}, status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def recover_domain_key(self, request):  # pylint: disable=no-self-use
        """Send Domain key to the domain administrator"""

        data = request.query_params.copy()
        try:
            domain = get_object_or_404(
                Domain,
                application_name=data.get('application_name')
            )
            admin = domain.administrator
            message = """Olá,\nA chave do seu domínio '{}' é\n
                         Chave: {}""".format(domain.uri, domain.key)
            admin.send_email(
                'Equipe Django Rest Denunciation',
                message
            )
        except SMTPException:
            return Response(
                {'detail': 'error while sending email'},
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return Response({'ok': 'domain key recovered'}, status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = request.data
        serialized_data = self.serializer_class(data=data)

        try:
            serialized_data.is_valid(raise_exception=True)
        except serializers.ValidationError:
            return Response(serialized_data.errors,
                            status.HTTP_400_BAD_REQUEST)

        admin = DomainAdministrator.objects.create_user(
            username=data.pop('username'),
            password=data.pop('password'),
        )
        serialized_data.update(validated_data=data, instance=admin)

        return Response({'ok': 'administrator registered'},
                        status.HTTP_200_OK)
