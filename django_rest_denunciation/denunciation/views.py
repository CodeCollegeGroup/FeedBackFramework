from rest_framework.views import APIView
from django.http import Http404
from rest_framework.response import Response
from denunciation.models import Denunciation, Denunciable, Denouncer
from json import loads
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.urls import reverse


class DenunciationList(APIView):

    # index
    def get(self, request, format=None):

        denunciations = Denunciation.objects.all()
        denunciations_dict_list = []

        for denunciation in denunciations:

            denunciable = Denunciable.objects.get(
                id=denunciation.denunciable.id
            )
            denunciation_dict = denunciation.__dict__

            url = reverse(
                'denunciation-detail',
                kwargs={'pk': denunciation.pk}
            )

            denunciation_dict.update(
                {'denunciable_id': denunciable.denunciable_id}
            )
            denunciation_dict.update(
                {'denunciable_type': denunciable.denunciable_type}
            )
            denunciation_dict.update(
                {'url': request.build_absolute_uri(url)}
            )

            del denunciation_dict['id']
            del denunciation_dict['_state']

            denunciations_dict_list.append(denunciation_dict)

        return Response(denunciations_dict_list)

    # create
    def post(self, request, format=None):

        response = Response()
        data = loads(request.body.decode())

        try:
            count = Denunciable.objects.filter(
                denunciable_id=data['denunciable_id']
            ).count()
            if count == 1:
                denunciable = Denunciable.objects.get(
                    denunciable_id=data['denunciable_id']
                )
            else:
                denunciable = Denunciable()
                denunciable.denunciable_id = data['denunciable_id']
                denunciable.denunciable_type = data['denunciable_type']
                denunciable.save()

            denouncer = Denouncer()
            denouncer.email = data['denouncer_id']
            denouncer.save()

            denunciation = Denunciation()
            denunciation.justification = data['justification']
            denunciation.denunciable = denunciable
            denunciation.denouncer = denouncer
            denunciation.save()

            response = Response(status=201)

        except ValidationError:
                response = Response(status=400)

        return response


class DenunciationDetails(APIView):

    def get_object(self, pk):

        try:
            return Denunciation.objects.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    # show
    def get(self, request, pk, format=None):

        denunciation = self.get_object(pk)

        denunciation_dic = denunciation.__dict__

        denunciable = Denunciable.objects.get(id=denunciation.denunciable.id)

        url = reverse(
            'denunciation-detail',
            kwargs={'pk': denunciation.pk}
        )

        denunciation_dic.update(
            {'denunciable_id': denunciable.denunciable_id}
        )
        denunciation_dic.update(
            {'denunciable_type': denunciable.denunciable_type}
        )
        denunciation_dic.update(
            {'url': request.build_absolute_uri(url)}
        )

        del denunciation_dic['id']
        del denunciation_dic['_state']

        return Response(denunciation_dic)

    # update
    def put(self, request, pk, format=None):

        denunciation = self.get_object(pk)
        denunciable = Denunciable.objects.get(id=denunciation.denunciable.id)
        response = Response()
        data = loads(request.body.decode())

        try:

            denunciation.justification = data['justification']
            denunciation.save()

            denunciable.denunciable_id = data['denunciable_id']
            denunciable.denunciable_type = data['denunciable_type']
            denunciable.save()

            response = Response(status=200)

        except ValidationError:

                response = Response(status=400)

        return response

    # delete
    def delete(self, request, pk, format=None):

        denunciation = self.get_object(pk)
        denunciation.delete()

        return Response(status=204)
