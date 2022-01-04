import typing

class EnumMeta(type):
    def _find_value_path(self, value: typing.Any) -> str | None:
        _path = None
        for attrName in self._get_enum_values():
            attrValue = getattr(self, attrName)
            if type(attrValue) == EnumMeta:
                _temp = attrValue._find_value_path(value)
                if _temp == None: continue
                else: 
                    _path = f"{attrValue.__name__}_" + _temp
                    break
            elif attrValue == value:
                return str(attrName)
        return _path
    def _get_enum_values(self) -> list[str]:
        return [_attrName for _attrName in dir(self) if not _attrName.startswith('_')]
    def __setattr__(self, name: str, value: typing.Any) -> None: return
    def __contains__(self, value: typing.Any) -> bool:
        for attrName in self._get_enum_values():
            attrValue = getattr(self, attrName)
            if type(attrValue) == EnumMeta and value in attrValue:
                return True
            elif attrValue == value:
                return True
        return False
    def __iter__(self):
        for attrName in self._get_enum_values():
            yield getattr(self, attrName)
class Enum(metaclass=EnumMeta):
    def __new__(cls, *args, **kwargs): return cls

class Event(Enum):
    class Message(Enum):
        New = "message_new"
        Reply = "message_reply"
        Edit = "message_edit"
        Allow = "message_allow"
        Deny = "message_deny"
        TypingStateChange = "message_typing_state"
    class CallbackButton(Enum):
        Press = "message_event"
    class Photo(Enum):
        New = "photo_new"
        class Comment(Enum):
            New = "photo_comment_new"
            Edit = "photo_comment_edit"
            Delete = "photo_comment_delete"
            Restore = "photo_comment_restore"
    class Audio(Enum):
        New = "audio_new"
    class Video(Enum):
        New = "video_new"
        class Comment(Enum):
            New = "video_comment_new"
            Edit = "video_comment_edit"
            Delete = "video_comment_delete"
            Restore = "video_comment_restore"
    class Wall(Enum):
        class Post(Enum):
            New = "wall_post_new"
            Repost = "wall_repost"
            class Comment(Enum):
                New = "wall_reply_new"
                Edit = "wall_reply_edit"
                Delete = "wall_reply_delete"
                Restore = "wall_reply_restore"
        class Like(Enum):
            Add = "like_add"
            Remove = "like_remove"
    class BoardPost(Enum):
        New = "board_post_new"
        Edit = "board_post_edit"
        Delete = "board_post_delete"
        Restore = "board_post_restore"
    class Market(Enum):
        class Order(Enum):
            New = "market_order_new"
            Edit = "market_order_edit"
        class Comment(Enum):
            New = "market_comment_new"
            Edit = "market_comment_edit"
            Delete = "market_comment_delete"
            Restore = "market_comment_restore"
    class Follower(Enum):
        Join = "group_join"
        Leave = "group_leave"
        Ban = "user_block"
        Unban = "user_unblock"
    class Poll(Enum):
        NewVote = "poll_vote_new"
    class Group(Enum):
        SettingsChange = "group_change_settings"
        OfficersListEdit = "group_officers_edit"
        PhotoChange = "group_change_photo"
    class VKPay(Enum):
        Transaction = "vkpay_transaction"
    class VKMiniApps(Enum):
        Event = "app_payload"
    class VKDonut(Enum):
        class Subscription(Enum):
            New = "donut_subscription_create"
            Prolong = "donut_subscription_prolonged"
            Expire = "donut_subscription_expired"
            Cancel = "donut_subscription_cancelled"
            PriceChange = "donut_subscription_price_changed"
        class MoneyWithdraw(Enum):
            Successful = "donut_money_withdraw"
            Error = "donut_money_withdraw_error"
            
class UserState(Enum):
    Idle = 0 # Not registred
    InMenu = 1
    WaitForNickname = 2