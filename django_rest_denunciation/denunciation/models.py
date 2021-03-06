from singleton_model import SingletonModel
from django.db import models
from domain.models import Domain


GRAVITY_MAP = {
    'High': 2,
    'Medium': 1,
    'Low': 0
}


def map_gravity(gravity):
    if gravity in ('High', 'Medium', 'Low'):
        gravity = GRAVITY_MAP[gravity]
    elif gravity in (0, 1, 2):
        pass
    else:
        raise Exception('Gravity can only be 0, 1 or 2 on db')

    return gravity


class DenunciationState(SingletonModel):

    name = models.CharField(max_length=100)

    _not_implemented_exception = NotImplementedError(
        'This method must be implemented at all children classes'
    )

    def specific_delete(self):
        raise self._not_implemented_exception

    def specific_notify_denunciator(self):
        raise self._not_implemented_exception

    def save(self, *args, **kwargs):  # pylint: disable=arguments-differ
        self.name = self.__class__.__name__.lower()
        super(DenunciationState, self).save(*args, **kwargs)


class DenunciationStateNotImplementedYet(DenunciationState):

    def specific_delete(self):
        pass

    def specific_notify_denunciator(self):
        pass


class NullState(DenunciationState):

    # Exceptions to detect if void methods are being called
    def specific_delete(self):
        raise Exception('Specific deletion')

    def specific_notify_denunciator(self):
        raise Exception('Specific notifier')


class EvaluatingState(DenunciationStateNotImplementedYet):
    pass


class WaitingState(DenunciationStateNotImplementedYet):
    pass


class DoneState(DenunciationStateNotImplementedYet):
    pass


class Denunciable(models.Model):

    denunciable_id = models.IntegerField(default=0)

    denunciable_type = models.CharField(
        max_length=100,
        help_text='Determines the type of the denunciable'
        )

    denunciable_datetime = models.DateTimeField(
        auto_now_add=True,
        help_text='Date which the denounciable has been made'
        )

    class Meta:
        unique_together = (("denunciable_id", "denunciable_type"),)


class Denouncer(models.Model):

    email = models.CharField(max_length=100, unique=True)

    fake_denunciation = models.IntegerField(default=0)


class DenunciationCategory(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text='Name of the denunciation\'s category'
    )

    gravity = models.PositiveIntegerField(
        help_text='An integer value qualifying \
        the gravity of the denunciation'
    )

    def save(self, *args, **kwargs):  # pylint: disable=arguments-differ
        self.gravity = map_gravity(self.gravity)

        super(DenunciationCategory, self).save(*args, **kwargs)


class Denunciation(models.Model):

    denunciable = models.ForeignKey(
        'Denunciable',
        on_delete=models.CASCADE,
        help_text='Denunciable related to the denounce.',
        related_name='denunciation'
    )

    current_state = models.ForeignKey(
        'DenunciationState',
        on_delete=models.CASCADE,
        null=True,
        help_text='The current state of the denunciation.'
        'it could be Null, Wainting, Evaluating and done.'
    )

    categories = models.ManyToManyField(
        'DenunciationCategory',
        help_text='The categories applied to the denunciation.'
    )

    domain = models.ForeignKey(
        Domain,
        on_delete=models.SET_NULL,
        null=True,
        help_text='The client\'s domain.'
    )

    justification = models.CharField(
        max_length=500,
        help_text='A brief text describing why'
        'the denunciation has been made.'
    )

    created_at = models.DateField(
        auto_now_add=True,
        help_text='The date in which the denunciation has been made.'
    )

    gravity = models.IntegerField(
        editable=False,
        help_text='A integer that qualifies the gravity'
        'of the denunciation. it could be:0,1,2.'
    )

    _initial_state = WaitingState

    domain = models.ForeignKey(Domain, on_delete=models.SET_NULL, null=True)

    denunciable = models.ForeignKey(
        'Denunciable',
        related_name='denunciations',
        on_delete=models.CASCADE
    )

    denouncer = models.ForeignKey(
        'Denouncer',
        related_name='denunciations',
        on_delete=models.CASCADE,
        null=True
    )

    evaluation = models.CharField(max_length=500, default='')

    fake = models.BooleanField(default=False)

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

        if self.id:
            categories_gravities = [category.gravity for category in
                                    self.categories.all()]
            categories_gravities += [0]
        else:
            categories_gravities = [0]
        self.gravity = max(categories_gravities)

        super(Denunciation, self).save(*args, **kwargs)
