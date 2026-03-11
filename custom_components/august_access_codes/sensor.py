"""August Access Lock Codes Sensor."""

from collections.abc import Callable
import logging

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.core import HomeAssistant
import homeassistant.helpers.device_registry as dr
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import AugustAccessConfigEntry
from .const import AUGUST_DOMAIN, DOMAIN, YALE_BLE_DOMAIN
from .coordinator import AccessCodeCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: AugustAccessConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Setup the sensors for the mapped entities."""
    dev_reg: dr.DeviceRegistry = dr.async_get(hass)
    entities: list[AccessCodeSensor] = []
    for coordinator in config_entry.runtime_data.values():
        device: DeviceEntry = dev_reg.async_get_device(
            identifiers={(YALE_BLE_DOMAIN, coordinator.serial_number)}
        )
        if device is None:
            if not (
                device := dev_reg.async_get_device(
                    identifiers={
                        (
                            AUGUST_DOMAIN,
                            coordinator.august_lock_id,
                        )
                    }
                )
            ):
                continue
        entities.append(AccessCodeSensor(hass, coordinator, device))

    if entities:
        async_add_entities(entities)


class AccessCodeSensor(CoordinatorEntity[AccessCodeCoordinator], SensorEntity):
    """Representation of an August Access Lock Codes Sensor."""

    _listener_handle_unload: Callable | None = None

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: AccessCodeCoordinator,
        august_device: DeviceEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator=coordinator)
        self._attr_has_entity_name = True
        self.should_poll = False
        self._attr_unique_id = f"august_access_{self.coordinator.seam_id}"
        self._attr_icon = "mdi:numeric"
        identifiers: set[tuple[str, str]] = august_device.identifiers.copy()
        identifiers.add((DOMAIN, self.coordinator.seam_id))
        self._attr_device_info = {"identifiers": identifiers}
        self._attr_translation_key = "access_codes"
        self._attr_state_class = SensorStateClass.TOTAL

    @property
    def native_value(self) -> int | None:  # noqa: D102
        return len(self.coordinator.data.managed_access_codes) + len(
            self.coordinator.data.unmanaged_access_codes
        )

    @property
    def extra_state_attributes(self):  # noqa: D102
        return self.coordinator.data.todict()
