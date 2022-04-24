"""Elro Connects K1 device communication."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from elro.api import K1
from elro.command import GET_ALL_EQUIPMENT_STATUS, GET_DEVICE_NAMES
from elro.utils import update_state_data

from homeassistant.const import ATTR_NAME
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo, EntityDescription
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN


class ElroConnectsK1(K1):
    """Communicate with the Elro Connects K1 adapter."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        ipaddress: str,
        k1_id: str,
        port: int = 1025,
    ) -> None:
        """Initialize the K1 connector."""
        self._coordinator = coordinator
        self._data: dict[int, dict] = {}
        K1.__init__(self, ipaddress, k1_id, port)

    async def async_update(self) -> None:
        """Synchronize with the K1 connector."""
        await self.async_connect()
        update_status = await self.async_process_command(GET_ALL_EQUIPMENT_STATUS)
        for key in update_status.keys():
            if key not in self._data:
                self._data[key] = {}
        update_state_data(self._data, update_status)
        update_names = await self.async_process_command(GET_DEVICE_NAMES)
        update_state_data(self._data, update_names)

    @property
    def data(self) -> dict[int, dict]:
        """Return the synced state."""
        return self._data

    @property
    def coordinator(self) -> DataUpdateCoordinator:
        """Return the data update coordinator."""
        return self._coordinator


class ElroConnectsEntity(CoordinatorEntity):
    """Defines a base entity for Elro Connects devices."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        connector_id: str,
        device_id: int,
        attributes: list,
        description: EntityDescription,
    ) -> None:
        """Initialize the Elro connects entity."""
        super().__init__(coordinator)

        self.data: dict = coordinator.data[device_id]

        self._attributes = attributes
        self._connector_id = connector_id
        self._device_id = device_id
        self._attr_device_class = description.device_class
        self._attr_icon = description.icon
        self._attr_unique_id = f"{connector_id}-{device_id}"
        self._description = description

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return state attributes."""
        if not self.data:
            return None
        return {key: val for key, val in self.data.items() if key in self._attributes}

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return (
            self.data[ATTR_NAME] if ATTR_NAME in self.data else self._description.name
        )

    @callback
    def _handle_coordinator_update(self):
        """Fetch state from the device."""
        self.data = self.coordinator.data[self._device_id]
        self.async_write_ha_state()

    @property
    def device_info(self) -> DeviceInfo:
        """Return info for device registry."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._connector_id)},
            manufacturer="Elro",
            model="K1 (SF40GA)",
            name="Elro Connects K1 connector",
        )
