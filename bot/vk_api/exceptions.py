class InvalidVkApiResponse(Exception):
	def __init__(self, response) -> None:
		self.response = response
	def __str__(self) -> str:
		return "Invalid vk api response. Response: " + str(self.response)

class LongPollDisabled(Exception):
	def __init__(self, about: str = "LongPoll is disabled. Enable it in group settings"):
		super().__init__(about)