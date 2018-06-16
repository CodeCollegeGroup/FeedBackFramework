from singleton_model import SingletonModel
from django.db import models


class DenunciationState(SingletonModel):

    _not_implemented_exception = NotImplementedError(
        'This method must be implemented at all children classes'
    )

    def specific_delete(self):
        raise self._not_implemented_exception

    def specific_notify_denunciator(self):
        raise self._not_implemented_exception


class NullState(DenunciationState):

    # Exceptions to detect if void methods are being called
    def specific_delete(self):
        raise Exception('Specific deletion')

    def specific_notify_denunciator(self):
        raise Exception('Specific notifier')


class EvaluatingState(DenunciationState):

    def specific_delete(self):
        pass

    def specific_notify_denunciator(self):
        pass


class WaitingState(DenunciationState):

    def specific_delete(self):
        pass

    def specific_notify_denunciator(self):
        pass


class DoneState(DenunciationState):

    def specific_delete(self):
        pass

    def specific_notify_denunciator(self):
        pass


class Denunciable(models.Model):

    denunciable_id = models.IntegerField(default=0)

    denunciable_type = models.CharField(max_length=500, default='')

    denunciable_datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("denunciable_id", "denunciable_type"),)


class Denouncer(models.Model):

    email = models.CharField(max_length=100, primary_key=True)

    fake_denunciation = models.IntegerField(default=0)


class Denunciation(models.Model):

    categories = models.ManyToManyField('DenunciationCategory')

    justification = models.CharField(max_length=500, default='')

    current_state = models.ForeignKey(
        'DenunciationState',
        related_name='denunciations',
        on_delete=models.CASCADE
    )

    _initial_state = WaitingState

    denunciable = models.ForeignKey(
        'Denunciable',
        related_name='denunciations',
        on_delete=models.CASCADE
    )

    denouncer = models.ForeignKey(
        'Denouncer',
        related_name='denunciations',
        on_delete=models.CASCADE,
        default=0
    )

    def delete_denunciation(self):
        self.current_state.specific_delete()

    def notify_denunciator(self):
        self.current_state.specific_notify_denunciator()

    def set_state(self, state):
        self.current_state = state

        if not isinstance(state, NullState):
            self.notify_denunciator()

    def __str__(self):
        return self.justification

    def save(self, *args, **kwargs):
        # pylint: disable=arguments-differ
        initial_state = self._initial_state.objects.create()
        self.current_state = initial_state

        super(Denunciation, self).save(*args, **kwargs)


class DenunciationCategory(models.Model):

    name = models.CharField(max_length=100, unique=True)

    GRAVITY_CHOICES = (
        ('High', 'H'),
        ('Medium', 'M'),
        ('Low', 'L')
    )

    gravity = models.CharField(
        max_length=10,
        choices=GRAVITY_CHOICES,
    )
