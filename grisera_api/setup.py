from channel.channel_service import ChannelService
from channel.channel_model import ChannelIn, Type
from modality.modality_service import ModalityService
from modality.modality_model import ModalityIn, Modality
from live_activity.live_activity_service import LiveActivityService
from live_activity.live_activity_model import LiveActivityIn, LiveActivity
import os
from time import sleep


class SetupNodes:
    """
    Class to init nodes in graph database
    """

    def set_channels(self):
        """
        Initialize values of channels
        """
        channel_service = ChannelService()
        if not os.path.exists("lock_channels"):
            open("lock_channels", "w").write("Busy")
            sleep(30)
            created_types = [channel.type for channel in channel_service.get_channels().channels]
            [channel_service.save_channel(ChannelIn(type=channel_type.value))
             for channel_type in Type
             if channel_type.value not in created_types]
            os.remove("lock_channels")

    def set_modalities(self):
        """
        Initialize values of modalities
        """
        modality_service = ModalityService()
        if not os.path.exists("lock_modalities"):
            open("lock_modalities", "w").write("Busy")
            sleep(30)
            created_modalities = [modality.modality for modality in modality_service.get_modalities().modalities]
            [modality_service.save_modality(ModalityIn(modality=modality_modality.value))
             for modality_modality in Modality
             if modality_modality.value not in created_modalities]
            os.remove("lock_modalities")

    def set_live_activities(self):
        """
        Initialize values of live activities
        """
        live_activity_service = LiveActivityService()
        if not os.path.exists("lock_live_activities"):
            open("lock_live_activities", "w").write("Busy")
            sleep(30)
            created_types = [live_activity.live_activity for live_activity in
                             live_activity_service.get_live_activities().live_activities]

            [live_activity_service.save_live_activity(LiveActivityIn(live_activity=live_activity_live_activity.value))
             for live_activity_live_activity in LiveActivity
             if live_activity_live_activity.value not in created_types]
            os.remove("lock_live_activities")