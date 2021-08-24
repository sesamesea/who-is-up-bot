import yeelight
from yeelight import transitions

import config


Color = tuple[int, int, int]
_BULB = yeelight.Bulb(config.BULB_IP)


def _flash(color: Color, pulses: int) -> None:
    transition = transitions.pulse(*color)

    if _BULB.get_properties().get('power', 'off') == 'off':
        action = yeelight.Flow.actions.off
    else:
        action = yeelight.Flow.actions.recover

    _BULB.start_flow(
        yeelight.Flow(count=pulses, action=action, transitions=transition)
    )


def notify(color: Color):
    try:
        _flash(color, config.PULSES)
    except yeelight.BulbException:
        pass
